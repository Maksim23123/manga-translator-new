"""Standalone CLI to run a pipeline executor against an image."""
# Usage: python scripts/run_pipeline_cli.py
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

# Ensure local imports work when running directly.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.application.pipelines.pipeline_executor import (  # noqa: E402
    EngineParams,
    PipelineExecutionContext,
    PipelineExecutionInput,
    PipelineExecutionRequest,
    PipelineExecutionResult,
    PyFlowPipelineExecutor,
    GraphRunner,
)


class SimpleGraphRunner(GraphRunner):
    """Minimal graph runner that echoes inputs instead of executing PyFlow."""

    def __init__(self) -> None:
        self._loaded_path: Path | None = None

    def load(self, graph_path: Path) -> None:
        if not graph_path.exists():
            raise FileNotFoundError(graph_path)
        self._loaded_path = graph_path

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        if not self._loaded_path:
            raise RuntimeError("Graph not loaded")

        images_info = []
        for image_path in inputs.get("images", []):
            path_obj = Path(image_path)
            data = path_obj.read_bytes()
            images_info.append(
                {
                    "path": str(path_obj),
                    "bytes": len(data),
                }
            )

        return {
            "graph_path": str(self._loaded_path),
            "images": images_info,
            "metadata": inputs.get("metadata", {}),
            "executor_params": inputs.get("executor_params", {}),
        }

    def cleanup(self) -> None:
        self._loaded_path = None


def prompt_path(label: str) -> Path:
    value = input(f"{label}: ").strip('" ').strip("' ")
    path = Path(value).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def format_result(result: PipelineExecutionResult) -> str:
    payload = asdict(result)
    return json.dumps(payload, indent=2, default=str)


def main() -> int:
    try:
        pipeline_path = prompt_path("Enter pipeline .pygraph path")
        image_path = prompt_path("Enter image path")
    except FileNotFoundError as ex:
        print(f"Path not found: {ex}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 1

    runner = SimpleGraphRunner()
    executor = PyFlowPipelineExecutor(runner)

    try:
        executor.prepare(pipeline_path, executor_params={"demo": True})
        request = PipelineExecutionRequest(
            id="demo-1",
            input=PipelineExecutionInput(images=[image_path]),
            engine_params=EngineParams(device="cpu"),
            context=PipelineExecutionContext(session_id="demo"),
        )
        result = executor.run(request)
        print("Execution result:")
        print(format_result(result))
    except Exception as ex:  # pragma: no cover - interactive script
        print(f"Failed to run pipeline: {ex}", file=sys.stderr)
        return 1
    finally:
        executor.cleanup()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
