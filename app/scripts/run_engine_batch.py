from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path
from typing import Optional

try:
    import cv2
except ModuleNotFoundError:
    cv2 = None  # type: ignore[assignment]

try:
    import numpy as np
except ModuleNotFoundError:
    np = None  # type: ignore[assignment]

from app.application.pipelines.pipeline_executor import PipelineExecutionInput, PipelineExecutionRequest, PyFlowPipelineExecutor
from app.application.pipelines.pyflow_graph_runner import PyFlowGraphRunner
from app.application.pipelines.translation_engine import TranslationEngine


def discover_graphs() -> list[Path]:
    roots = [
        Path("data") / "pipelines",
        Path("data") / "temp" / "pipelines",
    ]
    graphs: list[Path] = []
    for root in roots:
        if root.exists():
            graphs.extend(sorted(root.glob("*.pygraph")))
    return graphs


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run multiple PyFlow pipelines headlessly through the translation engine.",
        epilog="Example: python -m app.scripts.run_engine_batch --pipeline A.pygraph --pipeline B.pygraph --image sample.png",
    )
    parser.add_argument(
        "--pipeline",
        action="append",
        type=Path,
        help="Path to .pygraph file; pass multiple times to run several pipelines",
    )
    parser.add_argument("--image", type=Path, help="Path to input image")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory to write resulting images (default: data/pipeline_results/engine_batch)",
    )
    return parser.parse_args(argv)


def save_image(image, output_path: Path) -> Optional[Path]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if image is None:
        return None

    if isinstance(image, (bytes, bytearray, memoryview)):
        try:
            output_path.write_bytes(bytes(image))
            return output_path
        except Exception:
            pass

    if isinstance(image, (list, tuple)):
        try:
            if all(isinstance(v, int) and 0 <= v <= 255 for v in image):
                output_path.write_bytes(bytes(image))
                return output_path
        except Exception:
            pass

    if isinstance(image, (str, Path)):
        candidate = Path(image)
        if candidate.exists():
            try:
                output_path.write_bytes(candidate.read_bytes())
                return output_path
            except Exception:
                pass

    if cv2 is not None:
        try:
            if cv2.imwrite(str(output_path), image):
                return output_path
        except Exception:
            pass
    if np is not None:
        try:
            arr = np.asarray(image)
            if arr.size > 0:
                if cv2 is not None:
                    if cv2.imwrite(str(output_path), arr):
                        return output_path
                else:
                    np.save(output_path.with_suffix(".npy"), arr)
                    return output_path.with_suffix(".npy")
        except Exception:
            pass
    try:
        output_path.write_text(repr(image))
        return output_path
    except Exception:
        return None


def default_output_dir() -> Path:
    root = Path("data") / "pipeline_results" / "engine_batch"
    root.mkdir(parents=True, exist_ok=True)
    return root


def run_pipeline(engine: TranslationEngine, graph_path: Path, image_path: Path, output_dir: Path) -> bool:
    if not graph_path.exists():
        print(f"[skip] Pipeline graph not found: {graph_path}")
        return False

    request = PipelineExecutionRequest(
        id=str(uuid.uuid4()),
        input=PipelineExecutionInput(images=[image_path]),
    )
    result = engine.run(graph_path.stem, graph_path, request)
    if result.error:
        print(f"[fail] {graph_path.name}: {result.error.code} - {result.error.message}")
        return False

    output_path = output_dir / f"{graph_path.stem}_output.png"
    saved = save_image(result.output.get("image"), output_path)
    if saved:
        print(f"[ok] {graph_path.name} -> {saved}")
        return True
    else:
        print(f"[warn] {graph_path.name} succeeded but output could not be saved.")
        return False


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)

    graph_paths = args.pipeline or []
    if not graph_paths:
        selection = input("Enter .pygraph paths (comma-separated), or press Enter to auto-discover: ").strip()
        if selection:
            graph_paths = [Path(token.strip()) for token in selection.split(",") if token.strip()]
        else:
            discovered = discover_graphs()
            if not discovered:
                print("No pipelines discovered under data/pipelines or data/temp/pipelines.")
                return 1
            print("Discovered pipelines (will run all):")
            for p in discovered:
                print(f" - {p}")
            graph_paths = discovered

    image_path = args.image
    if image_path is None:
        image_input = input("Enter path to input image: ").strip()
        if not image_input:
            print("No image provided.")
            return 1
        image_path = Path(image_input)
    if not image_path.exists():
        print(f"Image not found: {image_path}")
        return 1

    output_dir = args.output_dir or default_output_dir()

    engine = TranslationEngine(lambda path: PyFlowPipelineExecutor(PyFlowGraphRunner(), graph_path=path))

    successes = 0
    for graph_path in graph_paths:
        if run_pipeline(engine, graph_path, image_path, output_dir):
            successes += 1

    total = len(graph_paths)
    print(f"Completed {successes}/{total} pipelines.")
    return 0 if successes == total else 1


if __name__ == "__main__":
    sys.exit(main())
