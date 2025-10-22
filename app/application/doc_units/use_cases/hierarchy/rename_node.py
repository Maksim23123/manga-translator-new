from __future__ import annotations

from app.application.doc_units.dto import RenameHierarchyNodeRequest
from app.application.doc_units.events import (
    HierarchyUpdated,
    ProjectDirtyStateChanged,
)
from app.application.doc_units.ports import ActiveDocUnitStore, DocUnitHierarchyRepository
from app.domain.doc_units.services import collect_node_map, rename_node


class RenameHierarchyNode:
    def __init__(
        self,
        repository: DocUnitHierarchyRepository,
        active_store: ActiveDocUnitStore,
        events,
    ) -> None:
        self._repository = repository
        self._active_store = active_store
        self._events = events

    def execute(self, request: RenameHierarchyNodeRequest):
        unit_id = self._active_store.get()
        if unit_id is None:
            raise RuntimeError("No active doc unit.")

        root = self._repository.get_hierarchy(unit_id)
        node_map = collect_node_map(root)
        if request.node_id not in node_map:
            raise KeyError(f"Hierarchy node '{request.node_id}' not found.")

        updated_root = rename_node(root, request.node_id, request.new_name)
        self._repository.save_hierarchy(unit_id, updated_root)

        self._events.publish(
            HierarchyUpdated(
                unit_id=unit_id.value,
                root=updated_root,
                changed_node_ids=[request.node_id],
            )
        )
        self._events.publish(ProjectDirtyStateChanged(True))
