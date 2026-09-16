import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_actual_stdio_handshake_and_workflows(tmp_path):
    config = tmp_path / "demo.toml"
    config.write_text(
        f'timezone = "America/Chicago"\nstate_dir = {json.dumps(str(tmp_path / "state"))}\n'
        '[[accounts]]\nname = "demo"\nprovider = "demo"\n'
    )
    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "cap_runtime.cli", "--config", str(config), "serve"],
        env=dict(os.environ),
    )
    async with stdio_client(server) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        tools = (await session.list_tools()).tools
        assert {t.name for t in tools} == {
            "cap_status",
            "cap_search",
            "cap_get",
            "cap_today_briefing",
            "cap_meeting_context",
            "cap_changes",
            "cap_ack_changes",
        }
        ack = next(t for t in tools if t.name == "cap_ack_changes")
        assert not ack.annotations.readOnlyHint
        for tool in tools:
            if tool.name != "cap_ack_changes":
                assert tool.annotations.readOnlyHint
        status = await session.call_tool("cap_status", {"probe": True})
        assert not status.isError
        assert status.structuredContent["accounts"][0]["connection"] == "connected"
        briefing = await session.call_tool("cap_today_briefing", {})
        assert not briefing.isError
        assert briefing.structuredContent["complete"]
        assert len(briefing.structuredContent["sources"]) == 2
        meeting = await session.call_tool(
            "cap_meeting_context", {"account": "demo", "event_id": "meeting-1"}
        )
        assert meeting.structuredContent["messages"]
        assert "DEMO" in meeting.structuredContent["event"]["title"]
        evidence = briefing.structuredContent
        request = {
            "account": "demo",
            "shelf": "comms",
            "start": evidence["start"],
            "end": evidence["end"],
        }
        changes = await session.call_tool("cap_changes", {"request": request, "workflow": "test"})
        assert changes.structuredContent["items"]
        batch = changes.structuredContent["batch_id"]
        acknowledged = await session.call_tool(
            "cap_ack_changes",
            {"account": "demo", "shelf": "comms", "workflow": "test", "batch_id": batch},
        )
        assert acknowledged.structuredContent["acknowledged"] == 1
        replay = await session.call_tool("cap_changes", {"request": request, "workflow": "test"})
        assert replay.structuredContent["items"] == []
        item = await session.call_tool(
            "cap_get", {"account": "demo", "shelf": "comms", "external_id": "message-1"}
        )
        assert item.structuredContent["item"]["source"]["external_id"] == "message-1"
        invalid_zone = await session.call_tool("cap_today_briefing", {"timezone": "bad/zone"})
        assert invalid_zone.structuredContent["error"]["code"] == "invalid_timezone"
        invalid = await session.call_tool(
            "cap_search", {"request": {"account": "demo", "shelf": "docs"}}
        )
        assert invalid.isError
