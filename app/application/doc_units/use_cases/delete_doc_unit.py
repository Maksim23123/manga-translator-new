from app.application.doc_units.dto import DeleteDocUnitRequest
from app.application.doc_units.events import (
    ActiveDocUnitChanged,
    DocUnitListUpdated,
    ProjectDirtyStateChanged,
)
from app.application.doc_units.ports import ActiveDocUnitStore, DocUnitRepository
from app.domain.doc_units.value_objects import DocUnitId


class DeleteDocUnit:
    def __init__(
        self,
        repository: DocUnitRepository,
        active_store: ActiveDocUnitStore,
        events,
    ) -> None:
        self._repository = repository
        self._active_store = active_store
        self._events = events

    def execute(self, request: DeleteDocUnitRequest) -> None:
        unit_id = DocUnitId(request.unit_id)
        self._repository.delete_unit(unit_id)

        active = self._active_store.get()
        if active and active.value == unit_id.value:
            self._active_store.set(None)
            self._events.publish(ActiveDocUnitChanged(None))

        units = self._repository.list_units()
        self._events.publish(
            DocUnitListUpdated([unit.unit_id.value for unit in units])
        )
        self._events.publish(ProjectDirtyStateChanged(True))
