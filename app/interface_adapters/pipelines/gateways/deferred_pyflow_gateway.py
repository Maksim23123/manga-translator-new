from __future__ import annotations

import logging
from typing import Callable, Optional

from app.application.pipelines.ports import PyFlowGateway

log = logging.getLogger(__name__)


class DeferredPyFlowGateway(PyFlowGateway):
    """Proxy that defers to an attached PyFlow gateway once available."""

    def __init__(self, delegate: Optional[PyFlowGateway] = None) -> None:
        self._delegate = delegate
        self._dirty_callbacks: list[Callable[[bool], None]] = []

    def set_delegate(self, delegate: PyFlowGateway) -> None:
        self._delegate = delegate
        for callback in self._dirty_callbacks:
            try:
                self._delegate.on_dirty_changed(callback)
            except Exception:
                log.exception("Failed to reattach dirty callback to delegate")

    def load_graph(self, graph_path) -> None:
        if self._delegate:
            self._delegate.load_graph(graph_path)
        else:
            log.debug("load_graph called before delegate attached")

    def save_graph(self, target_path) -> None:
        if self._delegate:
            self._delegate.save_graph(target_path)
        else:
            log.debug("save_graph called before delegate attached")

    def new_blank(self) -> None:
        if self._delegate:
            self._delegate.new_blank()
        else:
            log.debug("new_blank called before delegate attached")

    def on_dirty_changed(self, callback: Callable[[bool], None]) -> None:
        self._dirty_callbacks.append(callback)
        if self._delegate:
            self._delegate.on_dirty_changed(callback)
        else:
            log.debug("on_dirty_changed called before delegate attached; will reattach when ready")
