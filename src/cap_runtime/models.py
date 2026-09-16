"""The runtime's executable data contract; no natural-language query parsing."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

Shelf = Literal["comms", "calendar"]


def now() -> datetime:
    return datetime.now(UTC)


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SearchRequest(Model):
    account: str = Field(min_length=1, max_length=64)
    shelf: Shelf
    start: AwareDatetime
    end: AwareDatetime
    text: str = Field(default="", max_length=256, description="Literal subject/preview substring")
    participant: str | None = Field(default=None, max_length=320)
    unread: bool | None = None
    limit: int = Field(default=20, ge=1, le=100)
    cursor: str | None = Field(default=None, max_length=128)

    @model_validator(mode="after")
    def valid_range(self):
        if self.end <= self.start:
            raise ValueError("end must be after start")
        if (self.end - self.start).total_seconds() > 366 * 86400:
            raise ValueError("Search at most 366 days at a time")
        if self.shelf == "calendar" and self.unread is not None:
            raise ValueError("unread is only supported for comms")
        if self.participant is not None and (
            "@" not in self.participant or any(c.isspace() for c in self.participant)
        ):
            raise ValueError("participant must be an exact email address")
        return self


class Source(Model):
    system: Literal["demo", "microsoft365"]
    account: str
    external_id: str
    url: str | None = None


class Item(Model):
    id: str
    shelf: Shelf
    title: str
    preview: str = ""
    source: Source
    retrieved_at: AwareDatetime = Field(default_factory=now)
    updated_at: AwareDatetime | None = None
    sensitivity: Literal["S2", "S3"] = "S2"
    content_trust: Literal["untrusted"] = "untrusted"
    timestamp: AwareDatetime | None = None
    sender: str | None = None
    recipients: list[str] = Field(default_factory=list)
    is_read: bool | None = None
    start_time: AwareDatetime | None = None
    end_time: AwareDatetime | None = None
    all_day: bool = False
    attendees: list[str] = Field(default_factory=list)
    cancelled: bool = False


class Problem(Model):
    code: str
    message: str
    retryable: bool = False


class SearchResult(Model):
    account: str
    shelf: Shelf
    items: list[Item] = Field(default_factory=list)
    retrieved_at: AwareDatetime = Field(default_factory=now)
    complete: bool = False
    next_cursor: str | None = None
    scanned: int = 0
    warnings: list[str] = Field(default_factory=list)
    error: Problem | None = None


class CAPError(Exception):
    def __init__(self, code: str, message: str, retryable: bool = False):
        super().__init__(message)
        self.problem = Problem(code=code, message=message, retryable=retryable)


def matches(item: Item, request: SearchRequest) -> bool:
    if request.text.casefold() not in (item.title + " " + item.preview).casefold():
        return False
    if request.participant:
        addresses = [item.sender or "", *item.recipients, *item.attendees]
        if request.participant.casefold() not in {a.casefold() for a in addresses}:
            return False
    return request.unread is None or item.is_read is (not request.unread)
