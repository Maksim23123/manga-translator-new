from __future__ import annotations

from types import SimpleNamespace

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QInputDialog, QTabWidget

from app.composition_root.gui_factories.main_window_factory import build_main_window
from app.frameworks.pyside6_gui.project.qt_project_settings_store import (
    QtProjectSettingsStore,
)
from app.interface_adapters.project.repositories.fs_project_repository import (
    FsProjectRepository,
)
from app.interface_adapters.project.util.fs_names import safe_folder_name
from app.frameworks.pyside6_gui.tabs.tab import Tab


_VISUAL_WAIT_MS = 1000


def _noop(*_args, **_kwargs) -> None:
    return None


class _StubGraphEditorTab(Tab):
    _default_tab_name = "Graph Editor"

    def __init__(self) -> None:
        super().__init__(None)
        self.set_tab_name(self._default_tab_name)

    def on_project_available(self) -> None:
        return None


class _StubPipelineCollection:
    def list(self):
        return []

    def get(self, _name):
        return None

    @property
    def active(self):
        return None


class _StubPipelineService:
    def __init__(self) -> None:
        self.collection = _StubPipelineCollection()

    def build_signature(self, _pipeline_name: str) -> str:
        return "stub"

    def run_pipeline(self, *_args, **_kwargs):
        raise RuntimeError("Pipeline execution is not configured in tests.")


class _StubEventBus:
    def subscribe(self, *_args, **_kwargs) -> None:
        return None

    def publish(self, *_args, **_kwargs) -> None:
        return None


@pytest.fixture(autouse=True)
def _stub_graph_editor(monkeypatch):
    import app.composition_root.gui_factories.main_window_factory as main_window_factory

    def _build_stub_graph_editor_tab(*_args, **_kwargs):
        return SimpleNamespace(
            tab=_StubGraphEditorTab(),
            service=_StubPipelineService(),
            event_bus=_StubEventBus(),
            finalize_pipelines=None,
        )

    monkeypatch.setattr(main_window_factory, "build_graph_editor_tab", _build_stub_graph_editor_tab)


def test_main_window_e2e_new_project(qtbot, monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(QtProjectSettingsStore, "get_last_project_path", lambda _self: None)
    monkeypatch.setattr(QtProjectSettingsStore, "set_last_project_path", _noop)
    monkeypatch.setattr(QtProjectSettingsStore, "clear_last_project_path", _noop)
    monkeypatch.setattr(QInputDialog, "getText", lambda *_a, **_k: ("Demo", True))
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *_a, **_k: "")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *_a, **_k: ("", ""))

    window = build_main_window()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    qtbot.wait(_VISUAL_WAIT_MS)

    tab_widget = window.centralWidget()
    assert isinstance(tab_widget, QTabWidget)
    assert tab_widget.count() >= 3

    file_menu = next(action for action in window.menuBar().actions() if action.text() == "File").menu()
    new_project_action = next(action for action in file_menu.actions() if action.text() == "New Project")
    new_project_action.trigger()

    qtbot.waitUntil(lambda: "Demo" in window.windowTitle())
    qtbot.wait(_VISUAL_WAIT_MS)


def test_main_window_e2e_tabs_load(qtbot, monkeypatch) -> None:
    monkeypatch.setattr(QtProjectSettingsStore, "get_last_project_path", lambda _self: None)
    monkeypatch.setattr(QtProjectSettingsStore, "set_last_project_path", _noop)
    monkeypatch.setattr(QtProjectSettingsStore, "clear_last_project_path", _noop)

    window = build_main_window()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    qtbot.wait(_VISUAL_WAIT_MS)

    tab_widget = window.centralWidget()
    assert isinstance(tab_widget, QTabWidget)
    tab_names = [tab_widget.tabText(index) for index in range(tab_widget.count())]
    assert tab_names == ["Doc Units", "Graph Editor", "Page Editor"]
    for index in range(tab_widget.count()):
        assert tab_widget.widget(index) is not None
    qtbot.wait(_VISUAL_WAIT_MS)


def test_main_window_e2e_create_doc_unit_marks_dirty(qtbot, monkeypatch) -> None:
    monkeypatch.setattr(QtProjectSettingsStore, "get_last_project_path", lambda _self: None)
    monkeypatch.setattr(QtProjectSettingsStore, "set_last_project_path", _noop)
    monkeypatch.setattr(QtProjectSettingsStore, "clear_last_project_path", _noop)
    responses = iter([("Demo", True), ("Unit 1", True)])
    monkeypatch.setattr(QInputDialog, "getText", lambda *_a, **_k: next(responses, ("", False)))
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *_a, **_k: "")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *_a, **_k: ("", ""))

    window = build_main_window()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    qtbot.wait(_VISUAL_WAIT_MS)

    file_menu = next(action for action in window.menuBar().actions() if action.text() == "File").menu()
    new_project_action = next(action for action in file_menu.actions() if action.text() == "New Project")
    new_project_action.trigger()

    qtbot.waitUntil(lambda: "Demo" in window.windowTitle())

    tab_widget = window.centralWidget()
    assert isinstance(tab_widget, QTabWidget)
    doc_units_index = next(
        index
        for index in range(tab_widget.count())
        if tab_widget.tabText(index) == "Doc Units"
    )
    tab_widget.setCurrentIndex(doc_units_index)
    doc_units_tab = tab_widget.widget(doc_units_index)

    qtbot.mouseClick(doc_units_tab.ui.newUnitButton, Qt.LeftButton)
    list_widget = doc_units_tab.ui.unitListWidget

    qtbot.waitUntil(lambda: list_widget.count() == 1)
    item_widget = list_widget.itemWidget(list_widget.item(0))
    assert item_widget is not None
    assert item_widget.unit_name_label.text() == "Unit 1"

    qtbot.waitUntil(lambda: window.windowTitle().endswith(" *"))
    qtbot.wait(_VISUAL_WAIT_MS)


def test_main_window_e2e_save_project_clears_dirty(qtbot, monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(QtProjectSettingsStore, "get_last_project_path", lambda _self: None)
    monkeypatch.setattr(QtProjectSettingsStore, "set_last_project_path", _noop)
    monkeypatch.setattr(QtProjectSettingsStore, "clear_last_project_path", _noop)
    responses = iter([("Demo", True), ("Unit 1", True)])
    monkeypatch.setattr(QInputDialog, "getText", lambda *_a, **_k: next(responses, ("", False)))
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *_a, **_k: str(tmp_path))
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *_a, **_k: ("", ""))

    window = build_main_window()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    qtbot.wait(_VISUAL_WAIT_MS)

    file_menu = next(action for action in window.menuBar().actions() if action.text() == "File").menu()
    new_project_action = next(action for action in file_menu.actions() if action.text() == "New Project")
    new_project_action.trigger()

    qtbot.waitUntil(lambda: "Demo" in window.windowTitle())

    tab_widget = window.centralWidget()
    assert isinstance(tab_widget, QTabWidget)
    doc_units_index = next(
        index
        for index in range(tab_widget.count())
        if tab_widget.tabText(index) == "Doc Units"
    )
    tab_widget.setCurrentIndex(doc_units_index)
    doc_units_tab = tab_widget.widget(doc_units_index)

    qtbot.mouseClick(doc_units_tab.ui.newUnitButton, Qt.LeftButton)
    list_widget = doc_units_tab.ui.unitListWidget

    qtbot.waitUntil(lambda: list_widget.count() == 1)
    qtbot.waitUntil(lambda: window.windowTitle().endswith(" *"))

    save_as_action = next(action for action in file_menu.actions() if action.text() == "Save As...")
    save_as_action.trigger()

    meta_path = tmp_path / safe_folder_name("Demo") / FsProjectRepository.PROJECT_META_FILE_NAME
    qtbot.waitUntil(lambda: meta_path.exists())
    qtbot.waitUntil(lambda: not window.windowTitle().endswith(" *"))
    qtbot.wait(_VISUAL_WAIT_MS)
