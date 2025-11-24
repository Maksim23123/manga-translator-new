from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from app.application.pipelines.events import ActivePipelineChanged, PipelineEventBus
from app.application.pipelines.pipeline_service import PipelineService
from app.application.project.lifecycle_events import (
    ProjectDirtyStateChanged,
    ProjectLifecycleEventBus,
)
from app.application.project.ports import CurrentProjectStore
from app.frameworks.pyside6_gui.tabs.pipelines.graph_editor_tab import GraphEditorTab
from app.interface_adapters.pipelines.gateways.deferred_pyflow_gateway import DeferredPyFlowGateway
from app.interface_adapters.pipelines.controllers.pipeline_list_controller import PipelineListController
from app.interface_adapters.pipelines.controllers.pipeline_properties_controller import (
    PipelinePropertiesController,
)
from app.interface_adapters.pipelines.controllers.pyflow_controller import PyFlowController
from app.interface_adapters.pipelines.presenters.pipeline_list_presenter import PipelineListPresenter
from app.interface_adapters.pipelines.presenters.pipeline_properties_presenter import (
    PipelinePropertiesPresenter,
)
from app.interface_adapters.pipelines.presenters.pyflow_presenter import PyFlowPresenter
from app.interface_adapters.pipelines.repositories.project_pipeline_metadata_repository import (
    ProjectPipelineMetadataRepository,
)
from app.interface_adapters.pipelines.repositories.mem_pipeline_metadata_repository import (
    MemPipelineMetadataRepository,
)
from app.interface_adapters.pipelines.stores.mem_active_pipeline_store import MemActivePipelineStore
from app.interface_adapters.pipelines.storage.local_graph_storage import LocalGraphStorage

log = logging.getLogger(__name__)


@dataclass(slots=True)
class GraphEditorTabBundle:
    tab: GraphEditorTab
    controller: PyFlowController
    presenter: PyFlowPresenter
    service: PipelineService
    event_bus: PipelineEventBus
    pipeline_list_controller: PipelineListController | None = None
    pipeline_list_presenter: PipelineListPresenter | None = None
    pipeline_properties_controller: PipelinePropertiesController | None = None
    pipeline_properties_presenter: PipelinePropertiesPresenter | None = None
    finalize_pipelines: Callable[[], None] | None = None


def build_graph_editor_tab(
    *,
    pipeline_list_controller: PipelineListController | None = None,
    pipeline_list_presenter: PipelineListPresenter | None = None,
    pipeline_properties_controller: PipelinePropertiesController | None = None,
    pipeline_properties_presenter: PipelinePropertiesPresenter | None = None,
    project_store: Optional[CurrentProjectStore] = None,
    lifecycle_event_bus: ProjectLifecycleEventBus | None = None,
) -> GraphEditorTabBundle:
    """Constructs the PyFlow-backed graph editor tab."""
    event_bus = PipelineEventBus()
    metadata_repo = ProjectPipelineMetadataRepository(project_store) if project_store else MemPipelineMetadataRepository()
    shared_temp_root = Path("data") / "temp" / "pipelines"
    graph_storage = LocalGraphStorage(finals_dir=Path("data") / "pipelines", drafts_dir=shared_temp_root)
    pyflow_gateway = DeferredPyFlowGateway()
    active_store = MemActivePipelineStore()

    service = PipelineService(
        metadata_repo=metadata_repo,
        storage=graph_storage,
        pyflow_gateway=pyflow_gateway,
        preview_port=None,
        event_bus=event_bus,
        active_store=active_store,
    )

    # Core PyFlow presenters/controllers
    presenter = PyFlowPresenter()
    controller = PyFlowController(presenter)

    # Pipeline list dock wiring
    pipeline_list_controller = pipeline_list_controller or PipelineListController(
        service=service,
    )
    pipeline_list_presenter = pipeline_list_presenter or PipelineListPresenter(
        event_bus=event_bus,
        collection_provider=lambda: service.collection,
    )

    # Pipeline properties dock wiring
    pipeline_properties_controller = pipeline_properties_controller or PipelinePropertiesController(
        service=service,
    )
    pipeline_properties_presenter = pipeline_properties_presenter or PipelinePropertiesPresenter(
        event_bus=event_bus,
        collection_provider=lambda: service.collection,
    )

    # Build tab and wire PyFlow gateway delegate.
    tab = GraphEditorTab(
        presenter=presenter,
        controller=controller,
        pipeline_list_controller=pipeline_list_controller,
        pipeline_list_presenter=pipeline_list_presenter,
        pipeline_properties_controller=pipeline_properties_controller,
        pipeline_properties_presenter=pipeline_properties_presenter,
        project_ready_callback=_build_project_ready_callback(
            project_store=project_store,
            service=service,
        ),
    )
    pyflow_gateway.set_delegate(tab.pyflow_wrapper)
    _bridge_pipeline_dirty(event_bus, lifecycle_event_bus)
    _wire_pipeline_interactivity(event_bus, tab, service)
    _wire_pipeline_load_warnings(event_bus, tab)

    def finalize_pipelines() -> None:
        if project_store:
            project_data = project_store.get_data()
            project_root = Path(project_data.metadata.get("project_root_path")) if project_data and project_data.metadata.get("project_root_path") else None
            project_id = project_data.project_id.value if project_data else None
            project_meta_path_raw = project_data.metadata.get("project_meta_path") if project_data else None
            project_meta_path = Path(project_meta_path_raw) if project_meta_path_raw else None
            service.configure_storage(project_root, project_id=project_id, project_meta_path=project_meta_path)
        active = service.collection.active
        if active and active.is_dirty:
            try:
                service.save_active()
            except Exception as ex:  # pragma: no cover - depends on PyFlow/runtime FS
                log.error("Failed to save active pipeline '%s' before promotion: %s", active.name, ex)
        service.promote_all()
        service.cleanup_after_save()

    return GraphEditorTabBundle(
        tab=tab,
        controller=controller,
        presenter=presenter,
        service=service,
        event_bus=event_bus,
        pipeline_list_controller=pipeline_list_controller,
        pipeline_list_presenter=pipeline_list_presenter,
        pipeline_properties_controller=pipeline_properties_controller,
        pipeline_properties_presenter=pipeline_properties_presenter,
        finalize_pipelines=finalize_pipelines,
    )


def _build_project_ready_callback(
    *,
    project_store: Optional[CurrentProjectStore],
    service: PipelineService,
) -> Callable[[], None]:
    def _callback() -> None:
        if not project_store:
            return
        project_data = project_store.get_data()
        project_root_raw = project_data.metadata.get("project_root_path") if project_data else None
        project_root = Path(project_root_raw) if project_root_raw else None
        project_id = project_data.project_id.value if project_data else None
        project_meta_path_raw = project_data.metadata.get("project_meta_path") if project_data else None
        project_meta_path = Path(project_meta_path_raw) if project_meta_path_raw else None
        service.configure_storage(project_root, project_id=project_id, project_meta_path=project_meta_path)
        service.load()

    return _callback


def _bridge_pipeline_dirty(
    pipeline_event_bus: PipelineEventBus,
    lifecycle_event_bus: ProjectLifecycleEventBus | None,
) -> None:
    """Forward pipeline mutations to the shared project lifecycle bus."""
    if not lifecycle_event_bus:
        return

    def _mark_dirty(_event) -> None:
        lifecycle_event_bus.publish(ProjectDirtyStateChanged(True))

    from app.application.pipelines.events import (
        PipelineAdded,
        PipelineGraphDirtyChanged,
        PipelineGraphPointerUpdated,
        PipelineRemoved,
        PipelineRenamed,
    )

    def _handle_dirty_changed(event: PipelineGraphDirtyChanged) -> None:
        if event.is_dirty:
            _mark_dirty(event)

    pipeline_event_bus.subscribe(PipelineGraphDirtyChanged, _handle_dirty_changed)
    pipeline_event_bus.subscribe(PipelineAdded, _mark_dirty)
    pipeline_event_bus.subscribe(PipelineRemoved, _mark_dirty)
    pipeline_event_bus.subscribe(PipelineRenamed, _mark_dirty)
    pipeline_event_bus.subscribe(PipelineGraphPointerUpdated, _mark_dirty)


def _wire_pipeline_interactivity(
    pipeline_event_bus: PipelineEventBus,
    tab: GraphEditorTab,
    service: PipelineService,
) -> None:
    """Enable/disable PyFlow interactions when active pipeline changes."""

    def _toggle(event: ActivePipelineChanged) -> None:
        try:
            tab.pyflow_wrapper.set_interactive(bool(event.name))
        except Exception:
            log.debug("Failed to toggle PyFlow interactivity", exc_info=True)

    pipeline_event_bus.subscribe(ActivePipelineChanged, _toggle)

    try:
        tab.pyflow_wrapper.set_interactive(service.collection.active is not None)
    except Exception:
        log.debug("Failed to apply initial PyFlow interactivity state", exc_info=True)


def _wire_pipeline_load_warnings(
    pipeline_event_bus: PipelineEventBus,
    tab: GraphEditorTab,
) -> None:
    """Surface graph load failures to the user instead of failing silently."""
    try:
        from PySide6.QtWidgets import QMessageBox
    except Exception:
        log.debug("PySide6 not available; pipeline load warnings will be logged only")
        return

    from app.application.pipelines.events import PipelineGraphLoadWarning

    def _show(event: PipelineGraphLoadWarning) -> None:
        path_hint = str(event.path) if event.path else "unknown location"
        message = (
            f"Pipeline '{event.name}' graph could not be loaded from {path_hint}.\n"
            f"{event.reason}\nA blank graph was opened instead."
        )
        try:
            QMessageBox.warning(tab, "Pipeline graph missing", message)
        except Exception:
            log.debug("Failed to show pipeline load warning dialog", exc_info=True)

    pipeline_event_bus.subscribe(PipelineGraphLoadWarning, _show)
