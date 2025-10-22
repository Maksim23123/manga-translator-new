from __future__ import annotations

from app.application.doc_units.dto import CreateHierarchyFolderRequest
from app.application.doc_units.events import (
    HierarchyUpdated,
    ProjectDirtyStateChanged,
)
from app.application.doc_units.ports import ActiveDocUnitStore, DocUnitHierarchyRepository
from app.application.project.ports import IdGenerator
from app.domain.doc_units.entities import HierarchyNode
from app.domain.doc_units.services import (
    collect_node_map,
    collect_parent_map,
    create_folder_node,
    insert_nodes,
)


class CreateHierarchyFolder:
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

    def execute(self, request: CreateHierarchyFolderRequest) -> HierarchyNode:
        unit_id = self._active_store.get()
        if unit_id is None:
            raise RuntimeError("No active doc unit.")

        root = self._repository.get_hierarchy(unit_id)
        node_map = collect_node_map(root)
        anchor = node_map.get(request.anchor_node_id) if request.anchor_node_id else None

        if request.anchor_node_id and anchor is None:
            raise KeyError(f"Anchor node '{request.anchor_node_id}' not found.")

        parent_id: str
        insert_index: int

        if anchor and request.placement == "child":
            if anchor.node_type != HierarchyNode.FOLDER_TYPE:
                raise ValueError("Cannot create folder inside non-folder node.")
            parent_id = anchor.node_id
            insert_index = len(anchor.children)
        else:
            parents, indices = collect_parent_map(root)
            if anchor is None:
                parent_id = root.node_id
                insert_index = len(root.children)
            else:
                parent = parents.get(anchor.node_id)
                parent_id = parent.node_id if parent else root.node_id
                insert_index = indices.get(anchor.node_id, len(parent.children if parent else root.children))

        new_folder_id = self._ids.generate()
        new_folder = create_folder_node(new_folder_id, request.name)

        updated_root = insert_nodes(root, parent_id, insert_index, [new_folder])
        self._repository.save_hierarchy(unit_id, updated_root)

        self._events.publish(
            HierarchyUpdated(
                unit_id=unit_id.value,
                root=updated_root,
                changed_node_ids=[new_folder_id],
            )
        )
        self._events.publish(ProjectDirtyStateChanged(True))
        return new_folder
