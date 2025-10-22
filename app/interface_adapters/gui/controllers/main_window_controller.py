import logging
from typing import Callable, Optional, Sequence

from app.application.project.use_cases.create_project import CreateProject
from app.application.project.use_cases.save_project import SaveProject
from app.application.project.use_cases.load_project import LoadProject
from app.application.project.dto import (
    CreateProjectRequest,
    SaveProjectRequest,
    LoadProjectRequest,
)
from app.application.project.errors import ProjectSaveLocationUndefinedError
from app.application.project.ports import ProjectSettingsStore

from ..presenters.main_window_presenter import MainWindowPresenter

log = logging.getLogger(__name__)


class MainWindowController:
    def __init__(
        self,
        presenter: MainWindowPresenter,
        create_project_use_case: CreateProject,
        save_project_use_case: SaveProject,
        load_project_use_case: LoadProject,
        project_settings_store: ProjectSettingsStore,
        project_ready_callbacks: Optional[Sequence[Callable[[], None]]] = None,
    ) -> None:
        self._presenter = presenter
        self._create_project_use_case = create_project_use_case
        self._save_project_use_case = save_project_use_case
        self._load_project_use_case = load_project_use_case
        self._project_settings_store = project_settings_store
        self._project_ready_callbacks = list(project_ready_callbacks or [])

    def on_new_project_triggered(self) -> None:
        if project_name := self._presenter.request_project_name():
            req = CreateProjectRequest(project_name)
            self._create_project_use_case.execute(req)
            self._notify_project_ready()
            log.info(f"Project created. Project name: {project_name}")

    def on_save_project_triggered(self) -> None:
        try:
            if self._attempt_save(None):
                return
        except ProjectSaveLocationUndefinedError:
            self._prompt_and_save()
            return

    def on_save_project_as_triggered(self) -> None:
        self._prompt_and_save()

    def on_load_project_triggered(self) -> None:
        if load_location := self._presenter.request_load_location_path():
            try:
                req = LoadProjectRequest(load_location)
                self._load_project_use_case.execute(req)
                self._notify_project_ready()
                log.info("Project loaded")
            except Exception as ex:
                log.error(ex)
        log.debug("Load project triggered")

    def load_last_project_if_available(self) -> None:
        if not (last_path := self._project_settings_store.get_last_project_path()):
            return

        try:
            req = LoadProjectRequest(last_path)
            self._load_project_use_case.execute(req)
            self._notify_project_ready()
            log.info("Last project loaded")
        except Exception as ex:
            log.error(ex)
            self._project_settings_store.clear_last_project_path()

    def _notify_project_ready(self) -> None:
        for callback in self._project_ready_callbacks:
            try:
                callback()
            except Exception as ex:
                log.exception("Project ready callback failed: %s", ex)

    def _attempt_save(self, save_path: Optional[str]) -> bool:
        try:
            req = SaveProjectRequest(save_path)
            response = self._save_project_use_case.execute(req)
            log.info(f"Project saved to: {response.access_path}")
            return True
        except ProjectSaveLocationUndefinedError:
            raise
        except Exception as ex:
            log.error(ex)
            return False

    def _prompt_and_save(self) -> None:
        if save_location := self._presenter.request_save_as_location_path():
            try:
                self._attempt_save(save_location)
            except ProjectSaveLocationUndefinedError:
                log.error("Save location remained undefined after prompting the user.")
