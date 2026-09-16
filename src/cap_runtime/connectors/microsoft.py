import asyncio
from datetime import UTC, datetime
from urllib.parse import quote, urlsplit

import httpx

from cap_runtime.auth import MicrosoftAuth
from cap_runtime.connectors.base import Page
from cap_runtime.models import CAPError, Item, SearchRequest, Shelf, Source

BASE = "https://graph.microsoft.com/v1.0"
MAIL_FIELDS = (
    "id,subject,bodyPreview,from,toRecipients,ccRecipients,receivedDateTime,"
    "isRead,webLink,lastModifiedDateTime,sensitivity"
)
EVENT_FIELDS = (
    "id,subject,bodyPreview,start,end,isAllDay,attendees,organizer,isCancelled,"
    "webLink,lastModifiedDateTime,sensitivity"
)


def utc(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def parse_time(value: str | None) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed


def address(value: dict) -> str:
    return value.get("emailAddress", {}).get("address", "")


class MicrosoftConnector:
    def __init__(self, account: str, auth: MicrosoftAuth, transport=None):
        self.account = account
        self.auth = auth
        self.transport = transport

    async def identity(self) -> str:
        return await asyncio.to_thread(self.auth.principal)

    async def _request(self, url: str, params=None) -> dict:
        parts = urlsplit(url)
        if (
            parts.scheme != "https"
            or parts.netloc != "graph.microsoft.com"
            or not (parts.path.startswith("/v1.0/me/") or parts.path == "/v1.0/me")
            or parts.fragment
        ):
            raise CAPError("invalid_provider_url", "Rejected an unexpected provider URL.")
        token = await asyncio.to_thread(self.auth.token)
        headers = {
            "Authorization": f"Bearer {token}",
            "Prefer": 'outlook.timezone="UTC", IdType="ImmutableId"',
        }
        async with httpx.AsyncClient(
            transport=self.transport, timeout=20, follow_redirects=False
        ) as client:
            for attempt in range(3):
                try:
                    response = await client.get(url, params=params, headers=headers)
                except httpx.HTTPError as exc:
                    raise CAPError(
                        "provider_unavailable", "Microsoft Graph could not be reached.", True
                    ) from exc
                if response.status_code in (429, 502, 503, 504) and attempt < 2:
                    try:
                        delay = float(response.headers.get("Retry-After", str(0.25 * 2**attempt)))
                    except ValueError:
                        delay = 60
                    if 0 <= delay <= 2:
                        await asyncio.sleep(delay)
                        continue
                break
        status = response.status_code
        if status == 401:
            raise CAPError(
                "authentication_required", "Microsoft rejected the login. Run cap auth login."
            )
        if status == 403:
            raise CAPError(
                "permission_denied", "Microsoft denied access. Check consent and account policy."
            )
        if status == 404:
            raise CAPError("not_found", "Microsoft could not find this item or mailbox.")
        if status == 429:
            raise CAPError(
                "rate_limited", "Microsoft rate limit reached. Retry this request later.", True
            )
        if status >= 500:
            raise CAPError(
                "provider_unavailable", "Microsoft Graph is temporarily unavailable.", True
            )
        if status != 200:
            raise CAPError(
                "provider_error",
                "Microsoft rejected the read request. Check the account configuration.",
            )
        try:
            result = response.json()
            if not isinstance(result, dict):
                raise ValueError("Expected object")
            return result
        except ValueError as exc:
            raise CAPError(
                "invalid_provider_response", "Microsoft returned an invalid response."
            ) from exc

    def normalize(self, raw: dict, shelf: Shelf) -> Item:
        source = Source(
            system="microsoft365",
            account=self.account,
            external_id=raw["id"],
            url=raw.get("webLink"),
        )
        common = dict(
            id=f"microsoft365:{self.account}:{shelf}:{raw['id']}",
            shelf=shelf,
            source=source,
            title=raw.get("subject") or "(No subject)",
            preview=(raw.get("bodyPreview") or "")[:1200],
            updated_at=parse_time(raw.get("lastModifiedDateTime")),
            sensitivity="S3" if raw.get("sensitivity") in ("private", "confidential") else "S2",
        )
        if shelf == "comms":
            return Item(
                **common,
                timestamp=parse_time(raw["receivedDateTime"]),
                sender=address(raw.get("from") or {}),
                recipients=[
                    address(r) for r in raw.get("toRecipients", []) + raw.get("ccRecipients", [])
                ],
                is_read=raw.get("isRead"),
            )
        # Requests explicitly ask Graph to return start/end in UTC.
        for field in ("start", "end"):
            if raw[field].get("timeZone", "UTC") not in ("UTC", "Etc/UTC"):
                raise ValueError("Provider ignored UTC timezone preference")
        return Item(
            **common,
            start_time=parse_time(raw["start"]["dateTime"]),
            end_time=parse_time(raw["end"]["dateTime"]),
            all_day=raw.get("isAllDay", False),
            attendees=list(
                dict.fromkeys(
                    [address(a) for a in raw.get("attendees", [])]
                    + [address(raw.get("organizer") or {})]
                )
            ),
            cancelled=raw.get("isCancelled", False),
        )

    async def page(self, request: SearchRequest, continuation: str | None = None) -> Page:
        endpoint = "/me/calendar/calendarView" if request.shelf == "calendar" else "/me/messages"
        url = BASE + endpoint
        if continuation:
            # A cursor can never redirect the credential to another host/account/endpoint.
            if urlsplit(continuation).path != "/v1.0" + endpoint:
                raise CAPError("invalid_cursor", "Provider cursor changed the resource path.")
            data = await self._request(continuation)
        else:
            params = {"$top": "50"}
            if request.shelf == "calendar":
                params.update(
                    {
                        "startDateTime": utc(request.start),
                        "endDateTime": utc(request.end),
                        # calendarView does not support selecting lastModifiedDateTime.
                        # Keep the response small; revision hashes cover returned evidence.
                        "$select": EVENT_FIELDS.replace(",lastModifiedDateTime", ""),
                        "$orderby": "start/dateTime",
                    }
                )
            else:
                params.update(
                    {
                        "$filter": f"receivedDateTime ge {utc(request.start)} and "
                        f"receivedDateTime lt {utc(request.end)}",
                        "$orderby": "receivedDateTime desc",
                        "$select": MAIL_FIELDS,
                    }
                )
                if request.unread is not None:
                    params["$filter"] += " and isRead eq " + str(not request.unread).lower()
            data = await self._request(url, params)
        if not isinstance(data.get("value"), list):
            raise CAPError("invalid_provider_response", "Microsoft returned no collection.")
        items, warnings = [], []
        for raw in data["value"]:
            try:
                items.append(self.normalize(raw, request.shelf))
            except (ValueError, TypeError, KeyError, AttributeError):
                warnings.append("An invalid provider record was omitted; coverage is incomplete.")
        continuation = data.get("@odata.nextLink")
        if continuation is not None and not isinstance(continuation, str):
            raise CAPError("invalid_provider_response", "Microsoft returned an invalid cursor.")
        return Page(items, continuation, list(dict.fromkeys(warnings)))

    async def get(self, shelf: Shelf, external_id: str) -> Item:
        resource = "events" if shelf == "calendar" else "messages"
        data = await self._request(
            f"{BASE}/me/{resource}/{quote(external_id, safe='')}",
            {"$select": EVENT_FIELDS if shelf == "calendar" else MAIL_FIELDS},
        )
        try:
            return self.normalize(data, shelf)
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            raise CAPError(
                "invalid_provider_response", "Microsoft returned an invalid record."
            ) from exc
