from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, DefaultDict, List, Optional, Type, TypeVar

from app.domain.doc_units.entities import HierarchyNode


@dataclass(slots=True)
class DocUnitListUpdated:
    unit_ids: List[str]


@dataclass(slots=True)
class ActiveDocUnitChanged:
    unit_id: Optional[str]


@dataclass(slots=True)
class ProjectDirtyStateChanged:
    is_dirty: bool


@dataclass(slots=True)
class HierarchyLoaded:
    unit_id: str
    root: HierarchyNode


@dataclass(slots=True)
class HierarchyUpdated:
    unit_id: str
    root: HierarchyNode
    changed_node_ids: List[str]


@dataclass(slots=True)
class HierarchySelectionChanged:
    unit_id: str
    primary_node_id: Optional[str]
    selected_node_ids: List[str]


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
