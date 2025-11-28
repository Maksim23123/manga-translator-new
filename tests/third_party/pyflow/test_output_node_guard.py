import importlib.util
from pathlib import Path

from .pyflow_helpers import DummyGraph, DummyGraphManager, DummyOutputNode


def _load_guard():
    module_path = (
        Path(__file__).resolve()
        .parents[3]
        / "app"
        / "frameworks"
        / "pyside6_gui"
        / "tabs"
        / "pipelines"
        / "output_node_guard.py"
    )
    spec = importlib.util.spec_from_file_location("output_node_guard", module_path)
    guard_module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(guard_module)
    return guard_module.PipelineOutputGuard


def test_guard_rejects_duplicates_per_graph():
    PipelineOutputGuard = _load_guard()
    graph = DummyGraph()
    manager = DummyGraphManager([])
    guard = PipelineOutputGuard(manager)

    first = DummyOutputNode(graph)
    second = DummyOutputNode(graph)

    assert guard.register(first) is True
    assert guard.register(second) is False
    assert guard._by_graph[graph.uid] is first


def test_guard_dedupe_kills_duplicates():
    PipelineOutputGuard = _load_guard()
    graph = DummyGraph()
    first = DummyOutputNode(graph)
    second = DummyOutputNode(graph)
    manager = DummyGraphManager([first, second])
    guard = PipelineOutputGuard(manager)

    guard.dedupe_existing()

    assert guard._by_graph[graph.uid] is first
    assert first.kill_called is False
    assert second.kill_called is True


def test_guard_unregisters_on_kill_signal():
    PipelineOutputGuard = _load_guard()
    graph = DummyGraph()
    node = DummyOutputNode(graph)
    guard = PipelineOutputGuard(DummyGraphManager([node]))

    guard.register(node)
    node.kill()

    assert guard._by_graph == {}
