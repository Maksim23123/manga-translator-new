from __future__ import annotations

from typing import Optional

from app.interface_adapters.pipelines.views.PyFlowView import PyFlowView


class PyFlowPresenter:
    """Simple presenter that proxies controller requests into the PyFlow view."""

    def __init__(self) -> None:
        self._view: Optional[PyFlowView] = None

    def attach_view(self, view: PyFlowView) -> None:
        self._view = view

    def detach_view(self) -> None:
        self._view = None

    def show_menu(self, menu_title: str) -> None:
        if self._view:
            self._view.show_menu(menu_title)

    def show_preferences(self) -> None:
        if self._view:
            self._view.show_preferences()
