from __future__ import annotations

from app.interface_adapters.pipelines.presenters.pyflow_presenter import PyFlowPresenter


class PyFlowController:
    """Routes shelf tool triggers into presenter calls."""

    _TOOLS_MENU = "Tools"
    _PLUGINS_MENU = "Plugins"
    _INFORMATION_MENU = "Help"

    def __init__(self, presenter: PyFlowPresenter) -> None:
        self._presenter = presenter

    def open_tools_menu(self) -> None:
        self._presenter.show_menu(self._TOOLS_MENU)

    def open_plugins_menu(self) -> None:
        self._presenter.show_menu(self._PLUGINS_MENU)

    def open_information_menu(self) -> None:
        self._presenter.show_menu(self._INFORMATION_MENU)

    def open_preferences(self) -> None:
        self._presenter.show_preferences()
