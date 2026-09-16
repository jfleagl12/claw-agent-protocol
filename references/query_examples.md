# Structured CAP examples

These examples are MCP tool arguments, not shell commands or `cap://` resource URIs. Replace `work` with an account returned by `cap_status` and use the desired dates/timezone offsets.

## Unread mail for a local day

Tool: `cap_search`

```json
{"request":{"account":"work","shelf":"comms","start":"2026-09-15T00:00:00-05:00","end":"2026-09-16T00:00:00-05:00","unread":true,"limit":20}}
```

## Find a meeting

Tool: `cap_search`

```json
{"request":{"account":"work","shelf":"calendar","start":"2026-09-15T00:00:00-05:00","end":"2026-09-16T00:00:00-05:00","text":"Acme","limit":20}}
```

Then use `cap_meeting_context` with the returned `source.external_id` as `event_id`. If multiple events match, resolve the intended event first.

## Exact participant

Tool: `cap_search`

```json
{"request":{"account":"work","shelf":"comms","start":"2026-09-01T00:00:00-05:00","end":"2026-09-16T00:00:00-05:00","participant":"alex@acme.example","limit":20}}
```

## Daily briefing

Tool: `cap_today_briefing`

```json
{"day":"2026-09-15","timezone":"America/Chicago"}
```

## Pagination

Repeat the same search request with `cursor` set to `next_cursor`. Keep all other values, including `limit`, unchanged. Follow empty pages if they have a cursor. If the cursor expires or reports `stale_cursor`, restart from the original request and deduplicate IDs.

## Recurring processing

Call `cap_changes` with the search `request` plus `workflow="daily-followups"`. After successfully producing the intended output, call:

```json
{"account":"work","shelf":"comms","workflow":"daily-followups","batch_id":"TOKEN_FROM_CAP_CHANGES"}
```

Tool: `cap_ack_changes`. Never invent a batch ID, acknowledge before success, or assume this marks email read. Continue each search page even if its filtered/unacknowledged items are empty.

## CLI search

The CLI accepts the inner request object on stdin (no outer `request` wrapper):

```bash
cap --config config.local.toml search <<'JSON'
{"account":"work","shelf":"comms","start":"2026-09-15T00:00:00-05:00","end":"2026-09-16T00:00:00-05:00","limit":20}
JSON
```
