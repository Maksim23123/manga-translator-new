from __future__ import annotations

from dataclasses import dataclass

from app.application.doc_units.events import DocUnitEventBus
from app.application.doc_units.ports import ActiveDocUnitStore
from app.application.doc_units.use_cases.hierarchy import (
    CreateHierarchyFolder,
    DeleteHierarchyNodes,
    LoadHierarchy,
    MoveHierarchyNodes,
    RenameHierarchyNode,
    SelectHierarchyNode,
)
from app.application.page_editor.page_editor_service import PageEditorService
from app.application.pipelines.pipeline_service import PipelineService
from app.application.project.ports import CurrentProjectStore, IdGenerator
from app.frameworks.pyside6_gui.tabs.page_editor.page_editor_tab import PageEditorTab
from app.interface_adapters.doc_units.controllers.hierarchy_controller import HierarchyController
from app.interface_adapters.doc_units.presenters.hierarchy_presenter import HierarchyPresenter
from app.interface_adapters.doc_units.repositories.project_doc_unit_repository import (
    ProjectDocUnitRepository,
)
from app.interface_adapters.media.filesystem_media_store import FileSystemMediaStore
from app.interface_adapters.page_editor.page_editor_controller import PageEditorController
from app.interface_adapters.page_editor.page_editor_presenter import PageEditorPresenter
from app.interface_adapters.page_editor.translation_output_store import (
    FilesystemTranslationOutputStore,
)


@dataclass(slots=True)
class PageEditorTabBundle:
    tab: PageEditorTab


def build_page_editor_tab(
    *,
    project_store: CurrentProjectStore,
    id_generator: IdGenerator,
    doc_unit_event_bus: DocUnitEventBus,
    active_doc_unit_store: ActiveDocUnitStore,
    pipeline_service: PipelineService,
    pipeline_event_bus,
) -> PageEditorTabBundle:
    doc_unit_repository = ProjectDocUnitRepository(project_store)
    media_store = FileSystemMediaStore(project_store, id_generator)
    translation_store = FilesystemTranslationOutputStore(project_store)

    page_editor_service = PageEditorService(
        repository=doc_unit_repository,
        active_store=active_doc_unit_store,
        media_store=media_store,
        pipeline_service=pipeline_service,
        translation_output_store=translation_store,
        doc_unit_events=doc_unit_event_bus,
    )

    load_hierarchy_use_case = LoadHierarchy(
        repository=doc_unit_repository,
        active_store=active_doc_unit_store,
        events=doc_unit_event_bus,
    )
    create_folder_use_case = CreateHierarchyFolder(
        repository=doc_unit_repository,
        active_store=active_doc_unit_store,
        ids=id_generator,
        events=doc_unit_event_bus,
    )
    rename_node_use_case = RenameHierarchyNode(
        repository=doc_unit_repository,
        active_store=active_doc_unit_store,
        events=doc_unit_event_bus,
    )
    delete_nodes_use_case = DeleteHierarchyNodes(
        repository=doc_unit_repository,
        active_store=active_doc_unit_store,
        events=doc_unit_event_bus,
    )
    move_nodes_use_case = MoveHierarchyNodes(
        repository=doc_unit_repository,
        active_store=active_doc_unit_store,
        ids=id_generator,
        events=doc_unit_event_bus,
    )
    select_node_use_case = SelectHierarchyNode(
        repository=doc_unit_repository,
        active_store=active_doc_unit_store,
        events=doc_unit_event_bus,
    )

    hierarchy_controller = HierarchyController(
        load_use_case=load_hierarchy_use_case,
        create_folder_use_case=create_folder_use_case,
        rename_use_case=rename_node_use_case,
        delete_use_case=delete_nodes_use_case,
        move_use_case=move_nodes_use_case,
        select_use_case=select_node_use_case,
    )
    hierarchy_presenter = HierarchyPresenter(
        event_bus=doc_unit_event_bus,
        load_use_case=load_hierarchy_use_case,
    )

    page_editor_controller = PageEditorController(page_editor_service)
    page_editor_presenter = PageEditorPresenter(
        service=page_editor_service,
        doc_unit_events=doc_unit_event_bus,
        pipeline_events=pipeline_event_bus,
    )

    tab = PageEditorTab(
        presenter=page_editor_presenter,
        controller=page_editor_controller,
        hierarchy_presenter=hierarchy_presenter,
        hierarchy_controller=hierarchy_controller,
    )

    return PageEditorTabBundle(tab=tab)
