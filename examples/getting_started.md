# Getting Started with CAP v2

This guide walks you through the simple process of setting up and running the CAP MCP server.

## 1. Installation

Install the CAP server from PyPI:

```bash
pip install claw-agent-protocol
```

## 2. Authentication

Next, you need to authorize CAP to access your data sources. CAP makes this easy with a built-in web UI for handling the OAuth flows.

```bash
cap-server auth
```

This command will:
1.  Start a temporary web server on your local machine.
2.  Print a URL to the console.
3.  Open that URL in your default web browser.

In the browser, you will see a simple page listing the available connectors (e.g., Google, Notion). Click the "Connect" button for each service you want to use and follow the standard OAuth prompts from that service.

Once you have connected your accounts, you can close the browser tab. The credentials will be securely stored for future use.

## 3. Running the Server

Now you can run the CAP server:

```bash
cap-server run
```

The server will start and listen for connections from MCP clients. By default, it uses STDIO for transport, which is the standard for local MCP servers.

## 4. Connecting to Your Agent

The final step is to tell your AI agent (e.g., OpenClaw) to use your new CAP server. This is typically done by adding the server to your agent's configuration file.

For example, in OpenClaw's `openclaw.json`:

```json
{
  "mcpServers": {
    "cap": {
      "command": "cap-server",
      "args": ["run"]
    }
  }
}
```

Now, restart your agent. It will automatically discover the CAP server and be able to query your data through the canonical CAP shelves and views.

## Example Query

Try asking your agent:

> "What's on my calendar for today?"

Your agent will query the `cap://calendar` resource, which will cause the CAP server to fetch the latest data from your connected calendar service, normalize it, and return it to the agent. The agent will then use this clean, structured data to answer your question.
