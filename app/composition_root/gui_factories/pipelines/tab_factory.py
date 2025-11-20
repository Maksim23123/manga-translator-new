from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.application.pipelines.events import PipelineEventBus
from app.application.pipelines.pipeline_service import PipelineService
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
from app.interface_adapters.pipelines.repositories.mem_pipeline_metadata_repository import (
    MemPipelineMetadataRepository,
)
from app.interface_adapters.pipelines.storage.local_graph_storage import LocalGraphStorage


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


def build_graph_editor_tab(
    *,
    pipeline_list_controller: PipelineListController | None = None,
    pipeline_list_presenter: PipelineListPresenter | None = None,
    pipeline_properties_controller: PipelinePropertiesController | None = None,
    pipeline_properties_presenter: PipelinePropertiesPresenter | None = None,
) -> GraphEditorTabBundle:
    """Constructs the PyFlow-backed graph editor tab."""
    event_bus = PipelineEventBus()
    metadata_repo = MemPipelineMetadataRepository()
    graph_storage = LocalGraphStorage(Path("data") / "pipelines")
    pyflow_gateway = DeferredPyFlowGateway()

    service = PipelineService(
        metadata_repo=metadata_repo,
        storage=graph_storage,
        pyflow_gateway=pyflow_gateway,
        preview_port=None,
        event_bus=event_bus,
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
        collection=service.collection,
    )

    # Pipeline properties dock wiring
    pipeline_properties_controller = pipeline_properties_controller or PipelinePropertiesController(
        service=service,
    )
    pipeline_properties_presenter = pipeline_properties_presenter or PipelinePropertiesPresenter(
        event_bus=event_bus,
        collection=service.collection,
    )

    # Build tab and wire PyFlow gateway delegate.
    tab = GraphEditorTab(
        presenter=presenter,
        controller=controller,
        pipeline_list_controller=pipeline_list_controller,
        pipeline_list_presenter=pipeline_list_presenter,
        pipeline_properties_controller=pipeline_properties_controller,
        pipeline_properties_presenter=pipeline_properties_presenter,
    )
    pyflow_gateway.set_delegate(tab.pyflow_wrapper)

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
    )
