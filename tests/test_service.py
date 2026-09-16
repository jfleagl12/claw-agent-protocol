from datetime import UTC, date, datetime, timedelta

import pytest
from pydantic import ValidationError

from cap_runtime.config import Account, Config
from cap_runtime.connectors.base import Page
from cap_runtime.models import CAPError, SearchRequest
from cap_runtime.service import Service


async def test_pagination_retains_remainder(setup_service, make_item, request_data):
    service, _ = setup_service([make_item(i) for i in range(7)], page_size=3)
    request = request_data.model_copy(update={"limit": 2})
    all_ids = []
    for _ in range(5):
        result = await service.search(request)
        all_ids.extend(i.id for i in result.items)
        if not result.next_cursor:
            assert result.complete
            break
        assert not result.complete
        request.cursor = result.next_cursor
    assert all_ids == [make_item(i).id for i in range(7)]


async def test_empty_filtered_page_does_not_claim_no_matches(
    setup_service, make_item, request_data
):
    service, _ = setup_service(
        [make_item(1), make_item(2, title="target")], page_size=1, max_scan_pages=1
    )
    request_data.text = "target"
    first = await service.search(request_data)
    assert first.items == [] and not first.complete and first.next_cursor
    request_data.cursor = first.next_cursor
    second = await service.search(request_data)
    assert second.complete and second.items[0].title == "target"


async def test_cursor_binds_filters_and_principal(setup_service, make_item, request_data):
    service, connector = setup_service([make_item(1), make_item(2)], max_scan_pages=1, page_size=1)
    cursor = (await service.search(request_data)).next_cursor
    changed = request_data.model_copy(update={"cursor": cursor, "text": "different"})
    assert (await service.search(changed)).error.code == "invalid_cursor"
    connector.principal = "different-user"
    request_data.cursor = cursor
    assert (await service.search(request_data)).error.code == "invalid_cursor"


async def test_partial_failure_preserves_evidence(setup_service, make_item, request_data):
    service, _ = setup_service([make_item(1), make_item(2)], page_size=1, failure_at=1)
    result = await service.search(request_data)
    assert len(result.items) == 1 and not result.complete
    assert result.error.code == "provider_unavailable"


async def test_disabled_shelf_never_calls_provider(setup_service, request_data):
    service, connector = setup_service()
    service.accounts["work"].shelves = ["calendar"]
    assert (await service.search(request_data)).error.code == "permission_denied"
    assert connector.calls == []


async def test_unknown_account_is_explicit(setup_service, request_data):
    service, _ = setup_service()
    request_data.account = "missing"
    assert (await service.search(request_data)).error.code == "unknown_account"


async def test_changes_replay_until_ack_and_survive_restart(setup_service, make_item, request_data):
    service, connector = setup_service([make_item()])
    first = await service.changes(request_data, "morning")
    second = await service.changes(request_data, "morning")
    assert first["items"] == second["items"]
    service = Service(service.config, {"work": connector})
    await service.acknowledge("work", "comms", "morning", first["batch_id"])
    assert (await service.changes(request_data, "morning"))["items"] == []
    assert (await service.changes(request_data, "another-workflow"))["items"]
    connector.items[0].preview = "A changed commitment"
    assert (await service.changes(request_data, "morning"))["items"]


async def test_batch_rejects_wrong_scope_and_repeat_ack(setup_service, make_item, request_data):
    service, connector = setup_service([make_item()])
    batch = (await service.changes(request_data, "morning"))["batch_id"]
    with pytest.raises(CAPError):
        await service.acknowledge("work", "comms", "other", batch)
    connector.principal = "other-person"
    with pytest.raises(CAPError):
        await service.acknowledge("work", "comms", "morning", batch)
    connector.principal = "principal-one"
    await service.acknowledge("work", "comms", "morning", batch)
    with pytest.raises(CAPError):
        await service.acknowledge("work", "comms", "morning", batch)


async def test_no_sensitive_content_persisted(setup_service, make_item, request_data):
    service, _ = setup_service([make_item(title="PRIVATE_TITLE", preview="PRIVATE_BODY")])
    await service.changes(request_data, "workflow")
    raw = service.state.path.read_bytes()
    assert b"PRIVATE_TITLE" not in raw and b"PRIVATE_BODY" not in raw
    assert service.state.path.stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize("day,hours", [(date(2026, 3, 8), 23), (date(2026, 11, 1), 25)])
async def test_briefing_uses_local_day_across_dst(setup_service, day, hours):
    service, _ = setup_service()
    result = await service.briefing(day, "America/Chicago")
    start = datetime.fromisoformat(result["start"])
    end = datetime.fromisoformat(result["end"])
    assert (end - start).total_seconds() / 3600 == hours


async def test_meeting_matches_exact_addresses_and_deduplicates(setup_service, make_item):
    start = datetime(2026, 9, 16, 14, tzinfo=UTC)
    event = make_item(
        99,
        shelf="calendar",
        start_time=start,
        end_time=start + timedelta(hours=1),
        attendees=["alex@acme.example", "you@example.com"],
    )
    service, _ = setup_service(
        [event, make_item(1), make_item(2, sender="notalex@acme.example", recipients=[])]
    )
    result = await service.meeting_context("work", "99")
    assert len(result["messages"]) == 1 and result["complete"]


async def test_meeting_does_not_claim_coverage_without_attendees(setup_service, make_item):
    event = make_item(99, shelf="calendar", start_time=datetime.now(UTC), attendees=[])
    service, _ = setup_service([event])
    result = await service.meeting_context("work", "99")
    assert not result["complete"] and result["warnings"]


async def test_omitted_record_warning_persists_on_final_page(
    setup_service, make_item, request_data
):
    service, connector = setup_service()

    async def page(request, continuation=None):
        return (
            Page([make_item(2)])
            if continuation
            else Page([make_item(1)], "next", ["Invalid record omitted"])
        )

    connector.page = page
    request_data.limit = 1
    first = await service.search(request_data)
    request_data.cursor = first.next_cursor
    last = await service.search(request_data)
    assert not last.complete and not last.next_cursor and last.warnings


@pytest.mark.parametrize(
    "update",
    [
        {"start": "2026-09-15T00:00:00"},
        {"end": "2026-01-01T00:00:00Z"},
        {"limit": 0},
        {"limit": 101},
        {"shelf": "docs"},
        {"unexpected": "value"},
        {"shelf": "calendar", "unread": True},
        {"participant": "Acme"},
    ],
)
def test_query_validation(request_data, update):
    with pytest.raises(ValidationError):
        SearchRequest.model_validate({**request_data.model_dump(), **update})


def test_config_rejects_duplicate_names_and_unknown_fields(tmp_path):
    a = Account(name="demo", provider="demo")
    with pytest.raises(ValidationError):
        Config(accounts=[a, a], state_dir=tmp_path)
    with pytest.raises(ValidationError):
        Config(accounts=[a], timezone="not/a/timezone")


async def test_expired_cursor(setup_service, make_item, request_data):
    service, _ = setup_service([make_item(1), make_item(2)], max_scan_pages=1, page_size=1)
    request_data.cursor = (await service.search(request_data)).next_cursor
    with service.state.connect() as db:
        db.execute("UPDATE tokens SET expires=0")
    assert (await service.search(request_data)).error.code == "invalid_cursor"


async def test_changed_page_rejects_cursor_instead_of_skipping(
    setup_service, make_item, request_data
):
    service, connector = setup_service([make_item(1), make_item(2), make_item(3)], page_size=3)
    request_data.limit = 1
    request_data.cursor = (await service.search(request_data)).next_cursor
    connector.items.insert(0, make_item(0))
    result = await service.search(request_data)
    assert not result.complete and result.error.code == "stale_cursor"


async def test_briefing_retains_healthy_source_when_other_fails(setup_service, make_item):
    service, connector = setup_service([make_item(1)])
    original = connector.page

    async def page(request, continuation=None):
        if request.shelf == "calendar":
            raise CAPError("permission_denied", "Calendar not allowed")
        return await original(request, continuation)

    connector.page = page
    result = await service.briefing(date(2026, 9, 15))
    assert not result["complete"]
    assert result["sources"][0]["items"]
    assert result["sources"][1]["error"]["code"] == "permission_denied"
