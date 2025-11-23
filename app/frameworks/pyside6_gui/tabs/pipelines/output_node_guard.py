from __future__ import annotations

import logging
from typing import Dict, Optional
from uuid import UUID

try:
    from app.third_party.PyFlow.PyFlow.Core.GraphManager import GraphManager
    from app.third_party.PyFlow.PyFlow.Core.NodeBase import NodeBase
except Exception:  # pragma: no cover - only imported inside the GUI runtime
    GraphManager = None  # type: ignore[assignment]
    NodeBase = None  # type: ignore[assignment]

log = logging.getLogger(__name__)

_global_guard: Optional["PipelineOutputGuard"] = None


def set_global_output_guard(guard: "PipelineOutputGuard") -> None:
    """Expose a singleton guard so pipeline output nodes can register themselves."""
    global _global_guard
    _global_guard = guard


def get_global_output_guard() -> Optional["PipelineOutputGuard"]:
    return _global_guard


class PipelineOutputGuard:
    """Tracks pipeline output nodes and rejects duplicates per graph."""

    def __init__(self, graph_manager: GraphManager) -> None:
        self._graph_manager = graph_manager
        self._by_graph: Dict[UUID, NodeBase] = {}

    def reset(self) -> None:
        """Clear tracked nodes; call when graphs are recreated/loaded."""
        self._by_graph.clear()

    def register(self, node: NodeBase) -> bool:
        """Attempt to register a node; returns False if a graph already owns one."""
        graph = node.graph() if callable(getattr(node, "graph", None)) else None
        graph_uid = getattr(graph, "uid", None)
        if graph_uid is None:
            # If we cannot detect the graph, allow the node to exist to avoid crashes.
            return True

        existing = self._by_graph.get(graph_uid)
        if existing and existing is not node:
            if not self._node_exists_in_graph(existing):
                # Clear stale reference and accept the newcomer.
                self._by_graph.pop(graph_uid, None)
            else:
                return False

        self._by_graph[graph_uid] = node
        try:
            node.killed.connect(lambda *_: self._on_node_killed(graph_uid, node))
        except Exception:
            log.debug("Failed to attach killed handler for pipeline output node", exc_info=True)
        return True

    def dedupe_existing(self) -> None:
        """Sweep all graphs and remove duplicate output nodes, keeping the first per graph."""
        try:
            nodes = self._graph_manager.getAllNodes(classNameFilters=["PipelineOutputNode"])
        except Exception:
            log.debug("Pipeline output dedupe failed; graph manager not ready", exc_info=True)
            return

        seen: Dict[UUID, NodeBase] = {}
        for node in nodes:
            graph = node.graph() if callable(getattr(node, "graph", None)) else None
            graph_uid = getattr(graph, "uid", None)
            if graph_uid is None:
                continue

            if graph_uid in seen:
                try:
                    node.kill()
                except Exception:
                    log.debug("Failed to kill duplicate pipeline output node", exc_info=True)
                continue

            seen[graph_uid] = node
            self._by_graph[graph_uid] = node

    def _on_node_killed(self, graph_uid: UUID, node: NodeBase) -> None:
        """Clean up tracking when a node goes away."""
        if self._by_graph.get(graph_uid) is node:
            self._by_graph.pop(graph_uid, None)

    def _node_exists_in_graph(self, node: NodeBase) -> bool:
        """Check whether the tracked node is still part of its graph."""
        graph = node.graph() if callable(getattr(node, "graph", None)) else None
        try:
            nodes = graph.getNodes() if graph else {}
            return bool(nodes and node.uid in nodes)
        except Exception:
            return True
