from __future__ import annotations

from typing import Optional

from app.application.doc_units.events import DocUnitEventBus, ProjectDirtyStateChanged
from app.application.project.ports import CurrentProjectStore
from app.domain.project.value_objects import ProjectData

from ..views.main_window_view import MainWindowView


class MainWindowPresenter:
    def __init__(
        self,
        project_store: CurrentProjectStore,
        event_bus: DocUnitEventBus,
        window_name_prefix: str = "Manga Translator",
    ) -> None:
        self._project_store = project_store
        self._event_bus = event_bus
        self._window_name_prefix = window_name_prefix
        self._is_dirty = False
        self.view: Optional[MainWindowView] = None

        self._event_bus.subscribe(ProjectDirtyStateChanged, self._handle_dirty_state)

    def attach_view(self, view: MainWindowView) -> None:
        self.view = view
        self._update_window_title()

    def detach_view(self) -> None:
        self.view = None

    def request_project_name(self) -> Optional[str]:
        return self.view.prompt_project_name() if self.view else None

    def request_save_location_path(self) -> Optional[str]:
        return self.request_save_as_location_path()

    def request_save_as_location_path(self) -> Optional[str]:
        return self.view.prompt_location_for_new_project() if self.view else None

    def request_load_location_path(self) -> Optional[str]:
        return self.view.prompt_existing_project_location() if self.view else None

    def refresh_window_title(self) -> None:
        self._update_window_title()

    def set_dirty_flag(self, is_dirty: bool) -> None:
        if self._is_dirty == is_dirty:
            return
        self._is_dirty = is_dirty
        self._update_window_title()

    def _handle_dirty_state(self, event: ProjectDirtyStateChanged) -> None:
        self.set_dirty_flag(event.is_dirty)

    def _update_window_title(self) -> None:
        if not self.view:
            return
        title = self._build_window_title()
        self.view.update_window_title(title)

    def _build_window_title(self) -> str:
        project = self._project_store.get_data()
        if not project:
            return self._window_name_prefix

        project_segment = self._format_project_segment(project)
        dirty_suffix = " *" if self._is_dirty else ""
        return f"{self._window_name_prefix}{project_segment}{dirty_suffix}"

    def _format_project_segment(self, project: ProjectData) -> str:
        project_name = project.name.value.strip()
        if not project_name:
            return ""
        return f" - {project_name}"
