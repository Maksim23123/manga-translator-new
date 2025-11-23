from __future__ import annotations

import logging
from typing import Any, Dict, Optional
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
    """Tracks pipeline output nodes and rejects duplicates per root graph (including subgraphs)."""

    def __init__(self, graph_manager: GraphManager) -> None:
        self._graph_manager = self._unwrap_graph_manager(graph_manager)
        self._by_graph: Dict[UUID, NodeBase] = {}

    def reset(self) -> None:
        """Clear tracked nodes; call when graphs are recreated/loaded."""
        self._by_graph.clear()

    def register(self, node: NodeBase) -> bool:
        """Attempt to register a node; returns False if a graph already owns one."""
        graph = node.graph() if callable(getattr(node, "graph", None)) else None
        graph_uid = self._graph_key(graph)
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
        """Sweep all graphs and remove duplicate output nodes, keeping the first per root graph."""
        manager = self._graph_manager
        if manager is None or not hasattr(manager, "getAllNodes"):
            log.debug("Pipeline output dedupe failed; graph manager not ready")
            return
        try:
            nodes = manager.getAllNodes(classNameFilters=["PipelineOutputNode"])
        except Exception:
            log.debug("Pipeline output dedupe failed; graph manager not ready", exc_info=True)
            return

        seen: Dict[UUID, NodeBase] = {}
        for node in nodes:
            graph = node.graph() if callable(getattr(node, "graph", None)) else None
            graph_uid = self._graph_key(graph)
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

    @staticmethod
    def _unwrap_graph_manager(graph_manager: Any) -> Any:
        """Return the underlying GraphManager when a singleton wrapper is provided."""
        get_fn = getattr(graph_manager, "get", None)
        if callable(get_fn):
            try:
                unwrapped = get_fn()
                if unwrapped:
                    return unwrapped
            except Exception:
                log.debug("Failed to unwrap graph manager singleton", exc_info=True)
        return graph_manager

    @staticmethod
    def _graph_key(graph: Any) -> Optional[UUID]:
        """Use the root graph UID as the ownership key to prevent duplicates across subgraphs."""
        if graph is None:
            return None

        # Walk up to the root graph if a parent chain exists.
        parent = getattr(graph, "parentGraph", None)
        try:
            while parent is not None:
                graph = parent
                parent = getattr(graph, "parentGraph", None)
        except Exception:
            pass

        uid = getattr(graph, "uid", None)
        if uid is not None:
            return uid

        # Fallback: try graphManager root.
        manager = getattr(graph, "graphManager", None)
        find_root = getattr(manager, "findRootGraph", None)
        if callable(find_root):
            try:
                root = find_root()
                return getattr(root, "uid", None)
            except Exception:
                log.debug("Failed to resolve root graph uid", exc_info=True)
        return None
