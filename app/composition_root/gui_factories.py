from interface_adapters.GUI.presenters.main_window_presenter import MainWindowPresenter
from interface_adapters.GUI.controllers.main_window_controller import MainWindowController
from frameworks.PySide6_gui.main_window import MainWindow
from application.project.use_cases.create_project import CreateProject
from application.project.use_cases.save_project import SaveProject
from application.project.use_cases.load_project import LoadProject

from interface_adapters.project.repositories.mem_current_project_store import MemCurrentProjectStore
from interface_adapters.project.repositories.fs_project_repository import FsProjectRepository
from interface_adapters.project.util.idgen_uuid import UUIDGenerator


def build_main_window() -> MainWindow:
    id_generator = UUIDGenerator()
    mem_current_project_store = MemCurrentProjectStore()
    fs_project_repository = FsProjectRepository()
    
    create_project_use_case = CreateProject(mem_current_project_store, id_generator)
    save_project_use_case = SaveProject(mem_current_project_store, fs_project_repository)
    
    presenter = MainWindowPresenter()
    controller = MainWindowController(
        presenter,
        create_project_use_case,
        save_project_use_case
        )
    return MainWindow(presenter, controller)
     