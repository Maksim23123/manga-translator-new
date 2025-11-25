from __future__ import annotations

import base64
from pathlib import Path

import pytest

from app.application.pipelines.pipeline_executor import (
    EngineParams,
    PipelineExecutionContext,
    PipelineExecutionInput,
    PipelineExecutionRequest,
    PipelineExecutionResult,
    PipelineExecutionError,
    PipelineExecutionDiagnostics,
    PyFlowPipelineExecutor,
)


class StubGraphRunner:
    def __init__(self, *, fail_on_load: bool = False, fail_on_run: bool = False) -> None:
        self.loaded_path: Path | None = None
        self.fail_on_load = fail_on_load
        self.fail_on_run = fail_on_run
        self.cleaned_up = False
        self.run_inputs: list[dict] = []

    def load(self, graph_path: Path) -> None:
        if self.fail_on_load:
            raise RuntimeError("load failed")
        if not graph_path.exists():
            raise FileNotFoundError(graph_path)
        self.loaded_path = graph_path

    def run(self, inputs: dict) -> dict:
        if self.fail_on_run:
            raise RuntimeError("run failed")
        if not self.loaded_path:
            raise RuntimeError("graph not loaded")
        self.run_inputs.append(inputs)

        images = []
        for image_path in inputs.get("images", []):
            data = Path(image_path).read_bytes()
            images.append({"path": Path(image_path), "byte_size": len(data)})

        return {
            "graph": self.loaded_path.name,
            "images": images,
            "metadata": inputs.get("metadata", {}),
            "executor_params": inputs.get("executor_params", {}),
        }

    def cleanup(self) -> None:
        self.cleaned_up = True


def _write_sample_png(path: Path) -> None:
    """Write a 1x1 PNG so the runner can read real bytes without extra deps."""
    png_base64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO4X"
        "0XQAAAAASUVORK5CYII="
    )
    path.write_bytes(base64.b64decode(png_base64))


def test_prepare_and_run_returns_output_and_diagnostics(tmp_path: Path) -> None:
    graph_path = tmp_path / "sample.pygraph"
    graph_path.write_text("graph")
    image_path = tmp_path / "pixel.png"
    _write_sample_png(image_path)

    runner = StubGraphRunner()
    executor = PyFlowPipelineExecutor(runner)
    executor.prepare(graph_path, executor_params={"threshold": 0.5})

    request = PipelineExecutionRequest(
        id="req-1",
        input=PipelineExecutionInput(images=[image_path], metadata={"page": 1}),
        executor_params={"threshold": 0.7},
        engine_params=EngineParams(device="cpu"),
        context=PipelineExecutionContext(project_id="proj", session_id="sess"),
    )

    result = executor.run(request)

    assert result.error is None
    assert result.output["graph"] == graph_path.name
    assert result.output["images"][0]["byte_size"] == image_path.read_bytes().__len__()
    assert result.output["executor_params"]["threshold"] == 0.7  # request overrides prepare default
    assert result.diagnostics and result.diagnostics.graph_path == graph_path
    assert runner.run_inputs[-1]["executor_params"]["threshold"] == 0.7


def test_run_without_prepare_returns_error(tmp_path: Path) -> None:
    executor = PyFlowPipelineExecutor(StubGraphRunner())

    request = PipelineExecutionRequest(id="req-missing", input=PipelineExecutionInput())
    result = executor.run(request)

    assert isinstance(result, PipelineExecutionResult)
    assert result.error and result.error.code == "not_prepared"


def test_prepare_raises_on_missing_graph(tmp_path: Path) -> None:
    executor = PyFlowPipelineExecutor(StubGraphRunner())
    with pytest.raises(FileNotFoundError):
        executor.prepare(tmp_path / "missing.pygraph")


def test_run_failure_wraps_error(tmp_path: Path) -> None:
    graph_path = tmp_path / "sample.pygraph"
    graph_path.write_text("graph")

    runner = StubGraphRunner(fail_on_run=True)
    executor = PyFlowPipelineExecutor(runner)
    executor.prepare(graph_path)

    request = PipelineExecutionRequest(id="req-fail", input=PipelineExecutionInput())
    result = executor.run(request)

    assert isinstance(result.error, PipelineExecutionError)
    assert result.error.code == "execution_failed"
    assert isinstance(result.diagnostics, PipelineExecutionDiagnostics)


def test_cleanup_resets_prepared_state(tmp_path: Path) -> None:
    graph_path = tmp_path / "sample.pygraph"
    graph_path.write_text("graph")

    runner = StubGraphRunner()
    executor = PyFlowPipelineExecutor(runner)
    executor.prepare(graph_path)

    executor.cleanup()
    assert runner.cleaned_up

    # After cleanup, run should refuse to execute until prepared again.
    request = PipelineExecutionRequest(id="req-after-cleanup", input=PipelineExecutionInput())
    result = executor.run(request)

    assert result.error and result.error.code == "not_prepared"
