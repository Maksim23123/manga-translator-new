from __future__ import annotations

from app.application.doc_units.dto import MoveHierarchyNodesRequest
from app.application.doc_units.events import (
    HierarchyUpdated,
    ProjectDirtyStateChanged,
)
from app.application.doc_units.ports import ActiveDocUnitStore, DocUnitHierarchyRepository
from app.application.project.ports import IdGenerator
from app.domain.doc_units.services import collect_node_map, move_nodes


class MoveHierarchyNodes:
    def __init__(
        self,
        repository: DocUnitHierarchyRepository,
        active_store: ActiveDocUnitStore,
        ids: IdGenerator,
        events,
    ) -> None:
        self._repository = repository
        self._active_store = active_store
        self._ids = ids
        self._events = events

    def execute(self, request: MoveHierarchyNodesRequest):
        unit_id = self._active_store.get()
        if unit_id is None:
            raise RuntimeError("No active doc unit.")
        if not request.node_ids:
            return

        root = self._repository.get_hierarchy(unit_id)
        before_ids = set(collect_node_map(root).keys())

        updated_root = move_nodes(
            root,
            request.node_ids,
            request.target_parent_id,
            request.insert_index,
            copy=request.as_copy,
            id_factory=self._ids.generate if request.as_copy else None,
        )

        self._repository.save_hierarchy(unit_id, updated_root)

        if request.as_copy:
            after_ids = set(collect_node_map(updated_root).keys())
            changed_ids = list(after_ids - before_ids)
        else:
            changed_ids = list(dict.fromkeys(request.node_ids))

        self._events.publish(
            HierarchyUpdated(
                unit_id=unit_id.value,
                root=updated_root,
                changed_node_ids=changed_ids,
            )
        )
        self._events.publish(ProjectDirtyStateChanged(True))
