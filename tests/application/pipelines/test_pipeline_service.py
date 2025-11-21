from __future__ import annotations

from pathlib import Path

from app.application.pipelines.events import ActivePipelineChanged, PipelineEventBus
from app.application.pipelines.pipeline_service import PipelineService
from app.domain.pipelines.graph_pointer import GraphPointer
from app.interface_adapters.pipelines.repositories.mem_pipeline_metadata_repository import (
    MemPipelineMetadataRepository,
)


class StubGraphStorage:
    def draft_path_for(self, pipeline_name: str) -> Path:
        return Path(f"{pipeline_name}.draft")

    def final_path_for(self, pipeline_name: str) -> Path:
        return Path(f"{pipeline_name}.final")

    def promote(self, pointer: GraphPointer) -> GraphPointer:
        return pointer

    def delete_graph(self, pointer: GraphPointer) -> None:  # pragma: no cover - not used here
        pass


class StubPyFlowGateway:
    def __init__(self) -> None:
        self.load_graph_calls: list[Path] = []
        self.save_graph_calls: list[Path] = []
        self.new_blank_calls = 0
        self.dirty_callbacks = []

    def load_graph(self, graph_path: Path) -> None:
        self.load_graph_calls.append(graph_path)

    def save_graph(self, target_path: Path) -> None:
        self.save_graph_calls.append(target_path)

    def new_blank(self) -> None:
        self.new_blank_calls += 1

    def on_dirty_changed(self, callback) -> None:
        self.dirty_callbacks.append(callback)


def _build_service(event_bus: PipelineEventBus, pyflow_gateway: StubPyFlowGateway) -> PipelineService:
    return PipelineService(
        metadata_repo=MemPipelineMetadataRepository(),
        storage=StubGraphStorage(),
        pyflow_gateway=pyflow_gateway,
        preview_port=None,
        event_bus=event_bus,
    )


def test_create_first_pipeline_publishes_active_event_and_resets_pyflow() -> None:
    event_bus = PipelineEventBus()
    pyflow_gateway = StubPyFlowGateway()
    service = _build_service(event_bus, pyflow_gateway)

    active_events: list[str | None] = []
    event_bus.subscribe(ActivePipelineChanged, lambda e: active_events.append(e.name))

    service.create("Pipeline")

    assert active_events == ["Pipeline"]
    assert pyflow_gateway.new_blank_calls == 1
    assert not pyflow_gateway.load_graph_calls


def test_create_additional_pipeline_keeps_existing_active() -> None:
    event_bus = PipelineEventBus()
    pyflow_gateway = StubPyFlowGateway()
    service = _build_service(event_bus, pyflow_gateway)

    first = service.create("Pipeline")
    assert service.collection.active is first
    assert pyflow_gateway.new_blank_calls == 1

    active_events: list[str | None] = []
    event_bus.subscribe(ActivePipelineChanged, lambda e: active_events.append(e.name))

    service.create("Another Pipeline")

    assert service.collection.active is first
    assert active_events == []
    assert pyflow_gateway.new_blank_calls == 1
    assert not pyflow_gateway.load_graph_calls
