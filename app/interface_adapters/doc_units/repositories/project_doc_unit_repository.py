from __future__ import annotations

from typing import Optional

from app.application.doc_units.ports import (
    DocUnitHierarchyRepository,
    DocUnitRepository,
)
from app.application.project.ports import CurrentProjectStore
from app.domain.doc_units.entities import DocUnit, HierarchyNode
from app.domain.doc_units.value_objects import DocUnitId
from app.domain.project.value_objects import ProjectData


class ProjectDocUnitRepository(DocUnitRepository, DocUnitHierarchyRepository):
    def __init__(self, project_store: CurrentProjectStore) -> None:
        self._project_store = project_store

    def list_units(self) -> list[DocUnit]:
        project_data = self._require_project_data()
        return [
            DocUnit.from_dict(unit_id, data)
            for unit_id, data in project_data.doc_units.items()
        ]

    def get_unit(self, unit_id: DocUnitId) -> Optional[DocUnit]:
        project_data = self._require_project_data()
        if unit_dict := project_data.doc_units.get(unit_id.value):
            return DocUnit.from_dict(unit_id.value, unit_dict)
        return None

    def save_unit(self, doc_unit: DocUnit) -> None:
        project_data = self._require_project_data()
        project_data.doc_units[doc_unit.unit_id.value] = doc_unit.to_dict()
        self._project_store.set_data(project_data)

    def delete_unit(self, unit_id: DocUnitId) -> None:
        project_data = self._require_project_data()
        if unit_id.value in project_data.doc_units:
            del project_data.doc_units[unit_id.value]
            if project_data.last_active_doc_unit_id == unit_id.value:
                project_data.last_active_doc_unit_id = None
            self._project_store.set_data(project_data)

    def get_hierarchy(self, unit_id: DocUnitId) -> HierarchyNode:
        doc_unit = self.get_unit(unit_id)
        if not doc_unit:
            raise KeyError(f"Doc unit '{unit_id.value}' not found.")
        return doc_unit.hierarchy

    def save_hierarchy(self, unit_id: DocUnitId, hierarchy: HierarchyNode) -> None:
        doc_unit = self.get_unit(unit_id)
        if not doc_unit:
            raise KeyError(f"Doc unit '{unit_id.value}' not found.")
        updated = DocUnit(
            unit_id=doc_unit.unit_id,
            name=doc_unit.name,
            created_at=doc_unit.created_at,
            hierarchy=hierarchy,
            metadata=doc_unit.metadata,
        )
        self.save_unit(updated)

    def _require_project_data(self) -> ProjectData:
        project_data = self._project_store.get_data()
        if project_data is None:
            raise RuntimeError("No project loaded.")
        return project_data
