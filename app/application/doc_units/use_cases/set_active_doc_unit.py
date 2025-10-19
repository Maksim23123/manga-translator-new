from app.application.doc_units.dto import SetActiveDocUnitRequest
from app.application.doc_units.events import ActiveDocUnitChanged
from app.application.doc_units.ports import ActiveDocUnitStore
from app.domain.doc_units.value_objects import DocUnitId


class SetActiveDocUnit:
    def __init__(self, active_store: ActiveDocUnitStore, events) -> None:
        self._active_store = active_store
        self._events = events

    def execute(self, request: SetActiveDocUnitRequest) -> None:
        unit_id = DocUnitId(request.unit_id) if request.unit_id else None
        self._active_store.set(unit_id)
        self._events.publish(ActiveDocUnitChanged(unit_id.value if unit_id else None))
