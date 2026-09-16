# Claw Agent Protocol (CAP)

A working, read-only personal-data service for AI agents. CAP gives Hermes, OpenClaw, and other MCP clients a consistent way to search Outlook mail and calendar events, prepare meetings, and build daily briefings with source links.

**Version 0.2.0 is an initial runtime release.** It includes a real Microsoft Graph adapter and a synthetic demo. It does not send messages, edit calendars, or connect documents/tasks. Account login and live acceptance testing are required before relying on it with your mailbox.

## Try it in two minutes

Requires Python 3.11+ on macOS or Linux. Windows needs IANA timezone data (install `tzdata`) and its usual `.venv\Scripts` paths.

```bash
git clone https://github.com/jfleagl12/claw-agent-protocol.git
cd claw-agent-protocol
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cap --config examples/demo.toml doctor --probe
cap --config examples/demo.toml briefing
cap --config examples/demo.toml meeting --account demo --event-id meeting-1
```

Demo records are clearly labeled and relative to today's date in the configured timezone. No account or API key is needed. CLI exit codes: 0 success, 1 connection/provider failure, 2 invalid configuration/input, 3 partial evidence or more pages.

`state_dir` in the TOML file controls where private workflow metadata is stored; use a directory writable by your harness.

## What is implemented

| Tool | Result |
|---|---|
| `cap_status` | Configured accounts and enabled shelves; optional live connection probes |
| `cap_search` | Structured, bounded mail/calendar retrieval with resumable pagination |
| `cap_get` | A source-linked item and bounded preview by its source ID |
| `cap_today_briefing` | Today's events and received mail, grouped by account/source |
| `cap_meeting_context` | A selected event and recent correspondence with exact attendee addresses |
| `cap_changes` | Unacknowledged items/revisions within a requested search window |
| `cap_ack_changes` | Acknowledge successful handling in CAP's local metadata |

The harness writes the final summary from the returned evidence. CAP does not run a second LLM, invent priorities, or decide that an inferred commitment is confirmed.

## Connect your Microsoft account

See [Microsoft 365 setup](docs/microsoft365.md). Register a public client application in Microsoft Entra, configure its client ID, then sign in:

```bash
cp examples/microsoft365.toml config.local.toml
# Edit client_id, tenant, account name, timezone, and state_dir first.
cap --config config.local.toml auth login --account work
cap --config config.local.toml doctor --probe
```

Requested delegated permissions are `User.Read`, `Mail.Read`, and `Calendars.Read`; disabled shelves omit their permission. Tokens use MSAL and the OS credential store. There is no client secret and no plaintext token-file fallback. Some organizations restrict device login or require administrator consent.

## Connect an agent

CAP uses local MCP **stdio**. It binds no network port. Register the absolute path to `.venv/bin/cap` with arguments `--config`, an absolute TOML path, and `serve`.

- [Hermes and OpenClaw configuration](docs/harnesses.md)
- [Portable agent skill](SKILL.md)
- [Structured query examples](references/query_examples.md)
- [Data contract and result semantics](references/schema.md)
- [Security boundaries](references/security.md)

The skill teaches workflows; the separately installed runtime supplies the tools. Installing `SKILL.md` alone does not connect accounts.

## Reliability and scope

- Each source reports `complete`, `next_cursor`, `warnings`, and `error`. No results and a failed query are different outcomes.
- Queries require offset-aware dates and use half-open intervals. Calendar searches include events overlapping the interval. Daily workflows respect daylight saving time.
- Search matches literal text in subjects/previews and exact participant addresses. It is not full-body, attachment, semantic, or fuzzy company search.
- Cursors are opaque, expire after one hour, and are bound to the account principal and exact request. Within-page changes invalidate a cursor. Provider paging is not a transactionally consistent snapshot: retry overlapping windows and deduplicate when processing changing mailboxes.
- Results carry source IDs, source URLs when available, retrieval times, and an explicit untrusted-content marker.
- Workflow acknowledgements survive restarts. Delivery is **at least once**, not exactly once; no external delivery occurs inside CAP. The harness owns scheduling and notification delivery.
- Microsoft support currently covers the signed-in mailbox and default calendar through the global Graph endpoint. Shared mailboxes, other calendars, national clouds, documents, contacts, tasks, and Google Workspace are not yet implemented.

## Development and verification

```bash
python -m pip install -e '.[dev]'
pytest -q
ruff check src tests
ruff format --check src tests
python -m build
```

Tests exercise mocked Microsoft responses, authentication/account binding, pagination, failures, date boundaries, workflow replay, and an actual MCP stdio subprocess handshake. CI runs Python 3.11–3.13. [Acceptance checks](docs/acceptance.md) distinguish automated verification from live-account and native-harness verification.

The original scripts under `scripts/` are retained for compatibility as standalone **legacy helpers**. They use the older data format and are not used by the server. Their keyword query builder is not the runtime query engine. The previous documentation is available in Git history.

## Next increments

1. Live acceptance on Microsoft accounts and both native harnesses.
2. Additional calendar selection, provider delta feeds, and explicit state-retention controls.
3. Google Workspace and document/task adapters using the same service contract.
4. Carefully scoped writes with previews, authorization, duplicate prevention, and verified receipts.

Created by Jason Fleagle. [MIT license](LICENSE).
