from threading import RLock
from typing import Optional

from app.application.doc_units.ports import ActiveDocUnitStore
from app.domain.doc_units.value_objects import DocUnitId


class MemActiveDocUnitStore(ActiveDocUnitStore):
    def __init__(self) -> None:
        self._lock = RLock()
        self._active_unit: Optional[DocUnitId] = None

    def get(self) -> Optional[DocUnitId]:
        with self._lock:
            return self._active_unit

    def set(self, unit_id: Optional[DocUnitId]) -> None:
        with self._lock:
            self._active_unit = unit_id
