from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from cap_runtime.connectors.base import Page
from cap_runtime.models import CAPError, Item, SearchRequest, Shelf, Source, now


class DemoConnector:
    """Clearly synthetic, date-relative records; never touches real accounts."""

    def __init__(self, account: str, timezone: str):
        self.account = account
        today = now().astimezone(ZoneInfo(timezone)).date()
        start = datetime.combine(today, time(14), ZoneInfo(timezone))
        source = dict(system="demo", account=account)
        self.items = [
            Item(
                id=f"demo:{account}:calendar:meeting-1",
                shelf="calendar",
                title="DEMO: Acme project review",
                preview="Review milestones and open questions.",
                source=Source(
                    **source, external_id="meeting-1", url="https://example.com/demo/meeting-1"
                ),
                updated_at=start - timedelta(days=1),
                start_time=start,
                end_time=start + timedelta(hours=1),
                attendees=["alex@acme.example"],
            ),
            Item(
                id=f"demo:{account}:comms:message-1",
                shelf="comms",
                title="DEMO: Acme review agenda",
                preview="Please bring the revised rollout timeline. The budget needs confirmation.",
                source=Source(
                    **source, external_id="message-1", url="https://example.com/demo/message-1"
                ),
                timestamp=start - timedelta(hours=6),
                updated_at=start - timedelta(hours=6),
                sender="alex@acme.example",
                recipients=["you@example.com"],
                is_read=False,
            ),
        ]

    async def identity(self) -> str:
        return f"demo:{self.account}"

    async def page(self, request: SearchRequest, continuation: str | None = None) -> Page:
        items = []
        for item in self.items:
            if item.shelf != request.shelf:
                continue
            if item.shelf == "calendar":
                within = item.start_time < request.end and item.end_time > request.start
            else:
                within = request.start <= item.timestamp < request.end
            if within:
                items.append(item)
        offset = int(continuation or 0)
        end = offset + 50
        return Page(items[offset:end], str(end) if end < len(items) else None)

    async def get(self, shelf: Shelf, external_id: str) -> Item:
        for item in self.items:
            if item.shelf == shelf and item.source.external_id == external_id:
                return item
        raise CAPError("not_found", "Item not found in this account and shelf.")
