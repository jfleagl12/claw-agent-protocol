# CAP 0.2 security boundaries

## Enforced in code

- Provider operations are GET-only and address the signed-in user's Microsoft Graph mailbox/default calendar. CAP exposes no source write tools.
- Account names and enabled shelves are validated. Cursors and workflow acknowledgements bind to the authenticated principal and account configuration.
- Microsoft token acquisition/refresh uses MSAL. The serialized cache is stored only in an accepted OS-backed keyring. Tokens are never returned by MCP tools.
- Graph requests use HTTPS, reject foreign hosts/resource paths, and do not follow redirects. A malicious continuation URL cannot redirect the bearer token to another host.
- Provider failures return fixed messages instead of raw bodies, tokens, or message contents.
- Local state uses a private directory and SQLite file (0700/0600 on Unix). It stores opaque cursors, query/account fingerprints, item IDs, and revision hashes, not message bodies or subject lines. Cursor records can contain provider paging metadata and therefore remain private.
- The only mutating MCP tool is `cap_ack_changes`, which changes local progress metadata. There is no send, delete, or calendar-edit endpoint.

## Responsibilities outside CAP

CAP runs as a local stdio process under your OS user. It is not a multi-user authorization server, sandbox, encrypted database, or prompt-injection detector. Any trusted local process with equivalent OS access may have access to its files or keyring. Run it only for authorized users.

Once a tool returns data, the harness/model provider can see it and may record tool results in session history. Avoid broad searches in shared channels. CAP's no-content-cache policy does not control the harness's logs or memory.

Retrieved content is explicitly marked untrusted. The skill tells agents to treat it as evidence, never authority. This instruction reduces mistakes but cannot guarantee that every model resists prompt injection. Source read-only enforcement limits what CAP itself can do; unrelated tools in the harness still need their own controls.

Sensitivity labels map provider flags; they do not reliably detect every secret or regulated record. CAP does not automatically redact all sensitive data. Minimize requested information and choose an appropriate destination.

There is no background scheduler or external notification sender in CAP. Harness scheduling and delivery require their own authorization. Acknowledgement is at least once: a crash between delivery and acknowledgement can cause a duplicate. Use downstream idempotency where available.

## Retention and account changes

Expired cursor/batch tokens are pruned when a new token is issued. Seen-item revision hashes remain until the private state directory is removed. Stop CAP before removing its state; the next run reinitializes it and previously handled records may replay. Logout removes the local keyring entry, not the upstream Microsoft grant. Restart CAP after login/logout.

Do not commit real configuration, credentials, live exports, or state. `config.local.toml`, `.env*`, SQLite state, and virtual environments are ignored by Git. Example configuration contains placeholders only.
