import logging

from app.application.project.use_cases.create_project import CreateProject
from app.application.project.use_cases.save_project import SaveProject
from app.application.project.use_cases.load_project import LoadProject
from app.application.project.dto import (
    CreateProjectRequest,
    SaveProjectRequest,
    LoadProjectRequest,
)

from ..presenters.main_window_presenter import MainWindowPresenter

log = logging.getLogger(__name__)


class MainWindowController:
    def __init__(
        self,
        presenter: MainWindowPresenter,
        create_project_use_case: CreateProject,
        save_project_use_case: SaveProject,
        load_project_use_case: LoadProject,
    ) -> None:
        self._presenter = presenter
        self._create_project_use_case = create_project_use_case
        self._save_project_use_case = save_project_use_case
        self._load_project_use_case = load_project_use_case

    def on_new_project_triggered(self) -> None:
        if project_name := self._presenter.request_project_name():
            req = CreateProjectRequest(project_name)
            self._create_project_use_case.execute(req)
            log.info(f"Project created. Project name: {project_name}")

    def on_save_project_triggered(self) -> None:
        if save_location := self._presenter.request_save_location_path():
            try:
                req = SaveProjectRequest(save_location)
                response = self._save_project_use_case.execute(req)
                log.info(f"Project saved to: {response.access_path}")
            except Exception as ex:
                log.error(ex)

    def on_load_project_triggered(self) -> None:
        if load_location := self._presenter.request_load_location_path():
            try:
                req = LoadProjectRequest(load_location)
                self._load_project_use_case.execute(req)
                log.info("Project loaded")
            except Exception as ex:
                log.error(ex)
        log.debug("Load project triggered")
