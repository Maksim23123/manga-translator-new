from __future__ import annotations

from app.application.doc_units.events import HierarchyLoaded
from app.application.doc_units.ports import ActiveDocUnitStore, DocUnitHierarchyRepository


class LoadHierarchy:
    def __init__(
        self,
        repository: DocUnitHierarchyRepository,
        active_store: ActiveDocUnitStore,
        events,
    ) -> None:
        self._repository = repository
        self._active_store = active_store
        self._events = events

    def execute(self):
        unit_id = self._active_store.get()
        if unit_id is None:
            raise RuntimeError("No active doc unit.")

        hierarchy = self._repository.get_hierarchy(unit_id)
        self._events.publish(HierarchyLoaded(unit_id=unit_id.value, root=hierarchy))
        return hierarchy
