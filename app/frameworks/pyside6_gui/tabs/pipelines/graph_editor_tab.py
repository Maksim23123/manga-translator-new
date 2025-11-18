from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QWidget

from app.frameworks.pyside6_gui.tabs.tab import Tab
from app.interface_adapters.pipelines.controllers.pyflow_controller import PyFlowController
from app.interface_adapters.pipelines.presenters.pyflow_presenter import PyFlowPresenter

from .pyflow_wrapper import PyFlowWrapper


class GraphEditorTab(Tab):
    """Simple PyFlow-hosting tab that mirrors the legacy graph editor embedding."""

    _default_tab_name = "Graph Editor"

    def __init__(
        self,
        presenter: PyFlowPresenter,
        controller: PyFlowController,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.set_tab_name(self._default_tab_name)

        self._presenter = presenter
        self._controller = controller

        # Expose the default PyFlow menu bar for debugging. Toggle back once pipeline
        # orchestration is wired and custom menus land.
        self._pyflow_wrapper = PyFlowWrapper(
            presenter=presenter,
            controller=controller,
            parent=self,
            hide_menu_bar=False,
        )
        self.setCentralWidget(self._pyflow_wrapper)

        self._pyflow_wrapper.modifiedChanged.connect(self._handle_modified_changed)

    @property
    def pyflow_wrapper(self) -> PyFlowWrapper:
        return self._pyflow_wrapper

    def on_project_available(self) -> None:
        """Placeholder hook for project lifecycle events."""
        # Future implementation will load the active pipeline graph here.
        pass

    def _handle_modified_changed(self, is_modified: bool) -> None:
        tab_title = f"{self._default_tab_name}*" if is_modified else self._default_tab_name
        self.set_tab_name(tab_title)
