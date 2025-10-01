from ..presenters.main_window_presenter import MainWindowPresenter
from application.project.use_cases.create_project import CreateProject
from application.project.use_cases.save_project import SaveProject
from application.project.dto import CreateProjectRequest
from application.project.dto import SaveProjectRequest
import logging
log = logging.getLogger(__name__)



class MainWindowController:
    def __init__(self,
                 presenter: MainWindowPresenter,
                 create_project_use_case: CreateProject,
                 save_project_use_case: SaveProject
                 ) -> None:
        self._presenter = presenter
        self._create_project_use_case = create_project_use_case
        self._save_project_use_case = save_project_use_case
    
    
    def on_new_project_triggered(self) -> None:
        if project_name := self._presenter.request_project_name():
            req = CreateProjectRequest(project_name)
            self._create_project_use_case.execute(req)
            log.info(f"Project created. Project name: {project_name}")
    
    
    def on_save_project_triggered(self) -> None:
        if save_location := self._presenter.request_location_uri():
            try:
                req = SaveProjectRequest(save_location)
                self._save_project_use_case.execute(req)
                log.info(f"Project saved to: {save_location}")
            except Exception as ex:
                log.error(ex)