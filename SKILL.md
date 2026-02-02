---
name: claw-agent-protocol
description: Interact with the Claw Agent Protocol (CAP), a lightweight MCP server providing canonical, real-time access to personal data for AI agents. Use when working with user personal data across Gmail, Calendar, Notion, Slack, tasks, contacts, or any CAP-connected data source. Enables structured querying, data organization, and task-oriented views of user information.
---

# Claw Agent Protocol (CAP) Skill

This skill enables any AI agent to interact with a user's personal data through the Claw Agent Protocol (CAP), a lightweight MCP server that provides a canonical, real-time view of personal data from various sources.

## Core Concepts

**CAP solves the data chaos problem**: Instead of dealing with dozens of different APIs and data formats, CAP provides a single, consistent interface to all of a user's personal data.

- **Real-Time Translation Layer**: CAP fetches data on-demand from connected accounts (Gmail, Google Calendar, Notion, Slack, etc.) without storing it locally. Data stays at the source, queries are on-demand, security is delegated to OAuth providers.
- **MCP-Native**: CAP is a Model Context Protocol (MCP) server, making it compatible with any MCP-enabled client (OpenClaw, Claude Desktop, etc.).
- **Canonical Schema**: CAP exposes data through a consistent, canonical schema regardless of the original source. This eliminates integration complexity and improves agent reliability.

## Key Constructs

CAP organizes data into two primary constructs:

1. **Resources (Shelves)**: Raw, normalized data accessible via canonical URIs. These represent the fundamental categories of a user's digital life.
2. **Tools (Views)**: High-level, task-oriented functions that combine data from multiple shelves to provide refined, actionable perspectives.

## Available Shelves

| Shelf | Resource URI | Description |
|-------|--------------|-------------|
| Identity | `cap://identity` | People, orgs, contacts |
| Comms | `cap://comms` | Messages, emails, threads |
| Calendar | `cap://calendar` | Events, availability |
| Docs | `cap://docs` | Notes, files, snippets |
| Tasks | `cap://tasks` | Tasks, projects, milestones |

## Available Views

| View | Tool Name | Description |
|------|-----------|-------------|
| Today Briefing | `today_briefing` | Calendar, tasks, comms for today |
| Client Pipeline | `client_pipeline` | Contacts, comms, tasks by client |
| Knowledge Search | `knowledge_search` | Search all docs and notes |

## Usage Patterns

### Querying Shelves

Query shelves using `read` operations on resource URIs with optional filters:

```
read cap://calendar?start_date=today
read cap://tasks?status=pending&priority=high
read cap://comms?from=client@example.com&unread=true
```

### Executing Views

Call tools to execute pre-compiled views:

```
tools.today_briefing()
tools.client_pipeline(client_name="Acme Corp")
tools.knowledge_search(query="project requirements")
```

## Reference Documentation

For detailed information, consult these reference files:

- **Schema Reference**: `file.read('/home/ubuntu/skills/claw-agent-protocol/references/schema.md')` - Complete schema definitions for all shelves
- **Query Examples**: `file.read('/home/ubuntu/skills/claw-agent-protocol/references/query_examples.md')` - Common query patterns and filters
- **Security Guide**: `file.read('/home/ubuntu/skills/claw-agent-protocol/references/security.md')` - Permissions, sensitivity tiers, and safe data handling
- **Use Cases**: `file.read('/home/ubuntu/skills/claw-agent-protocol/references/use_cases.md')` - 30 common scenarios for CAP usage

## Utility Scripts

Use these scripts for common CAP operations:

- **generate_briefing.py**: Format CAP data into readable daily briefings
  ```bash
  python /home/ubuntu/skills/claw-agent-protocol/scripts/generate_briefing.py '<json_data>'
  ```

- **validate_cap_data.py**: Validate CAP data against schema requirements
  ```bash
  python /home/ubuntu/skills/claw-agent-protocol/scripts/validate_cap_data.py '<json_data>'
  ```

- **export_cap_data.py**: Export CAP data to various formats (CSV, JSON, Markdown)
  ```bash
  python /home/ubuntu/skills/claw-agent-protocol/scripts/export_cap_data.py --format csv --shelf calendar --output events.csv
  ```

- **build_query.py**: Generate CAP query strings from natural language
  ```bash
  python /home/ubuntu/skills/claw-agent-protocol/scripts/build_query.py "show me high priority tasks due this week"
  ```

## Best Practices

1. **Always check provenance**: Use the `source` field to understand where data originated and link back to the original source.
2. **Respect sensitivity tiers**: Handle S1 (public), S2 (internal), and S3 (sensitive) data appropriately.
3. **Use confidence scores**: When `confidence` is below 0.8, verify data with the user before taking action.
4. **Prefer views over raw queries**: Use pre-compiled views (tools) when available—they're optimized and tested.
5. **Cache judiciously**: CAP data is real-time, but you can cache results briefly for performance. Never cache beyond the current session.
