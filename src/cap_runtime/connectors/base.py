from dataclasses import dataclass, field
from typing import Protocol

from cap_runtime.models import Item, SearchRequest, Shelf


@dataclass
class Page:
    items: list[Item]
    continuation: str | None = None
    warnings: list[str] = field(default_factory=list)


class Connector(Protocol):
    async def page(self, request: SearchRequest, continuation: str | None = None) -> Page: ...

    async def get(self, shelf: Shelf, external_id: str) -> Item: ...

    async def identity(self) -> str: ...
