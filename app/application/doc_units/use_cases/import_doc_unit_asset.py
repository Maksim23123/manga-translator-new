from pathlib import Path

from app.application.doc_units.dto import ImportAssetRequest
from app.application.doc_units.events import (
    DocUnitListUpdated,
    ProjectDirtyStateChanged,
)
from app.application.doc_units.ports import DocUnitRepository, MediaStore
from app.application.project.ports import IdGenerator
from app.domain.doc_units.entities import DocUnit, HierarchyNode
from app.domain.doc_units.value_objects import DocUnitId


class ImportDocUnitAsset:
    def __init__(
        self,
        repository: DocUnitRepository,
        media_store: MediaStore,
        ids: IdGenerator,
        events,
    ) -> None:
        self._repository = repository
        self._media_store = media_store
        self._ids = ids
        self._events = events

    def execute(self, request: ImportAssetRequest) -> DocUnit:
        doc_unit = self._repository.get_unit(DocUnitId(request.unit_id))
        if not doc_unit:
            raise KeyError(f"Doc unit '{request.unit_id}' not found.")

        pointer = self._media_store.import_temp(request.source_path)

        node_id = self._ids.generate()
        name_hint = Path(pointer.path_hint or request.source_path).stem
        new_node = HierarchyNode(
            node_id=node_id,
            name=name_hint,
            node_type=HierarchyNode.IMAGE_TYPE,
            pointer=pointer,
            settings={},
        )

        new_children = list(doc_unit.hierarchy.children)
        new_children.append(new_node)

        new_root = HierarchyNode(
            node_id=doc_unit.hierarchy.node_id,
            name=doc_unit.hierarchy.name,
            node_type=doc_unit.hierarchy.node_type,
            settings=dict(doc_unit.hierarchy.settings),
            pointer=doc_unit.hierarchy.pointer,
            children=new_children,
        )

        updated = DocUnit(
            unit_id=doc_unit.unit_id,
            name=doc_unit.name,
            created_at=doc_unit.created_at,
            hierarchy=new_root,
            metadata=doc_unit.metadata,
        )

        self._repository.save_unit(updated)

        units = self._repository.list_units()
        self._events.publish(
            DocUnitListUpdated([unit.unit_id.value for unit in units])
        )
        self._events.publish(ProjectDirtyStateChanged(True))

        return updated
