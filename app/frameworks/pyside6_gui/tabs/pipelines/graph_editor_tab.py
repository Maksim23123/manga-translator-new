from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtWidgets import QWidget

from app.frameworks.pyside6_gui.tabs.tab import Tab
from app.interface_adapters.pipelines.controllers.pipeline_list_controller import PipelineListController
from app.interface_adapters.pipelines.controllers.pipeline_properties_controller import (
    PipelinePropertiesController,
)
from app.interface_adapters.pipelines.controllers.pyflow_controller import PyFlowController
from app.interface_adapters.pipelines.presenters.pipeline_list_presenter import PipelineListPresenter
from app.interface_adapters.pipelines.presenters.pipeline_properties_presenter import (
    PipelinePropertiesPresenter,
)
from app.interface_adapters.pipelines.presenters.pyflow_presenter import PyFlowPresenter

from .pyflow_wrapper import PyFlowWrapper


class GraphEditorTab(Tab):
    """Simple PyFlow-hosting tab that mirrors the legacy graph editor embedding."""

    _default_tab_name = "Graph Editor"

    def __init__(
        self,
        presenter: PyFlowPresenter,
        controller: PyFlowController,
        *,
        pipeline_list_controller: Optional[PipelineListController] = None,
        pipeline_list_presenter: Optional[PipelineListPresenter] = None,
        pipeline_properties_controller: Optional[PipelinePropertiesController] = None,
        pipeline_properties_presenter: Optional[PipelinePropertiesPresenter] = None,
        parent: Optional[QWidget] = None,
        project_ready_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__(parent)
        self.set_tab_name(self._default_tab_name)

        self._presenter = presenter
        self._controller = controller
        self._project_ready_callback = project_ready_callback

        # Expose the default PyFlow menu bar for debugging. Toggle back once pipeline
        # orchestration is wired and custom menus land.
        self._pyflow_wrapper = PyFlowWrapper(
            presenter=presenter,
            controller=controller,
            pipeline_list_controller=pipeline_list_controller,
            pipeline_list_presenter=pipeline_list_presenter,
            pipeline_properties_controller=pipeline_properties_controller,
            pipeline_properties_presenter=pipeline_properties_presenter,
            parent=self
        )
        self.setCentralWidget(self._pyflow_wrapper)

        self._pyflow_wrapper.modifiedChanged.connect(self._handle_modified_changed)

    @property
    def pyflow_wrapper(self) -> PyFlowWrapper:
        return self._pyflow_wrapper

    def on_project_available(self) -> None:
        """Project lifecycle hook to wire pipelines to the current project."""
        if self._project_ready_callback:
            try:
                self._project_ready_callback()
            except Exception:
                # Keep UI responsive even if lifecycle setup fails.
                return

    def _handle_modified_changed(self, is_modified: bool) -> None:
        tab_title = f"{self._default_tab_name}*" if is_modified else self._default_tab_name
        self.set_tab_name(tab_title)
