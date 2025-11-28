from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.application.pipelines.pyflow_graph_runner import PyFlowGraphRunner


def _init_pyflow():
    from PyFlow import GET_PACKAGES, INITIALIZE

    if not GET_PACKAGES():
        INITIALIZE()


def _build_stub_graph(tmp_path: Path) -> Path:
    """Create a minimal graph with input->output connection."""
    _init_pyflow()
    from PyFlow import getRawNodeInstance
    from PyFlow.Core.GraphManager import GraphManager
    from PyFlow.Core.Common import connectPins

    manager = GraphManager()
    graph = manager.activeGraph()

    input_node = getRawNodeInstance("PipelineInputImageNode", "MangaTranslator")
    output_node = getRawNodeInstance("PipelineOutputNode", "MangaTranslator")

    graph.addNode(input_node)
    graph.addNode(output_node)
    connectPins(input_node.image_out_pin, output_node.pipeline_result_image_input_pin)

    graph_path = tmp_path / "stub.pygraph"
    graph_path.write_text(json.dumps(manager.serialize()))
    return graph_path


def test_runner_loads_and_returns_image(monkeypatch, tmp_path: Path):
    graph_path = _build_stub_graph(tmp_path)
    image_path = tmp_path / "pixel.bin"
    image_path.write_bytes(b"\x01\x02\x03")

    monkeypatch.setattr(
        "PyFlow.Packages.MangaTranslator.Nodes.PipelineInputImageNode.ImageImportLogic.run",
        lambda self, p: ["stub-image"],
    )

    runner = PyFlowGraphRunner()
    runner.load(graph_path)
    output = runner.run({"images": [image_path]})

    assert output["image"] == ["stub-image"]
    assert output["graph_path"] == graph_path


def test_runner_requires_image(tmp_path: Path):
    graph_path = _build_stub_graph(tmp_path)

    runner = PyFlowGraphRunner()
    runner.load(graph_path)

    with pytest.raises(ValueError):
        runner.run({"images": []})
