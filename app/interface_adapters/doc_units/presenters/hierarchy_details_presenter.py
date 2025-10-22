from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

from app.application.doc_units.events import (
    ActiveDocUnitChanged,
    HierarchySelectionChanged,
    HierarchyUpdated,
)
from app.application.doc_units.ports import ActiveDocUnitStore, DocUnitHierarchyRepository, MediaStore
from app.domain.doc_units.entities import HierarchyNode
from app.domain.doc_units.services import find_node


@dataclass(slots=True)
class HierarchyDetailsViewModel:
    node_id: str
    name: str
    node_type: str
    children_count: Optional[int]
    image_path: Optional[str]


class HierarchyDetailsView(Protocol):
    def show_hierarchy_item(self, view_model: HierarchyDetailsViewModel) -> None: ...
    def show_no_selection(self) -> None: ...


class HierarchyDetailsPresenter:
    def __init__(
        self,
        event_bus,
        repository: DocUnitHierarchyRepository,
        active_store: ActiveDocUnitStore,
        media_store: MediaStore,
    ) -> None:
        self._event_bus = event_bus
        self._repository = repository
        self._active_store = active_store
        self._media_store = media_store
        self._view: Optional[HierarchyDetailsView] = None
        self._current_primary_id: Optional[str] = None
        self._current_selected_ids: list[str] = []

        self._event_bus.subscribe(HierarchySelectionChanged, self._handle_selection_changed)
        self._event_bus.subscribe(HierarchyUpdated, self._handle_hierarchy_updated)
        self._event_bus.subscribe(ActiveDocUnitChanged, self._handle_active_unit_changed)

    def attach_view(self, view: HierarchyDetailsView) -> None:
        self._view = view
        if self._current_primary_id:
            self._refresh_details()
        else:
            self._view.show_no_selection()

    def detach_view(self) -> None:
        self._view = None

    def _handle_selection_changed(self, event: HierarchySelectionChanged) -> None:
        self._current_primary_id = event.primary_node_id
        self._current_selected_ids = event.selected_node_ids
        if not self._view:
            return
        if not event.primary_node_id or len(event.selected_node_ids) != 1:
            self._view.show_no_selection()
            return
        self._refresh_details()

    def _handle_hierarchy_updated(self, event: HierarchyUpdated) -> None:
        if not self._view or not self._current_primary_id:
            return
        unit_id = self._active_store.get()
        if not unit_id or unit_id.value != event.unit_id:
            return
        self._refresh_details()

    def _handle_active_unit_changed(self, event: ActiveDocUnitChanged) -> None:
        self._current_primary_id = None
        self._current_selected_ids = []
        if self._view:
            self._view.show_no_selection()

    def _refresh_details(self) -> None:
        if not self._view:
            return
        if not self._current_primary_id:
            self._view.show_no_selection()
            return

        unit_id = self._active_store.get()
        if not unit_id:
            self._view.show_no_selection()
            return

        try:
            root = self._repository.get_hierarchy(unit_id)
        except Exception:
            self._view.show_no_selection()
            return

        node = find_node(root, self._current_primary_id)
        if not node:
            self._view.show_no_selection()
            return

        view_model = self._build_view_model(node)
        self._view.show_hierarchy_item(view_model)

    def _build_view_model(self, node: HierarchyNode) -> HierarchyDetailsViewModel:
        if node.node_type == HierarchyNode.FOLDER_TYPE:
            children_count = len(node.children)
            image_path: Optional[str] = None
        else:
            children_count = None
            image_path = None
            if node.pointer:
                try:
                    image_path = self._media_store.resolve_path(node.pointer)
                except Exception:
                    image_path = None
        return HierarchyDetailsViewModel(
            node_id=node.node_id,
            name=node.name,
            node_type=node.node_type,
            children_count=children_count,
            image_path=image_path,
        )
