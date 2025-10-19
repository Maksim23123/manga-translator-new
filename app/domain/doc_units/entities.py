from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .value_objects import AssetId, DocUnitId, DocUnitName


@dataclass(slots=True)
class AssetPointer:
    asset_id: AssetId
    resolver: str
    status: str
    path_hint: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "asset_id": self.asset_id.value,
            "resolver": self.resolver,
            "status": self.status,
        }
        if self.path_hint:
            data["path_hint"] = self.path_hint
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssetPointer":
        return cls(
            asset_id=AssetId(data["asset_id"]),
            resolver=data.get("resolver", "file"),
            status=data.get("status", "final"),
            path_hint=data.get("path_hint"),
        )


@dataclass(slots=True)
class HierarchyNode:
    node_id: str
    name: str
    node_type: str
    settings: Dict[str, Any] = field(default_factory=dict)
    pointer: Optional[AssetPointer] = None
    children: List["HierarchyNode"] = field(default_factory=list)

    FOLDER_TYPE = "folder"
    IMAGE_TYPE = "image"

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "id": self.node_id,
            "name": self.name,
            "type": self.node_type,
            "settings": self.settings,
        }

        if self.pointer:
            data["pointer"] = self.pointer.to_dict()

        if self.node_type == self.FOLDER_TYPE:
            data["children"] = [child.to_dict() for child in self.children]

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HierarchyNode":
        pointer_data = data.get("pointer")
        pointer = AssetPointer.from_dict(pointer_data) if pointer_data else None

        children: List["HierarchyNode"] = []
        if data.get("type") == cls.FOLDER_TYPE:
            for child in data.get("children", []):
                children.append(cls.from_dict(child))

        return cls(
            node_id=data.get("id", ""),
            name=data.get("name", ""),
            node_type=data.get("type", cls.FOLDER_TYPE),
            settings=data.get("settings", {}),
            pointer=pointer,
            children=children,
        )


@dataclass(slots=True)
class DocUnit:
    unit_id: DocUnitId
    name: DocUnitName
    created_at: Optional[str]
    hierarchy: HierarchyNode
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "name": self.name.value,
            "hierarchy": self.hierarchy.to_dict(),
            "metadata": self.metadata,
        }

        if self.created_at:
            data["created_at"] = self.created_at

        return data

    @classmethod
    def from_dict(cls, unit_id: str, data: Dict[str, Any]) -> "DocUnit":
        hierarchy_data = data.get("hierarchy") or {
            "id": f"{unit_id}-root",
            "name": "root",
            "type": HierarchyNode.FOLDER_TYPE,
            "settings": {},
            "children": [],
        }

        return cls(
            unit_id=DocUnitId(unit_id),
            name=DocUnitName(data.get("name", unit_id)),
            created_at=data.get("created_at"),
            hierarchy=HierarchyNode.from_dict(hierarchy_data),
            metadata=data.get("metadata", {}),
        )
