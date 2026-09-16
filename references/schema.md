# CAP 0.2 runtime contract

Executable schemas live in `src/cap_runtime/models.py`; `cap schema` prints the search input JSON Schema. MCP tool discovery provides each tool's complete input/output schema.

## Search request

Required: `account`, `shelf` (`comms` or `calendar`), `start`, `end`. Dates must include offsets, end must be later than start, and a request may span at most 366 days.

Optional: `text` (literal subject/preview substring), `participant` (exact email), `unread` (comms only), `limit` (1–100, default 20), and opaque `cursor`.

Mail intervals are `[start, end)` by received time. Calendar intervals select overlapping events. Filters are ANDed. Unknown fields and unsupported shelves are rejected, rather than silently ignored. Text/participant filtering is performed locally over bounded provider pages.

## Item

Every item has `id`, `shelf`, `title`, `preview`, `source`, `retrieved_at`, optional `updated_at` (not selected in calendar search), `sensitivity`, and `content_trust="untrusted"`.

`source` includes `system`, `account`, `external_id`, and a URL when the provider supplies one. Use the tuple of account, shelf, and external ID for `cap_get`; do not parse the composite ID. Microsoft's immutable-ID preference is used for Outlook requests.

Mail adds `timestamp`, `sender`, `recipients`, and `is_read`. Calendar adds `start_time`, `end_time`, `all_day`, `attendees`, and `cancelled`. Provider body previews are bounded to 1,200 characters. Complete bodies and attachments are not returned.

`S3` reflects Microsoft private/confidential flags; other data is labeled `S2`. This is not comprehensive content classification. No synthetic confidence scores or invented creation timestamps are supplied.

## Search result

- `items`: matching normalized evidence.
- `complete`: true only when the requested search is exhausted without omitted records or errors. A demo information warning does not change completeness within the synthetic dataset.
- `next_cursor`: repeat the same request with this token to continue. It expires after one hour and binds filters, limits, configured account, and authenticated principal.
- `scanned`: normalized records examined in this call, including nonmatches.
- `warnings`: omitted-record or demo information.
- `error`: null or `{code, message, retryable}`. Provider error bodies and credentials are never relayed.

An empty incomplete page may precede matches. Incomplete results without a cursor indicate a failure or omission that pagination cannot fix. Within-page data changes cause `stale_cursor`; restart and deduplicate. Provider continuation pages are live data, not a frozen snapshot.

## Workflow batches

`cap_changes` adds `workflow`, `batch_id`, and delivery semantics to a search result. Only unacknowledged item revisions are returned, scoped to account principal, shelf, and workflow. A batch expires after 24 hours. `cap_ack_changes` records its IDs/revision hashes atomically; replaying an acknowledgement produces `invalid_batch`. It never marks source mail read.

Use overlapping received-time/event windows. This mechanism cannot discover old messages changed outside the window, deleted items, or updates excluded by your filters. It is not a delta-sync API or an exactly-once notification system.

The original five-shelf design and legacy script schema are retained in Git history; only the two shelves documented here are implemented by the runtime.
