from dataclasses import dataclass
from typing import Literal, Optional


@dataclass(slots=True)
class CreateDocUnitRequest:
    name: str


@dataclass(slots=True)
class RenameDocUnitRequest:
    unit_id: str
    new_name: str


@dataclass(slots=True)
class DeleteDocUnitRequest:
    unit_id: str


@dataclass(slots=True)
class SetActiveDocUnitRequest:
    unit_id: Optional[str]


@dataclass(slots=True)
class ImportAssetRequest:
    unit_id: str
    source_path: str


@dataclass(slots=True)
class CreateHierarchyFolderRequest:
    anchor_node_id: Optional[str]
    placement: Literal["child", "sibling"]
    name: str


@dataclass(slots=True)
class RenameHierarchyNodeRequest:
    node_id: str
    new_name: str


@dataclass(slots=True)
class DeleteHierarchyNodesRequest:
    node_ids: list[str]


@dataclass(slots=True)
class MoveHierarchyNodesRequest:
    node_ids: list[str]
    target_parent_id: str
    insert_index: int
    as_copy: bool = False


@dataclass(slots=True)
class SelectHierarchyNodeRequest:
    primary_node_id: Optional[str]
    selected_node_ids: list[str]
