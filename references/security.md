# CAP Security and Permissions Guide

This document outlines security best practices, sensitivity tiers, and safe data handling when working with CAP.

## Security Model

CAP's security model is built on three principles:

1. **Data stays at source**: No local database means no centralized attack surface
2. **Delegated authentication**: OAuth flows handled by trusted providers (Google, Microsoft, etc.)
3. **Least privilege access**: Agents request only the data they need, when they need it

## Sensitivity Tiers

Every CAP object includes a `sensitivity` field indicating the data classification:

| Tier | Description | Examples | Handling Requirements |
|------|-------------|----------|----------------------|
| **S1** | Public or low-sensitivity | Public calendar events, published documents | Standard handling, can be logged |
| **S2** | Internal or moderate-sensitivity | Work emails, internal notes, project tasks | Avoid logging full content, redact in summaries |
| **S3** | Confidential or high-sensitivity | Personal health info, financial data, credentials | Never log, never cache, minimize exposure |

### Handling S3 Data

When working with S3 data:

1. **Never log full content**: Log only metadata (id, timestamp, source)
2. **Never cache**: Always fetch fresh from source
3. **Minimize exposure**: Only load S3 data when absolutely necessary
4. **Redact in summaries**: Use placeholders like `[REDACTED]` or `[SENSITIVE]`
5. **Confirm before sharing**: Always ask user before including S3 data in responses

Example:
```python
if data["sensitivity"] == "S3":
    # Don't log the full object
    logger.info(f"Processing S3 object: {data['id']}")
    
    # Don't include in summaries
    summary = f"Found {len(s3_items)} sensitive items (details redacted)"
    
    # Confirm before exposing
    confirm = ask_user(f"Include sensitive data from {data['source']['system']}?")
```

## Permissions and Scopes

CAP uses capability-scoped tokens to control access:

### Read Permissions

| Scope | Access |
|-------|--------|
| `cap:read:identity` | Read contacts and organizations |
| `cap:read:comms` | Read messages and emails |
| `cap:read:calendar` | Read calendar events |
| `cap:read:docs` | Read documents and notes |
| `cap:read:tasks` | Read tasks and projects |
| `cap:read:*` | Read all shelves |

### Write Permissions

| Scope | Access |
|-------|--------|
| `cap:write:calendar` | Create/update calendar events |
| `cap:write:tasks` | Create/update tasks |
| `cap:write:docs` | Create/update documents |
| `cap:write:*` | Write to all shelves |

### Tool Permissions

| Scope | Access |
|-------|--------|
| `cap:tool:today_briefing` | Execute today briefing view |
| `cap:tool:client_pipeline` | Execute client pipeline view |
| `cap:tool:knowledge_search` | Execute knowledge search |
| `cap:tool:*` | Execute all tools |

### Checking Permissions

Before attempting an operation, check if the agent has the required permission:

```python
if not has_permission("cap:read:comms"):
    return "Error: Missing permission to read communications"
```

## Time-Bounded Grants

For sensitive operations, request time-bounded grants:

```
Request: cap:write:calendar (valid for 10 minutes)
```

After the grant expires, the agent must request a new one.

## Human-in-the-Loop Gates

For destructive or high-impact actions, always implement human-in-the-loop confirmation:

### Actions Requiring Confirmation

- Deleting any data
- Sending emails or messages
- Creating calendar events with external attendees
- Modifying tasks in shared projects
- Accessing S3 data

Example:
```python
def send_email(to, subject, body):
    # Show preview to user
    preview = f"To: {to}\nSubject: {subject}\n\n{body[:200]}..."
    
    # Request confirmation
    confirmed = ask_user(f"Send this email?\n\n{preview}")
    
    if confirmed:
        cap.comms.send(to=to, subject=subject, body=body)
    else:
        return "Email cancelled by user"
```

## Write Quarantine

For write operations, use a staging/quarantine pattern:

1. Agent writes to a staging area
2. User reviews changes
3. User approves or rejects
4. Approved changes are committed to source

This prevents accidental data corruption or unwanted modifications.

## Audit Logging

CAP maintains an append-only audit log for critical actions:

```json
{
  "timestamp": "2026-02-01T14:30:00Z",
  "agent_id": "agent-123",
  "action": "read",
  "shelf": "comms",
  "query": "from=client@example.com",
  "result_count": 15,
  "sensitivity_max": "S2"
}
```

Agents should contribute to this log by recording their actions.

## Data Provenance

Always preserve and respect the `source` field:

```json
{
  "source": {
    "system": "gmail",
    "external_id": "msg-abc123",
    "url": "https://mail.google.com/mail/u/0/#inbox/msg-abc123"
  }
}
```

This allows:
- Tracing data back to its origin
- Linking to the original source for verification
- Understanding which system's permissions apply

## Content Firewalling

Before ingesting external content (web pages, attachments, etc.) into CAP:

1. **Scan for malicious content**: Check for scripts, malware, phishing
2. **Sanitize HTML**: Strip dangerous tags and attributes
3. **Validate file types**: Ensure files match their declared MIME types
4. **Quarantine suspicious content**: Flag for user review before adding to shelves

## Schema Validation and Signing

To prevent agents from silently corrupting data:

1. **Validate against schema**: All writes must conform to the canonical schema
2. **Sign critical operations**: Use cryptographic signatures for high-impact changes
3. **Version control**: Track schema versions and migrations

Example validation:
```python
def validate_task(task_data):
    required_fields = ["id", "type", "title", "status", "priority"]
    for field in required_fields:
        if field not in task_data:
            raise ValidationError(f"Missing required field: {field}")
    
    if task_data["status"] not in ["pending", "active", "blocked", "completed", "cancelled"]:
        raise ValidationError(f"Invalid status: {task_data['status']}")
    
    return True
```

## Secure Communication

### In Transit
- All CAP communication uses TLS 1.3+
- Certificate pinning for MCP connections
- Mutual TLS (mTLS) for high-security deployments

### At Rest
- CAP doesn't store data at rest (real-time translation model)
- Temporary caches (if used) must be encrypted
- Credentials stored in secure vaults (never in plaintext)

## Secret Management

Never store secrets in CAP queries or logs:

❌ **Bad**:
```
read cap://comms?api_key=sk_live_abc123xyz
```

✅ **Good**:
```python
api_key = get_secret("gmail_api_key")
headers = {"Authorization": f"Bearer {api_key}"}
response = cap.comms.read(headers=headers)
```

Use secure secret stores:
- Environment variables (for development)
- HashiCorp Vault (for production)
- Cloud provider secret managers (AWS Secrets Manager, GCP Secret Manager)

## Rate Limiting and Abuse Prevention

CAP implements rate limiting to protect source APIs:

- **Per-agent limits**: 100 requests/minute per agent
- **Per-shelf limits**: 50 requests/minute per shelf
- **Burst allowance**: 10 requests in 1 second

When rate limited:
```json
{
  "error": "rate_limit_exceeded",
  "retry_after": 30,
  "limit": 100,
  "window": 60
}
```

Implement exponential backoff:
```python
def query_with_backoff(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            return cap.query(query)
        except RateLimitError as e:
            wait_time = e.retry_after * (2 ** attempt)
            time.sleep(wait_time)
    raise Exception("Max retries exceeded")
```

## Incident Response

If a security incident occurs:

1. **Immediately revoke tokens**: Disconnect affected agents
2. **Audit the log**: Review all actions taken by the compromised agent
3. **Notify the user**: Inform them of the incident and potential exposure
4. **Rotate credentials**: Generate new OAuth tokens for all connected services
5. **Document and learn**: Record the incident and update security procedures

## Compliance Considerations

When using CAP in regulated environments:

- **GDPR**: Respect data subject rights (access, deletion, portability)
- **HIPAA**: Ensure BAAs are in place for health data
- **SOC 2**: Maintain audit logs and access controls
- **CCPA**: Provide data disclosure and opt-out mechanisms

## Best Practices Summary

1. ✅ Always check `sensitivity` before logging or caching
2. ✅ Request minimum necessary permissions
3. ✅ Implement human-in-the-loop for destructive actions
4. ✅ Use write quarantine for modifications
5. ✅ Preserve data provenance (source fields)
6. ✅ Validate all writes against schema
7. ✅ Use secure secret management
8. ✅ Implement exponential backoff for rate limits
9. ✅ Never log S3 data in full
10. ✅ Maintain comprehensive audit logs
