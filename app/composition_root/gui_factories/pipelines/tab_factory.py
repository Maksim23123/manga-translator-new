from __future__ import annotations

from dataclasses import dataclass

from app.frameworks.pyside6_gui.tabs.pipelines.graph_editor_tab import GraphEditorTab


@dataclass(slots=True)
class GraphEditorTabBundle:
    tab: GraphEditorTab


def build_graph_editor_tab() -> GraphEditorTabBundle:
    """Constructs the PyFlow-backed graph editor tab."""
    tab = GraphEditorTab()
    return GraphEditorTabBundle(tab=tab)
