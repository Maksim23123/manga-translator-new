from __future__ import annotations

from app.application.doc_units.dto import SelectHierarchyNodeRequest
from app.application.doc_units.events import HierarchySelectionChanged
from app.application.doc_units.ports import ActiveDocUnitStore, DocUnitHierarchyRepository
from app.domain.doc_units.services import collect_node_map


class SelectHierarchyNode:
    def __init__(
        self,
        repository: DocUnitHierarchyRepository,
        active_store: ActiveDocUnitStore,
        events,
    ) -> None:
        self._repository = repository
        self._active_store = active_store
        self._events = events

    def execute(self, request: SelectHierarchyNodeRequest):
        unit_id = self._active_store.get()
        if unit_id is None:
            raise RuntimeError("No active doc unit.")

        root = self._repository.get_hierarchy(unit_id)
        node_map = collect_node_map(root)

        selected_ids = list(dict.fromkeys(request.selected_node_ids))
        for node_id in selected_ids:
            if node_id not in node_map:
                raise KeyError(f"Hierarchy node '{node_id}' not found.")

        primary_node_id = request.primary_node_id
        if primary_node_id and primary_node_id not in node_map:
            raise KeyError(f"Hierarchy node '{primary_node_id}' not found.")
        if primary_node_id and primary_node_id not in selected_ids:
            selected_ids.insert(0, primary_node_id)

        self._events.publish(
            HierarchySelectionChanged(
                unit_id=unit_id.value,
                primary_node_id=primary_node_id,
                selected_node_ids=selected_ids,
            )
        )
