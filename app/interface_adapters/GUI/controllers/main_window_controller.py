from ..presenters.main_window_presenter import MainWindowPresenter
from application.project.use_cases.create_project import CreateProject
from application.project.dto import CreateProjectRequest
import logging
log = logging.getLogger(__name__)



class MainWindowController:
    def __init__(self,
                 presenter: MainWindowPresenter,
                 create_project_use_case: CreateProject
                 ) -> None:
        self._presenter = presenter
        self._create_project_use_case = create_project_use_case
    
    
    def on_new_project_triggered(self) -> None:
        if project_name := self._presenter.request_project_name():
            req = CreateProjectRequest(project_name)
            self._create_project_use_case.execute(req)
            log.info(f"Project created. Project name: {project_name}")