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

from app.application.pipelines.pipeline_executor import (
    PipelineExecutionInput,
    PipelineExecutionRequest,
    PyFlowPipelineExecutor,
)
from app.application.pipelines.pyflow_graph_runner import PyFlowGraphRunner


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


def prompt_for_choice(options: list[Path], label: str) -> Path:
    print(f"Select {label}:")
    for idx, path in enumerate(options, start=1):
        print(f"  [{idx}] {path}")
    while True:
        choice = input(f"Enter {label} number: ").strip()
        if not choice.isdigit():
            continue
        idx = int(choice)
        if 1 <= idx <= len(options):
            return options[idx - 1]


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a PyFlow pipeline headlessly.")
    parser.add_argument("--pipeline", type=Path, help="Path to .pygraph file")
    parser.add_argument("--image", type=Path, help="Path to input image")
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to write resulting image (default: data/pipeline_results/<pipeline>_output.png)",
    )
    return parser.parse_args(argv)


def save_image(image, output_path: Path) -> Optional[Path]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if image is None:
        print("No image returned from pipeline.")
        return None

    # If the pipeline returned raw bytes (or a list of byte values), persist them directly.
    if isinstance(image, (bytes, bytearray, memoryview)):
        try:
            output_path.write_bytes(bytes(image))
            return output_path
        except Exception:
            pass

    if isinstance(image, (list, tuple)):
        try:
            # Attempt to interpret a flat list/tuple of ints as raw bytes.
            if all(isinstance(v, int) and 0 <= v <= 255 for v in image):
                output_path.write_bytes(bytes(image))
                return output_path
        except Exception:
            pass

    # If a path/string was returned, copy the file into place.
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
                    # Save as raw numpy for inspection.
                    np.save(output_path.with_suffix(".npy"), arr)
                    return output_path.with_suffix(".npy")
        except Exception:
            pass
    try:
        output_path.write_text(repr(image))
        return output_path
    except Exception:
        return None


def default_output_path(graph_path: Path) -> Path:
    root = Path("data") / "pipeline_results"
    root.mkdir(parents=True, exist_ok=True)
    stem = graph_path.stem if graph_path else "pipeline"
    return root / f"{stem}_output.png"


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)

    graph_path = args.pipeline
    if graph_path is None:
        available = discover_graphs()
        if available:
            graph_path = prompt_for_choice(available, "pipeline")
        else:
            manual = input("No pipelines found. Enter path to a .pygraph file: ").strip()
            if not manual:
                print("No pipeline selected.")
                return 1
            graph_path = Path(manual)

    image_path = args.image
    if image_path is None:
        image_input = input("Enter path to input image: ").strip()
        image_path = Path(image_input)

    if not graph_path.exists():
        print(f"Pipeline graph not found: {graph_path}")
        return 1
    if not image_path.exists():
        print(f"Image not found: {image_path}")
        return 1

    runner = PyFlowGraphRunner()
    executor = PyFlowPipelineExecutor(runner, graph_path=graph_path)
    executor.prepare(graph_path)

    request = PipelineExecutionRequest(
        id=str(uuid.uuid4()),
        input=PipelineExecutionInput(images=[image_path]),
    )

    result = executor.run(request)
    if result.error:
        print(f"Pipeline failed: {result.error.code} - {result.error.message}")
        return 1

    output_path = args.output or default_output_path(graph_path)
    saved = save_image(result.output.get("image"), output_path)
    if saved:
        print(f"Pipeline succeeded. Output saved to: {saved}")
        return 0
    else:
        print("Pipeline succeeded, but failed to save output image.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
