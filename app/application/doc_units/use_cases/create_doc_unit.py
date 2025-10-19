from datetime import datetime, timezone

from app.application.doc_units.dto import CreateDocUnitRequest
from app.application.doc_units.events import (
    ActiveDocUnitChanged,
    DocUnitListUpdated,
    ProjectDirtyStateChanged,
)
from app.application.doc_units.ports import (
    ActiveDocUnitStore,
    DocUnitRepository,
)
from app.application.project.ports import IdGenerator
from app.domain.doc_units.entities import DocUnit, HierarchyNode
from app.domain.doc_units.value_objects import DocUnitId, DocUnitName


class CreateDocUnit:
    def __init__(
        self,
        repository: DocUnitRepository,
        active_store: ActiveDocUnitStore,
        ids: IdGenerator,
        events,
    ) -> None:
        self._repository = repository
        self._active_store = active_store
        self._ids = ids
        self._events = events

    def execute(self, request: CreateDocUnitRequest) -> DocUnit:
        unit_id = DocUnitId(self._ids.generate())
        doc_unit = DocUnit(
            unit_id=unit_id,
            name=DocUnitName(request.name),
            created_at=datetime.now(tz=timezone.utc).isoformat(),
            hierarchy=HierarchyNode(
                node_id=f"{unit_id.value}-root",
                name="root",
                node_type=HierarchyNode.FOLDER_TYPE,
            ),
            metadata={},
        )
        self._repository.save_unit(doc_unit)

        self._active_store.set(unit_id)

        units = self._repository.list_units()
        self._events.publish(
            DocUnitListUpdated([unit.unit_id.value for unit in units])
        )
        self._events.publish(ActiveDocUnitChanged(unit_id.value))
        self._events.publish(ProjectDirtyStateChanged(True))

        return doc_unit
