from __future__ import annotations

from app.application.doc_units.events import DocUnitEventBus
from app.application.doc_units.use_cases.create_doc_unit import CreateDocUnit
from app.application.doc_units.use_cases.delete_doc_unit import DeleteDocUnit
from app.application.doc_units.use_cases.import_doc_unit_asset import (
    ImportDocUnitAsset,
)
from app.application.doc_units.use_cases.list_doc_units import ListDocUnits
from app.application.doc_units.use_cases.rename_doc_unit import RenameDocUnit
from app.application.doc_units.use_cases.set_active_doc_unit import (
    SetActiveDocUnit,
)
from app.application.doc_units.ports import ActiveDocUnitStore
from app.application.project.ports import CurrentProjectStore, IdGenerator
from app.frameworks.pyside6_gui.tabs.doc_units.doc_unit_tab import DocUnitTab
from app.interface_adapters.doc_units.controllers.doc_unit_controller import (
    DocUnitController,
)
from app.interface_adapters.doc_units.presenters.doc_unit_presenter import (
    DocUnitPresenter,
)
from app.interface_adapters.doc_units.repositories.project_doc_unit_repository import (
    ProjectDocUnitRepository,
)
from app.interface_adapters.doc_units.stores.mem_active_doc_unit_store import (
    MemActiveDocUnitStore,
)
from app.interface_adapters.media.filesystem_media_store import (
    FileSystemMediaStore,
)


def build_doc_unit_tab(
    project_store: CurrentProjectStore,
    id_generator: IdGenerator,
    active_store: ActiveDocUnitStore | None = None,
) -> DocUnitTab:
    doc_unit_repository = ProjectDocUnitRepository(project_store)
    active_doc_unit_store = active_store or MemActiveDocUnitStore()
    event_bus = DocUnitEventBus()

    list_use_case = ListDocUnits(doc_unit_repository)
    presenter = DocUnitPresenter(event_bus, list_use_case)

    create_use_case = CreateDocUnit(
        repository=doc_unit_repository,
        active_store=active_doc_unit_store,
        ids=id_generator,
        events=event_bus,
    )
    rename_use_case = RenameDocUnit(doc_unit_repository, event_bus)
    delete_use_case = DeleteDocUnit(
        repository=doc_unit_repository,
        active_store=active_doc_unit_store,
        events=event_bus,
    )
    set_active_use_case = SetActiveDocUnit(active_doc_unit_store, event_bus)
    media_store = FileSystemMediaStore(project_store, id_generator)
    import_use_case = ImportDocUnitAsset(
        repository=doc_unit_repository,
        media_store=media_store,
        ids=id_generator,
        events=event_bus,
    )

    controller = DocUnitController(
        create_use_case=create_use_case,
        rename_use_case=rename_use_case,
        delete_use_case=delete_use_case,
        set_active_use_case=set_active_use_case,
        import_asset_use_case=import_use_case,
    )

    return DocUnitTab(presenter=presenter, controller=controller)
