import argparse
import asyncio
import json
import sys
from datetime import date

from pydantic import ValidationError

from cap_runtime.auth import MicrosoftAuth
from cap_runtime.config import load_config
from cap_runtime.models import CAPError, SearchRequest
from cap_runtime.server import create_server, respond
from cap_runtime.service import Service


def main():
    parser = argparse.ArgumentParser(
        description="CAP: read-only mail/calendar service for AI agents"
    )
    parser.add_argument("--config", help="TOML config path; defaults to CAP_CONFIG")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("serve", help="Run the MCP stdio server")
    doctor = commands.add_parser(
        "doctor", help="Check configuration; optionally test live connections"
    )
    doctor.add_argument("--probe", action="store_true")
    commands.add_parser("schema", help="Print the machine-readable search input schema")
    briefing = commands.add_parser("briefing", help="Print a daily evidence package as JSON")
    briefing.add_argument("--date", type=date.fromisoformat)
    briefing.add_argument("--timezone")
    search = commands.add_parser("search", help="Read structured search JSON from stdin")
    search.add_argument("--request", help="JSON request; prefer stdin for privacy")
    meeting = commands.add_parser("meeting", help="Prepare a meeting by source ID")
    meeting.add_argument("--account", required=True)
    meeting.add_argument("--event-id", required=True)
    auth = commands.add_parser("auth", help="Connect or disconnect a Microsoft account")
    auth.add_argument("action", choices=["login", "logout"])
    auth.add_argument("--account", required=True)
    args = parser.parse_args()
    try:
        if args.command == "schema":
            print(json.dumps(SearchRequest.model_json_schema(), indent=2))
            return
        config = load_config(args.config)
        if args.command == "auth":
            account = next((a for a in config.accounts if a.name == args.account), None)
            if account is None or account.provider != "microsoft365":
                raise ValueError("Choose a configured Microsoft 365 account")
            client = MicrosoftAuth(account)
            if args.action == "login":
                client.login(lambda message: print(message, file=sys.stderr, flush=True))
            else:
                client.logout()
            print(json.dumps({"account": account.name, "action": args.action, "ok": True}))
            return
        service = Service(config)
        if args.command == "serve":
            create_server(service).run(transport="stdio")
            return
        if args.command == "doctor":
            output = asyncio.run(respond(service.status(args.probe)))
        elif args.command == "briefing":
            output = asyncio.run(respond(service.briefing(args.date, args.timezone)))
        elif args.command == "search":
            request = SearchRequest.model_validate_json(args.request or sys.stdin.read())
            output = asyncio.run(service.search(request)).model_dump(mode="json")
        else:
            output = asyncio.run(respond(service.meeting_context(args.account, args.event_id)))
        print(json.dumps(output, indent=2))
        if output.get("error") or any(
            a["connection"] == "unavailable_or_partial" for a in output.get("accounts", [])
        ):
            raise SystemExit(1)
        if output.get("complete") is False:
            raise SystemExit(3)
    except CAPError as exc:
        print(json.dumps({"error": exc.problem.model_dump()}), file=sys.stderr)
        raise SystemExit(1) from None
    except (ValueError, OSError, ValidationError) as exc:
        # Do not echo input values or file contents into harness logs.
        print(
            json.dumps(
                {
                    "error": "invalid_configuration_or_input",
                    "type": type(exc).__name__,
                    "hint": "Check the config and request against examples and cap schema.",
                }
            ),
            file=sys.stderr,
        )
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
