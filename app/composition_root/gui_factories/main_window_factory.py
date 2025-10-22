from app.application.project.use_cases.create_project import CreateProject
from app.application.project.use_cases.load_project import LoadProject
from app.application.project.use_cases.save_project import SaveProject
from app.composition_root.gui_factories.doc_units.tab_factory import (
    build_doc_unit_tab,
)
from app.frameworks.pyside6_gui.main_window import MainWindow
from app.interface_adapters.gui.controllers.main_window_controller import (
    MainWindowController,
)
from app.interface_adapters.gui.presenters.main_window_presenter import (
    MainWindowPresenter,
)
from app.interface_adapters.project.repositories.fs_project_repository import (
    FsProjectRepository,
)
from app.interface_adapters.project.repositories.mem_current_project_store import (
    MemCurrentProjectStore,
)
from app.frameworks.pyside6_gui.project.qt_project_settings_store import QtProjectSettingsStore
from app.interface_adapters.project.util.idgen_uuid import UUIDGenerator


def build_main_window() -> MainWindow:
    id_generator = UUIDGenerator()
    mem_current_project_store = MemCurrentProjectStore()
    fs_project_repository = FsProjectRepository()
    project_settings_store = QtProjectSettingsStore()

    doc_unit_tab = build_doc_unit_tab(
        project_store=mem_current_project_store,
        id_generator=id_generator,
    )

    create_project_use_case = CreateProject(mem_current_project_store, id_generator)
    save_project_use_case = SaveProject(
        mem_current_project_store,
        fs_project_repository,
        project_settings_store,
    )
    load_project_use_case = LoadProject(
        mem_current_project_store,
        fs_project_repository,
        project_settings_store,
    )

    presenter = MainWindowPresenter()
    controller = MainWindowController(
        presenter,
        create_project_use_case,
        save_project_use_case,
        load_project_use_case,
        project_settings_store,
        project_ready_callbacks=[doc_unit_tab.on_project_available],
    )

    main_window = MainWindow(presenter, controller)

    main_window.connect_tabs([doc_unit_tab])
    if mem_current_project_store.is_set:
        doc_unit_tab.on_project_available()
    controller.load_last_project_if_available()
    return main_window
