from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, DefaultDict, List, Optional, Type, TypeVar


@dataclass(slots=True)
class DocUnitListUpdated:
    unit_ids: List[str]


@dataclass(slots=True)
class ActiveDocUnitChanged:
    unit_id: Optional[str]


@dataclass(slots=True)
class ProjectDirtyStateChanged:
    is_dirty: bool


EventT = TypeVar("EventT")
Handler = Callable[[EventT], None]


class DocUnitEventBus:
    def __init__(self) -> None:
        self._handlers: DefaultDict[Type, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: Type[EventT], handler: Handler[EventT]) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: EventT) -> None:
        for handler in list(self._handlers.get(type(event), [])):
            handler(event)
