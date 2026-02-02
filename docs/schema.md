# CAP Schema Reference

This document defines the canonical schemas for the Claw Agent Protocol shelves. In CAP, this schema is applied **in-memory** to data fetched from external sources; it is not a database schema.

## Common Metadata

Every object returned by a CAP connector includes the following metadata fields:

| Field | Type | Description |
|---|---|---|
| `id` | string | A stable, unique identifier for the object, ideally from the source system. |
| `created_at` | ISO8601 | The timestamp when the object was created at the source. |
| `updated_at` | ISO8601 | The timestamp when the object was last modified at the source. |
| `source` | SourcePointer | An object containing provenance information. |
| `confidence` | float | A score from 0.0 to 1.0 indicating the confidence in the normalization. |
| `sensitivity` | string | The sensitivity tier of the data (S1, S2, S3). |

### SourcePointer Object

```json
{
  "system": "google_calendar",
  "external_id": "a1b2c3d4e5f6",
  "url": "https://calendar.google.com/event?eid=..."
}
```

## Shelf Schemas

### Identity (`cap://identity`)

Represents people, organizations, and their contact information.

```json
{
  "id": "string",
  "type": "person | org | role",
  "name": {
    "full": "string",
    "display": "string"
  },
  "emails": ["string"],
  "phones": ["string"],
  "tags": ["string"]
}
```

### Comms (`cap://comms`)

Represents messages, emails, and communication threads.

```json
{
  "id": "string",
  "type": "email | message | call",
  "thread_id": "string | null",
  "from": "string", // Can be an email or an identity ID
  "to": ["string"],
  "subject": "string | null",
  "body_preview": "string",
  "timestamp": "ISO8601",
  "is_read": "boolean"
}
```

### Calendar (`cap://calendar`)

Represents events and time-based commitments.

```json
{
  "id": "string",
  "type": "event | reminder | block",
  "title": "string",
  "start_time": "ISO8601",
  "end_time": "ISO8601",
  "all_day": "boolean",
  "location": "string | null",
  "attendees": [
    {
      "email": "string",
      "status": "accepted | declined | tentative | pending"
    }
  ],
  "status": "confirmed | tentative | cancelled"
}
```

### Docs (`cap://docs`)

Represents notes, files, and knowledge artifacts.

```json
{
  "id": "string",
  "type": "note | file | snippet | bookmark",
  "title": "string",
  "content_preview": "string | null",
  "url": "string | null",
  "tags": ["string"]
}
```

### Tasks (`cap://tasks`)

Represents tasks, projects, and work items.

```json
{
  "id": "string",
  "type": "task | project | milestone",
  "title": "string",
  "status": "pending | active | blocked | completed | cancelled",
  "priority": "low | medium | high | urgent",
  "due_date": "ISO8601 | null",
  "project": "string | null"
}
```
