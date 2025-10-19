from app.application.doc_units.dto import RenameDocUnitRequest
from app.application.doc_units.events import (
    DocUnitListUpdated,
    ProjectDirtyStateChanged,
)
from app.application.doc_units.ports import DocUnitRepository
from app.domain.doc_units.entities import DocUnit
from app.domain.doc_units.value_objects import DocUnitId, DocUnitName


class RenameDocUnit:
    def __init__(self, repository: DocUnitRepository, events) -> None:
        self._repository = repository
        self._events = events

    def execute(self, request: RenameDocUnitRequest) -> DocUnit:
        doc_unit = self._repository.get_unit(DocUnitId(request.unit_id))
        if not doc_unit:
            raise KeyError(f"Doc unit '{request.unit_id}' not found.")

        renamed = DocUnit(
            unit_id=doc_unit.unit_id,
            name=DocUnitName(request.new_name),
            created_at=doc_unit.created_at,
            hierarchy=doc_unit.hierarchy,
            metadata=doc_unit.metadata,
        )
        self._repository.save_unit(renamed)

        units = self._repository.list_units()
        self._events.publish(
            DocUnitListUpdated([unit.unit_id.value for unit in units])
        )
        self._events.publish(ProjectDirtyStateChanged(True))

        return renamed
