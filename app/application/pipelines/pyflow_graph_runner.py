from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, List, Optional

log = logging.getLogger(__name__)


class PyFlowGraphRunner:
    """Headless loader/runner for PyFlow `.pygraph` files."""

    _initialized = False

    def __init__(self, packages_root: Optional[Path] = None) -> None:
        default_root = Path(__file__).resolve().parents[2] / "third_party" / "PyFlow"
        self._packages_root = packages_root or default_root
        self._graph_manager = None
        self._graph_path: Optional[Path] = None

    def _init_pyflow(self) -> None:
        if PyFlowGraphRunner._initialized:
            return

        if str(self._packages_root) not in sys.path:
            sys.path.insert(0, str(self._packages_root))

        from PyFlow import INITIALIZE

        try:
            INITIALIZE()
        except Exception:  # pragma: no cover - defensive fallback
            log.exception("Failed to initialize PyFlow; pipeline execution unavailable")
            raise

        PyFlowGraphRunner._initialized = True

    def load(self, graph_path: Path) -> None:
        self._init_pyflow()
        if not graph_path.exists():
            raise FileNotFoundError(graph_path)

        from PyFlow.Core.GraphManager import GraphManager

        data = json.loads(graph_path.read_text())
        manager = GraphManager()
        manager.deserialize(data)

        self._graph_manager = manager
        self._graph_path = graph_path

    def run(self, inputs: dict) -> dict:
        if self._graph_manager is None or self._graph_path is None:
            raise RuntimeError("Graph not loaded; call load(graph_path) first")

        image_path = self._pick_image(inputs.get("images"))
        if image_path is None:
            raise ValueError("No image supplied to run the pipeline")

        input_node = self._get_single_node("PipelineInputImageNode")
        output_node = self._get_single_node("PipelineOutputNode")
        if input_node is None or output_node is None:
            raise RuntimeError("Pipeline graph missing required input/output nodes")

        # Inject image path for the input node.
        setattr(input_node, "_image_path", str(image_path))

        # Compute upstream nodes in topological order and then the output node itself.
        from PyFlow.Core.EvaluationEngine import DefaultEvaluationEngine_Impl

        order = DefaultEvaluationEngine_Impl.getEvaluationOrderIterative(output_node)
        for node in order:
            try:
                node.processNode()
            except Exception:  # pragma: no cover - defensive fallback
                log.exception("Failed computing node %s", node.__class__.__name__)
                raise

        try:
            output_node.processNode()
        except Exception:  # pragma: no cover - defensive fallback
            log.exception("Failed computing pipeline output node")
            raise

        try:
            image = output_node.pipeline_result_image_input_pin.getData()
        except Exception:
            image = None

        return {"image": image, "graph_path": self._graph_path}

    def cleanup(self) -> None:
        try:
            if self._graph_manager:
                try:
                    self._graph_manager.clear()
                except Exception:
                    pass
        finally:
            self._graph_manager = None
            self._graph_path = None

    def _get_single_node(self, class_name: str):
        nodes = self._graph_manager.getAllNodes(classNameFilters=[class_name]) if self._graph_manager else []
        if not nodes:
            return None
        if len(nodes) > 1:
            log.warning("Multiple %s nodes found; using the first", class_name)
        return nodes[0]

    @staticmethod
    def _pick_image(images: Optional[List[Any]]) -> Optional[Path]:
        if not images:
            return None
        candidate = images[0]
        try:
            return Path(candidate)
        except TypeError:
            return None
