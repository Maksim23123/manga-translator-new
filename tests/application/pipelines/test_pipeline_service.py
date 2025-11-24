from __future__ import annotations

from pathlib import Path

from app.application.pipelines.events import ActivePipelineChanged, PipelineEventBus
from app.application.pipelines.pipeline_service import PipelineService
from app.domain.pipelines.graph_pointer import GraphPointer, GraphPointerStatus
from app.interface_adapters.pipelines.repositories.mem_pipeline_metadata_repository import (
    MemPipelineMetadataRepository,
)


class StubGraphStorage:
    def __init__(self, *, fail_promote: bool = False) -> None:
        self.fail_promote = fail_promote
        self.promote_calls: list[GraphPointer] = []

    def draft_path_for(self, pipeline_name: str) -> Path:
        return Path(f"{pipeline_name}.draft")

    def final_path_for(self, pipeline_name: str) -> Path:
        return Path(f"{pipeline_name}.final")

    def promote(self, pointer: GraphPointer) -> GraphPointer:
        self.promote_calls.append(pointer)
        if self.fail_promote:
            raise RuntimeError("promote failed")
        draft = pointer.draft_path or self.draft_path_for("unknown")
        final_path = self.final_path_for(draft.stem)
        return GraphPointer(final_path=final_path, draft_path=None, status=GraphPointerStatus.FINAL)

    def delete_graph(self, pointer: GraphPointer) -> None:  # pragma: no cover - not used here
        pass

    def cleanup_project_orphans(self, _expected: set[str]) -> None:  # pragma: no cover - noop for tests
        pass

    def cleanup_shared_temp(self) -> None:  # pragma: no cover - noop for tests
        pass

    def cleanup_current_shared_temp(self) -> None:  # pragma: no cover - noop for tests
        pass


class StubPyFlowGateway:
    def __init__(self, *, fail_on_load: bool = False) -> None:
        self.load_graph_calls: list[Path] = []
        self.save_graph_calls: list[Path] = []
        self.new_blank_calls = 0
        self.dirty_callbacks = []
        self.fail_on_load = fail_on_load

    def load_graph(self, graph_path: Path) -> None:
        if self.fail_on_load:
            raise RuntimeError("load failed")
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


def test_set_active_saves_previous_dirty_pipeline() -> None:
    event_bus = PipelineEventBus()
    pyflow_gateway = StubPyFlowGateway()
    service = _build_service(event_bus, pyflow_gateway)

    first = service.create("Pipeline")
    service.create("Another Pipeline")
    first.mark_dirty()

    service.set_active("Another Pipeline")

    assert pyflow_gateway.save_graph_calls == [Path("Pipeline.draft")]
    assert service.collection.active and service.collection.active.name == "Another Pipeline"
    assert not first.is_dirty


def test_save_active_marks_pointer_as_draft() -> None:
    event_bus = PipelineEventBus()
    pyflow_gateway = StubPyFlowGateway()
    service = _build_service(event_bus, pyflow_gateway)

    pipeline = service.create("Pipeline")
    pipeline.mark_dirty()

    saved = service.save_active()

    assert saved is pipeline
    assert saved.graph.status is GraphPointerStatus.DRAFT
    assert saved.graph.draft_path == Path("Pipeline.draft")
    assert not saved.is_dirty


def test_promote_all_updates_pointer_and_keeps_drafts_on_failure() -> None:
    event_bus = PipelineEventBus()
    pyflow_gateway = StubPyFlowGateway()
    storage = StubGraphStorage()
    service = PipelineService(
        metadata_repo=MemPipelineMetadataRepository(),
        storage=storage,
        pyflow_gateway=pyflow_gateway,
        preview_port=None,
        event_bus=event_bus,
    )

    pipeline = service.create("Pipeline")
    pipeline.mark_dirty()
    service.save_active()

    promoted = service.promote_all()

    assert promoted == [pipeline]
    assert pipeline.graph.status is GraphPointerStatus.FINAL
    assert pipeline.graph.final_path == Path("Pipeline.final")

    failing_storage = StubGraphStorage(fail_promote=True)
    failing_service = PipelineService(
        metadata_repo=MemPipelineMetadataRepository(),
        storage=failing_storage,
        pyflow_gateway=pyflow_gateway,
        preview_port=None,
        event_bus=event_bus,
    )
    pipeline2 = failing_service.create("Other")
    pipeline2.mark_dirty()
    failing_service.save_active()

    promoted_fail = failing_service.promote_all()

    assert promoted_fail == []
    assert pipeline2.graph.status is GraphPointerStatus.DRAFT


def test_load_missing_graph_warns_and_opens_blank(tmp_path: Path) -> None:
    event_bus = PipelineEventBus()
    pyflow_gateway = StubPyFlowGateway()
    service = _build_service(event_bus, pyflow_gateway)

    pipeline = service.create("Pipeline")
    missing_path = tmp_path / "missing.pygraph"
    pipeline.update_graph(GraphPointer(final_path=missing_path, draft_path=None, status=GraphPointerStatus.FINAL))
    service._metadata_repo.save(service.collection)  # type: ignore[attr-defined]

    warnings = []
    from app.application.pipelines.events import PipelineGraphLoadWarning

    event_bus.subscribe(PipelineGraphLoadWarning, lambda e: warnings.append(e))

    service.load()

    assert pyflow_gateway.new_blank_calls == 1
    assert warnings and warnings[0].path == missing_path
    assert "missing" in warnings[0].reason.lower()


def test_load_graph_error_warns_and_opens_blank(tmp_path: Path) -> None:
    event_bus = PipelineEventBus()
    pyflow_gateway = StubPyFlowGateway(fail_on_load=True)
    service = _build_service(event_bus, pyflow_gateway)

    pipeline = service.create("Pipeline")
    existing_path = tmp_path / "present.pygraph"
    existing_path.write_text("data")
    pipeline.update_graph(GraphPointer(final_path=existing_path, draft_path=None, status=GraphPointerStatus.FINAL))
    service._metadata_repo.save(service.collection)  # type: ignore[attr-defined]

    warnings = []
    from app.application.pipelines.events import PipelineGraphLoadWarning

    event_bus.subscribe(PipelineGraphLoadWarning, lambda e: warnings.append(e))

    service.load()

    assert pyflow_gateway.new_blank_calls == 1
    assert warnings and warnings[0].path == existing_path
    assert "failed to load" in warnings[0].reason.lower()
