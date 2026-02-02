# CAP Query Examples

This document provides common query patterns for interacting with CAP shelves.

## Calendar Queries

### Today's Events
```
read cap://calendar?start_date=today&end_date=today
```

### This Week's Events
```
read cap://calendar?start_date=today&end_date=+7days
```

### Upcoming Events with Specific Attendee
```
read cap://calendar?start_date=today&attendee=john@example.com
```

### All-Day Events Only
```
read cap://calendar?all_day=true&start_date=today
```

### Confirmed Events (Exclude Tentative/Cancelled)
```
read cap://calendar?status=confirmed&start_date=today
```

## Task Queries

### High Priority Pending Tasks
```
read cap://tasks?status=pending&priority=high
```

### Tasks Due This Week
```
read cap://tasks?due_date_start=today&due_date_end=+7days
```

### All Tasks for Specific Project
```
read cap://tasks?project=website_redesign
```

### Blocked Tasks (Need Attention)
```
read cap://tasks?status=blocked
```

### Completed Tasks (Last 30 Days)
```
read cap://tasks?status=completed&updated_after=-30days
```

## Communication Queries

### Unread Emails from Specific Sender
```
read cap://comms?type=email&is_read=false&from=client@example.com
```

### Recent Messages (Last 24 Hours)
```
read cap://comms?timestamp_after=-24hours
```

### All Communications in a Thread
```
read cap://comms?thread_id=abc123xyz
```

### Calls Only
```
read cap://comms?type=call&timestamp_after=-7days
```

### Messages by Subject Keyword
```
read cap://comms?subject_contains=invoice
```

## Identity Queries

### All Contacts Tagged as "Client"
```
read cap://identity?tags=client
```

### People with Specific Email Domain
```
read cap://identity?email_domain=example.com
```

### Organizations Only
```
read cap://identity?type=org
```

### Contacts with Phone Numbers
```
read cap://identity?has_phone=true
```

## Document Queries

### Notes Tagged with Specific Tag
```
read cap://docs?type=note&tags=meeting-notes
```

### Files Modified Recently
```
read cap://docs?type=file&updated_after=-7days
```

### Bookmarks Only
```
read cap://docs?type=bookmark
```

### Search Documents by Title
```
read cap://docs?title_contains=proposal
```

### All Documents with URLs
```
read cap://docs?has_url=true
```

## Advanced Query Patterns

### Combining Multiple Filters
```
read cap://tasks?status=pending&priority=high,urgent&due_date_end=+3days
```

### Date Range Queries
```
read cap://calendar?start_date=2026-02-01&end_date=2026-02-28
```

### Relative Date Queries
```
read cap://comms?timestamp_after=-1week&timestamp_before=today
```

### Sorting Results
```
read cap://tasks?status=pending&sort_by=due_date&sort_order=asc
```

### Limiting Results
```
read cap://comms?type=email&limit=50&is_read=false
```

## Query Parameter Reference

### Common Parameters (All Shelves)

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `limit` | integer | Max results to return | `limit=100` |
| `offset` | integer | Skip N results | `offset=50` |
| `sort_by` | string | Field to sort by | `sort_by=created_at` |
| `sort_order` | string | `asc` or `desc` | `sort_order=desc` |
| `updated_after` | date/relative | Filter by update time | `updated_after=-7days` |
| `updated_before` | date/relative | Filter by update time | `updated_before=today` |

### Date/Time Formats

- **Absolute**: ISO8601 format (`2026-02-01`, `2026-02-01T14:30:00Z`)
- **Relative**: `today`, `tomorrow`, `yesterday`, `+Ndays`, `-Ndays`, `+Nweeks`, `-Nweeks`, `+Nmonths`, `-Nmonths`
- **Special**: `now`, `-Nhours`, `+Nhours`

### Boolean Parameters

Use `true` or `false` (lowercase):
```
is_read=true
all_day=false
has_phone=true
```

### Multi-Value Parameters

Separate multiple values with commas:
```
priority=high,urgent
tags=client,vip
status=pending,active
```

### Text Search Parameters

Use `*_contains` suffix for partial matching:
```
title_contains=report
subject_contains=meeting
name_contains=john
```

## Error Handling

### Invalid Query Parameters
If a query parameter is invalid, CAP returns an error with details:
```json
{
  "error": "invalid_parameter",
  "parameter": "priority",
  "message": "Invalid value 'super-high'. Valid values: low, medium, high, urgent"
}
```

### No Results
Empty result sets return an empty array:
```json
{
  "shelf": "tasks",
  "query": "status=pending&priority=urgent",
  "results": [],
  "count": 0
}
```

### Rate Limiting
CAP may rate-limit queries to protect source APIs. Respect `Retry-After` headers and implement exponential backoff.
