import os
import tomllib
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import Field, field_validator, model_validator

from cap_runtime.models import Model


class Account(Model):
    name: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,64}$")
    provider: Literal["demo", "microsoft365"]
    client_id: str | None = None
    tenant: str = Field(default="common", pattern=r"^[a-zA-Z0-9.-]+$")
    shelves: list[Literal["comms", "calendar"]] = Field(
        default_factory=lambda: ["comms", "calendar"], min_length=1
    )

    @model_validator(mode="after")
    def requires_client_id(self):
        if self.provider == "microsoft365" and not self.client_id:
            raise ValueError("Microsoft 365 accounts need an Entra application client_id")
        return self


class Config(Model):
    timezone: str = "America/Chicago"
    state_dir: Path = Field(default_factory=lambda: Path.home() / ".local/state/cap")
    max_scan_pages: int = Field(default=5, ge=1, le=20)
    accounts: list[Account] = Field(default_factory=list, min_length=1)

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value):
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("Use an IANA timezone, such as America/Chicago") from exc
        return value

    @model_validator(mode="after")
    def unique_accounts(self):
        names = [a.name for a in self.accounts]
        if len(names) != len(set(names)):
            raise ValueError("Account names must be unique")
        self.state_dir = self.state_dir.expanduser().resolve()
        return self


def load_config(path: str | None = None) -> Config:
    path = path or os.environ.get("CAP_CONFIG")
    if not path:
        raise ValueError("Specify --config PATH or CAP_CONFIG (see examples/demo.toml)")
    with open(Path(path).expanduser(), "rb") as handle:
        return Config.model_validate(tomllib.load(handle))
