from unittest.mock import Mock

import httpx
import pytest

from cap_runtime.connectors.microsoft import BASE, MicrosoftConnector
from cap_runtime.models import CAPError


def mail(index=1):
    return {
        "id": str(index),
        "subject": "Project planning",
        "bodyPreview": "Context",
        "from": {"emailAddress": {"address": "alex@acme.example"}},
        "toRecipients": [],
        "receivedDateTime": "2026-09-15T10:00:00Z",
        "isRead": False,
        "webLink": "https://outlook.office.com/mail/id/1",
        "sensitivity": "private",
    }


def connector(handler):
    return MicrosoftConnector(
        "work",
        Mock(token=lambda: "synthetic-test-token", principal=lambda: "tenant:person"),
        httpx.MockTransport(handler),
    )


async def test_graph_read_query_and_normalization(request_data):
    def handle(request):
        assert request.method == "GET"
        assert request.url.path == "/v1.0/me/messages"
        assert "receivedDateTime ge" in request.url.params["$filter"]
        assert "isRead eq false" in request.url.params["$filter"]
        assert "ImmutableId" in request.headers["Prefer"]
        return httpx.Response(200, json={"value": [mail()]})

    request_data.unread = True
    page = await connector(handle).page(request_data)
    assert page.items[0].sensitivity == "S3"
    assert page.items[0].content_trust == "untrusted"
    assert page.items[0].source.account == "work"


@pytest.mark.parametrize(
    "status,code",
    [
        (401, "authentication_required"),
        (403, "permission_denied"),
        (404, "not_found"),
        (429, "rate_limited"),
        (503, "provider_unavailable"),
        (400, "provider_error"),
    ],
)
async def test_graph_errors_are_structured_and_sanitized(request_data, status, code):
    c = connector(
        lambda r: httpx.Response(
            status, headers={"Retry-After": "90"}, json={"error": "PRIVATE_PROVIDER_CONTENT"}
        )
    )
    with pytest.raises(CAPError) as caught:
        await c.page(request_data)
    assert caught.value.problem.code == code
    assert "PRIVATE" not in str(caught.value)


async def test_transient_retry_then_success(request_data):
    calls = []

    def handle(request):
        calls.append(request)
        return (
            httpx.Response(429, headers={"Retry-After": "0"})
            if len(calls) == 1
            else httpx.Response(200, json={"value": []})
        )

    assert (await connector(handle).page(request_data)).items == []
    assert len(calls) == 2


@pytest.mark.parametrize(
    "url",
    [
        "https://evil.example/v1.0/me/messages",
        "http://graph.microsoft.com/v1.0/me/messages",
        "https://graph.microsoft.com/v1.0/users/victim/messages",
        "https://graph.microsoft.com/v1.0/me/calendarView",
        "https://graph.microsoft.com@evil.example/v1.0/me/messages",
    ],
)
async def test_cursor_cannot_redirect_credentials(request_data, url):
    c = connector(lambda r: pytest.fail("Unexpected network request"))
    with pytest.raises(CAPError):
        await c.page(request_data, url)


async def test_nextlink_is_followed_verbatim(request_data):
    url = BASE + "/me/messages?$skiptoken=abc%2Bdef&$top=50"
    c = connector(
        lambda request: (
            httpx.Response(200, json={"value": []})
            if str(request.url) == url
            else pytest.fail("Cursor was rewritten")
        )
    )
    assert not (await c.page(request_data, url)).items


async def test_malformed_records_report_partial_coverage(request_data):
    c = connector(lambda r: httpx.Response(200, json={"value": [mail(), {"id": "bad"}]}))
    page = await c.page(request_data)
    assert len(page.items) == 1 and page.warnings


async def test_calendar_uses_calendarview_and_utc(request_data):
    def handle(request):
        assert request.url.path == "/v1.0/me/calendar/calendarView"
        assert "lastModifiedDateTime" not in request.url.params["$select"]
        assert request.url.params["startDateTime"].endswith("Z")
        assert 'outlook.timezone="UTC"' in request.headers["Prefer"]
        return httpx.Response(
            200,
            json={
                "value": [
                    {
                        "id": "event1",
                        "subject": "Meeting",
                        "start": {"dateTime": "2026-09-15T14:00:00.0000000", "timeZone": "UTC"},
                        "end": {"dateTime": "2026-09-15T15:00:00.0000000", "timeZone": "UTC"},
                        "isAllDay": False,
                        "attendees": [],
                        "organizer": {},
                    }
                ]
            },
        )

    request_data.shelf = "calendar"
    page = await connector(handle).page(request_data)
    assert page.items[0].start_time.utcoffset().total_seconds() == 0


async def test_redirects_not_followed(request_data):
    c = connector(lambda r: httpx.Response(302, headers={"Location": "https://evil.example"}))
    with pytest.raises(CAPError, match="rejected"):
        await c.page(request_data)


async def test_network_failure(request_data):
    def handle(request):
        raise httpx.ConnectError("PRIVATE_DETAIL", request=request)

    with pytest.raises(CAPError) as caught:
        await connector(handle).page(request_data)
    assert caught.value.problem.retryable and "PRIVATE" not in str(caught.value)
