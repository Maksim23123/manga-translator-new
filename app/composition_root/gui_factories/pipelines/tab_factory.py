from __future__ import annotations

from dataclasses import dataclass

from app.frameworks.pyside6_gui.tabs.pipelines.graph_editor_tab import GraphEditorTab
from app.interface_adapters.pipelines.controllers.pyflow_controller import PyFlowController
from app.interface_adapters.pipelines.presenters.pyflow_presenter import PyFlowPresenter


@dataclass(slots=True)
class GraphEditorTabBundle:
    tab: GraphEditorTab
    controller: PyFlowController
    presenter: PyFlowPresenter


def build_graph_editor_tab() -> GraphEditorTabBundle:
    """Constructs the PyFlow-backed graph editor tab."""
    presenter = PyFlowPresenter()
    controller = PyFlowController(presenter)
    tab = GraphEditorTab(presenter=presenter, controller=controller)
    return GraphEditorTabBundle(tab=tab, controller=controller, presenter=presenter)
