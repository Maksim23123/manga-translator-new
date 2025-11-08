from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Protocol

from app.application.doc_units.events import (
    ActiveDocUnitChanged,
    HierarchyLoaded,
    HierarchySelectionChanged,
    HierarchyUpdated,
)
from app.application.doc_units.use_cases.hierarchy.load_hierarchy import LoadHierarchy
from app.domain.doc_units.entities import AssetPointer, HierarchyNode


@dataclass(slots=True)
class HierarchyNodeViewModel:
    node_id: str
    name: str
    node_type: str
    pointer: Optional[AssetPointer]
    settings: dict[str, Any]
    children: List["HierarchyNodeViewModel"]


class HierarchyView(Protocol):
    def display_hierarchy(self, root: HierarchyNodeViewModel, changed_node_ids: List[str]) -> None: ...
    def clear(self) -> None: ...
    def select_nodes(self, primary_node_id: Optional[str], selected_node_ids: List[str]) -> None: ...


class HierarchyPresenter:
    def __init__(self, event_bus, load_use_case: LoadHierarchy) -> None:
        self._event_bus = event_bus
        self._load_use_case = load_use_case
        self._view: Optional[HierarchyView] = None
        self._current_root: Optional[HierarchyNode] = None
        self._active_unit_id: Optional[str] = None

        self._event_bus.subscribe(ActiveDocUnitChanged, self._handle_active_unit_changed)
        self._event_bus.subscribe(HierarchyLoaded, self._handle_hierarchy_loaded)
        self._event_bus.subscribe(HierarchyUpdated, self._handle_hierarchy_updated)
        self._event_bus.subscribe(HierarchySelectionChanged, self._handle_selection_changed)

    def attach_view(self, view: HierarchyView) -> None:
        self._view = view
        if self._current_root:
            model = self._build_view_model(self._current_root)
            self._view.display_hierarchy(model, [])
        elif self._active_unit_id:
            self._trigger_load()
        else:
            self._view.clear()

    def detach_view(self) -> None:
        self._view = None

    def _handle_active_unit_changed(self, event: ActiveDocUnitChanged) -> None:
        self._active_unit_id = event.unit_id
        if not event.unit_id:
            self._current_root = None
            if self._view:
                self._view.clear()
            return
        self._trigger_load()

    def _handle_hierarchy_loaded(self, event: HierarchyLoaded) -> None:
        self._current_root = event.root
        if event.unit_id != self._active_unit_id:
            self._active_unit_id = event.unit_id
        if self._view:
            model = self._build_view_model(event.root)
            self._view.display_hierarchy(model, [])

    def _handle_hierarchy_updated(self, event: HierarchyUpdated) -> None:
        if self._active_unit_id != event.unit_id:
            # Ignore updates for inactive units
            return
        self._current_root = event.root
        if self._view:
            model = self._build_view_model(event.root)
            self._view.display_hierarchy(model, event.changed_node_ids)

    def _handle_selection_changed(self, event: HierarchySelectionChanged) -> None:
        if self._active_unit_id != event.unit_id:
            return
        if self._view:
            self._view.select_nodes(event.primary_node_id, event.selected_node_ids)

    def _trigger_load(self) -> None:
        try:
            self._load_use_case.execute()
        except (RuntimeError, KeyError):
            if self._view:
                self._view.clear()

    def _build_view_model(self, node: HierarchyNode) -> HierarchyNodeViewModel:
        return HierarchyNodeViewModel(
            node_id=node.node_id,
            name=node.name,
            node_type=node.node_type,
            pointer=node.pointer,
            settings=dict(node.settings),
            children=[self._build_view_model(child) for child in node.children],
        )
