# Hermes and OpenClaw integration

Install the runtime from the repository README. Resolve absolute paths to the `cap` executable and a demo/live TOML configuration. Examples below use `/absolute/path/to/claw-agent-protocol`; replace it with your actual checkout.

The executable must run in the harness's environment. A remote/containerized harness needs its own installation, writable state directory, and Microsoft login/keyring. Your desktop path and credentials are not automatically available there.

## Hermes

Merge this entry into `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  cap:
    command: /absolute/path/to/claw-agent-protocol/.venv/bin/cap
    args:
      - --config
      - /absolute/path/to/claw-agent-protocol/examples/demo.toml
      - serve
    timeout: 180
```

Restart Hermes and ask it to call `cap_status` with `probe=true`, then prepare today's briefing. Do not enable parallel tool calls initially; ordinary sequential calls simplify account-login and acknowledgement behavior.

Optionally install the skill by copying the repository's `SKILL.md` into `~/.hermes/skills/claw-agent-protocol/SKILL.md`. The skill is self-contained; it does not need hardcoded script paths. Installing it does not register the MCP server.

Current official references: [MCP configuration](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp), [skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills).

## OpenClaw

Merge the following into your OpenClaw configuration, preserving existing settings:

```json
{
  "mcp": {
    "servers": {
      "cap": {
        "command": "/absolute/path/to/claw-agent-protocol/.venv/bin/cap",
        "args": ["--config", "/absolute/path/to/claw-agent-protocol/examples/demo.toml", "serve"],
        "transport": "stdio",
        "enabled": true,
        "requestTimeoutMs": 180000
      }
    }
  }
}
```

With a current OpenClaw version, check the connection:

```bash
openclaw mcp doctor cap --probe
```

Optionally copy `SKILL.md` to `~/.openclaw/skills/claw-agent-protocol/SKILL.md`, or your agent's workspace skills directory. Start a new session so the skill is discovered. Existing OpenClaw tool policies still apply; the acknowledgement tool mutates local metadata and is annotated accordingly.

Official references: [MCP configuration](https://docs.openclaw.ai/tools/mcp), [skills](https://docs.openclaw.ai/tools/skills).

## Acceptance prompts

1. “Use CAP to check which accounts and data sources are available.”
2. “Give me today's briefing using CAP. Cite the sources and identify missing coverage.”
3. “Find today's Acme project review, then prepare me for that specific meeting using CAP.”
4. “Use the CAP workflow name `daily-followups` to inspect new items in the last seven days. Acknowledge the batch after producing the summary here.”

Demo output must explicitly say it is synthetic. After changing the config to a live account, authenticate that account and repeat the probes/prompts.

## Compatibility status

Configuration examples were checked against official documentation. Automated tests launch the actual CAP server and verify MCP discovery and tool calls with the official Python MCP client. Native Hermes/OpenClaw sessions and live Microsoft accounts must be verified on the target machine; the test suite does not claim to exercise those installed applications.

The runtime pins MCP SDK v1 (`>=1.30,<2`) intentionally. A major SDK upgrade should include protocol/serialization regression tests before changing that bound.
