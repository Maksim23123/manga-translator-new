from __future__ import annotations

from app.application.doc_units.dto import DeleteHierarchyNodesRequest
from app.application.doc_units.events import (
    HierarchyUpdated,
    ProjectDirtyStateChanged,
)
from app.application.doc_units.ports import ActiveDocUnitStore, DocUnitHierarchyRepository
from app.domain.doc_units.services import delete_nodes


class DeleteHierarchyNodes:
    def __init__(
        self,
        repository: DocUnitHierarchyRepository,
        active_store: ActiveDocUnitStore,
        events,
    ) -> None:
        self._repository = repository
        self._active_store = active_store
        self._events = events

    def execute(self, request: DeleteHierarchyNodesRequest):
        unit_id = self._active_store.get()
        if unit_id is None:
            raise RuntimeError("No active doc unit.")

        if not request.node_ids:
            return

        root = self._repository.get_hierarchy(unit_id)
        updated_root = delete_nodes(root, request.node_ids)
        self._repository.save_hierarchy(unit_id, updated_root)

        self._events.publish(
            HierarchyUpdated(
                unit_id=unit_id.value,
                root=updated_root,
                changed_node_ids=request.node_ids,
            )
        )
        self._events.publish(ProjectDirtyStateChanged(True))
