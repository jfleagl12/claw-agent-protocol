# Acceptance and release checks

## Automated checks

Run `pytest -q`, `ruff check src tests`, and `ruff format --check src tests`. Build the wheel with `python -m build` and verify installation/CLI behavior from that wheel.

The suite covers structured input rejection, exact participant matching, timezone/DST boundaries, pagination without dropped page remainders, incomplete filtered pages, stale/expired/account-bound cursors, authentication errors, retry limits, foreign-host continuation rejection, malformed provider records, and durable two-phase workflow acknowledgement. A subprocess test uses the official MCP client to initialize CAP, discover tools, and execute demo workflows.

Microsoft HTTP responses and credential stores are mocked. Those tests validate our request construction and behavior, not real Microsoft consent or tenant configuration.

## Live account checks (operator)

- Authenticate a dedicated Microsoft account using the setup guide and run `doctor --probe`.
- Compare a local day's events and received mail with Outlook. Check an all-day event, a recurring occurrence, and a cancelled event if available.
- Find an actual meeting by date and title, select the right event, then compare returned correspondence and source links.
- Verify pagination on a window with more records than the result limit.
- Verify a disconnected/denied shelf is reported as unavailable, not empty.
- Run a recurring query, leave it unacknowledged, restart CAP, and verify it replays. Acknowledge, rerun, and verify it is omitted until its revision changes.

## Native harness checks (operator)

Register CAP separately in Hermes and OpenClaw using `docs/harnesses.md`. Verify discovery of all seven tools, source-cited demo briefing, meeting preparation, invalid-input recovery, and acknowledgement behavior. Confirm that model-visible errors are explained accurately. Repeat relevant checks with the live account.

No native-harness or live-account compatibility certification is implied by a successful MCP subprocess test. Record the installed harness versions and account types when completing those checks.
