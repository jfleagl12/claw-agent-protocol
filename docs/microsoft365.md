# Microsoft 365 setup

## Register an application

1. In Microsoft Entra, create an app registration. Choose the supported account types appropriate for your organization or personal Microsoft account.
2. Copy the **Application (client) ID**. This is an identifier, not a secret.
3. Under Authentication, enable **Allow public client flows** for device-code sign-in. CAP uses MSAL's public-client device flow and does not need a client secret.
4. Add delegated Microsoft Graph permissions `User.Read`, `Mail.Read`, and `Calendars.Read`. If you configure only one shelf, you can omit the other permission. Obtain administrator consent if your tenant requires it.
5. Copy `examples/microsoft365.toml` to `config.local.toml`. Set `client_id` to the application ID. Set `tenant` to your tenant ID for work accounts, `consumers` for personal-only applications, or `common` for an app supporting both. Use a separate account alias per signed-in identity.

Registering an app does not grant mailbox access. The user must complete Microsoft sign-in and consent. Conditional Access can block device flow; if so, work with the tenant administrator. CAP does not bypass that policy.

## Authenticate and test

```bash
cap --config config.local.toml auth login --account work
cap --config config.local.toml doctor --probe
cap --config config.local.toml briefing
```

Login displays Microsoft's device-code instructions on stderr. Complete them directly at Microsoft's login site. CAP binds the account alias to the signed-in tenant and object ID and stores its MSAL cache in the OS credential store.

`doctor` without `--probe` only validates configuration. A successful probe confirms that each enabled shelf answers a read request; it does not validate every workflow. A failed or partially connected account produces a nonzero exit code and structured error.

## Credential storage

Supported backends are macOS Keychain, Windows Credential Manager, and Linux Secret Service/KWallet. There is intentionally no plaintext fallback. A headless Linux session needs an accessible, unlocked OS keyring. Configure it before connecting the account.

Start the agent under the same OS user that completed login, with access to that user's keyring. Never place access or refresh tokens in TOML, MCP config, skill files, or Git.

```bash
cap --config config.local.toml auth logout --account work
```

Logout removes the local credential record. It does not revoke the application grant in Microsoft; revoke that separately in your account/tenant if needed. Restart existing CAP servers after login/logout or configuration changes.

## Limits

Only the global `graph.microsoft.com` cloud is supported. Reads use `/me/messages` and `/me/calendar/calendarView`, so mail covers the signed-in mailbox (including folders returned by Microsoft), while calendar retrieval covers the default calendar and expanded recurring occurrences. Other/shared calendars and mailboxes are not implemented.

Messages are filtered by received time, not last-modified time. Meeting context matches exact attendee/organizer addresses across sender/to/cc metadata. Documents, attachments, task systems, aliases, and inferred company relationships are outside the first release.

Official references: [MSAL token acquisition](https://learn.microsoft.com/en-us/entra/msal/python/getting-started/acquiring-tokens), [list messages](https://learn.microsoft.com/en-us/graph/api/user-list-messages?view=graph-rest-1.0), [calendar view](https://learn.microsoft.com/en-us/graph/api/calendar-list-calendarview?view=graph-rest-1.0).
