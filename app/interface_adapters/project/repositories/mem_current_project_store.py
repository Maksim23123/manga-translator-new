from typing import Optional
from threading import RLock

from app.domain.project.value_objects import ProjectData
from app.application.project.ports import CurrentProjectStore


class MemCurrentProjectStore(CurrentProjectStore):
    def __init__(self):
        self._lock = RLock()
        self._project_data: Optional[ProjectData] = None

    def get_data(self) -> Optional[ProjectData]:
        with self._lock:
            return self._project_data

    def set_data(self, project_data: Optional[ProjectData]) -> None:
        with self._lock:
            self._project_data = project_data

    def clear(self):
        self.set_data(None)

    @property
    def is_set(self):
        with self._lock:
            return self._project_data is not None
