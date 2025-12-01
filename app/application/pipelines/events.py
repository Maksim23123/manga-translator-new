from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, DefaultDict, List, Optional, Type, TypeVar

from app.domain.pipelines.graph_pointer import GraphPointer


@dataclass(slots=True)
class PipelineListUpdated:
    names: List[str]


@dataclass(slots=True)
class PipelineAdded:
    name: str


@dataclass(slots=True)
class PipelineRemoved:
    name: str


@dataclass(slots=True)
class PipelineRenamed:
    old_name: str
    new_name: str


@dataclass(slots=True)
class ActivePipelineChanged:
    name: Optional[str]


@dataclass(slots=True)
class PreviewImageChanged:
    """Emitted when the active pipeline's preview image path changes."""

    name: Optional[str]
    path: Optional[Path]


@dataclass(slots=True)
class PipelineGraphDirtyChanged:
    name: str
    is_dirty: bool


@dataclass(slots=True)
class PipelineGraphPointerUpdated:
    name: str
    pointer: GraphPointer


@dataclass(slots=True)
class PipelineGraphLoadWarning:
    """Emitted when a pipeline graph fails to load (missing/corrupt)."""

    name: str
    path: Path | None
    reason: str


EventT = TypeVar("EventT")
Handler = Callable[[EventT], None]


class PipelineEventBus:
    """Lightweight pub/sub for pipeline events."""

    def __init__(self) -> None:
        self._handlers: DefaultDict[Type, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: Type[EventT], handler: Handler[EventT]) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: EventT) -> None:
        for handler in list(self._handlers.get(type(event), [])):
            handler(event)
