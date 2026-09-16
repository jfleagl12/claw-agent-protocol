from datetime import UTC, datetime

import pytest

from cap_runtime.config import Account, Config
from cap_runtime.connectors.base import Page
from cap_runtime.models import CAPError, Item, SearchRequest, Source
from cap_runtime.service import Service


class FakeConnector:
    def __init__(self, items=None, page_size=2, failure_at=None):
        self.items = items or []
        self.page_size = page_size
        self.failure_at = failure_at
        self.calls = []
        self.principal = "principal-one"

    async def identity(self):
        return self.principal

    async def page(self, request, continuation=None):
        self.calls.append(request)
        offset = int(continuation or 0)
        if self.failure_at is not None and offset >= self.failure_at:
            raise CAPError("provider_unavailable", "Provider is offline", True)
        items = [i for i in self.items if i.shelf == request.shelf]
        end = offset + self.page_size
        return Page(items[offset:end], str(end) if end < len(items) else None)

    async def get(self, shelf, external_id):
        for item in self.items:
            if item.shelf == shelf and item.source.external_id == external_id:
                return item
        raise CAPError("not_found", "Missing")


@pytest.fixture
def make_item():
    def make(index=1, **overrides):
        return Item(
            **{
                "id": f"microsoft365:work:comms:{index}",
                "shelf": "comms",
                "title": f"Message {index}",
                "preview": "Quarterly planning",
                "source": Source(
                    system="microsoft365",
                    account="work",
                    external_id=str(index),
                    url=f"https://outlook.office.com/mail/id/{index}",
                ),
                "timestamp": datetime(2026, 9, 15, 10, tzinfo=UTC),
                "sender": "alex@acme.example",
                "recipients": ["you@example.com"],
                "is_read": False,
                **overrides,
            }
        )

    return make


@pytest.fixture
def request_data():
    return SearchRequest(
        account="work",
        shelf="comms",
        start=datetime(2026, 9, 15, tzinfo=UTC),
        end=datetime(2026, 9, 16, tzinfo=UTC),
    )


@pytest.fixture
def setup_service(tmp_path):
    def setup(items=None, page_size=2, max_scan_pages=5, failure_at=None):
        config = Config(
            state_dir=tmp_path / "state",
            max_scan_pages=max_scan_pages,
            accounts=[Account(name="work", provider="microsoft365", client_id="test-app")],
        )
        connector = FakeConnector(items, page_size, failure_at)
        return Service(config, {"work": connector}), connector

    return setup
