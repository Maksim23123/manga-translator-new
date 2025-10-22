from __future__ import annotations

from typing import Iterable, Optional

from app.application.doc_units.dto import (
    CreateHierarchyFolderRequest,
    DeleteHierarchyNodesRequest,
    MoveHierarchyNodesRequest,
    RenameHierarchyNodeRequest,
    SelectHierarchyNodeRequest,
)
from app.application.doc_units.use_cases.hierarchy import (
    CreateHierarchyFolder,
    DeleteHierarchyNodes,
    LoadHierarchy,
    MoveHierarchyNodes,
    RenameHierarchyNode,
    SelectHierarchyNode,
)


class HierarchyController:
    def __init__(
        self,
        load_use_case: LoadHierarchy,
        create_folder_use_case: CreateHierarchyFolder,
        rename_use_case: RenameHierarchyNode,
        delete_use_case: DeleteHierarchyNodes,
        move_use_case: MoveHierarchyNodes,
        select_use_case: SelectHierarchyNode,
    ) -> None:
        self._load_use_case = load_use_case
        self._create_folder_use_case = create_folder_use_case
        self._rename_use_case = rename_use_case
        self._delete_use_case = delete_use_case
        self._move_use_case = move_use_case
        self._select_use_case = select_use_case

    def load_hierarchy(self):
        return self._load_use_case.execute()

    def create_folder(self, anchor_node_id: Optional[str], placement: str, name: str):
        return self._create_folder_use_case.execute(
            CreateHierarchyFolderRequest(
                anchor_node_id=anchor_node_id,
                placement=placement,  # "child" or "sibling"
                name=name,
            )
        )

    def rename_node(self, node_id: str, new_name: str):
        return self._rename_use_case.execute(
            RenameHierarchyNodeRequest(node_id=node_id, new_name=new_name)
        )

    def delete_nodes(self, node_ids: Iterable[str]):
        self._delete_use_case.execute(
            DeleteHierarchyNodesRequest(node_ids=list(dict.fromkeys(node_ids)))
        )

    def move_nodes(
        self,
        node_ids: Iterable[str],
        target_parent_id: str,
        insert_index: int,
        *,
        as_copy: bool = False,
    ):
        self._move_use_case.execute(
            MoveHierarchyNodesRequest(
                node_ids=list(dict.fromkeys(node_ids)),
                target_parent_id=target_parent_id,
                insert_index=insert_index,
                as_copy=as_copy,
            )
        )

    def select_node(self, primary_node_id: Optional[str], selected_node_ids: Iterable[str]):
        self._select_use_case.execute(
            SelectHierarchyNodeRequest(
                primary_node_id=primary_node_id,
                selected_node_ids=list(dict.fromkeys(selected_node_ids)),
            )
        )
