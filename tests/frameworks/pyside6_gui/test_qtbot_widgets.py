from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QInputDialog

from app.composition_root.gui_factories.doc_units.tab_factory import (
    build_doc_unit_tab,
)
from app.domain.project.services import new_project
from app.frameworks.pyside6_gui.main_window import MainWindow
from app.interface_adapters.project.repositories.mem_current_project_store import (
    MemCurrentProjectStore,
)
from app.interface_adapters.project.util.idgen_uuid import UUIDGenerator
from app.third_party.PyFlow.PyFlow.Packages.MangaTranslator.manga_translator_api.gui.pipelines_list.pipelines_list import (
    PipelinesList,
)


_VISUAL_WAIT_MS = 1000


class _StubPresenter:
    def attach_view(self, _view) -> None:
        return None


class _StubController:
    def on_new_project_triggered(self) -> None:
        return None

    def on_save_project_triggered(self) -> None:
        return None

    def on_save_project_as_triggered(self) -> None:
        return None

    def on_load_project_triggered(self) -> None:
        return None


def test_pipelines_list_selects_item(qtbot) -> None:
    widget = PipelinesList()
    qtbot.addWidget(widget)
    widget.show()
    qtbot.waitExposed(widget)
    qtbot.wait(_VISUAL_WAIT_MS)

    list_widget = widget.pipelines_list_listWidget
    list_widget.addItem("First")
    list_widget.addItem("Second")

    item = list_widget.item(1)
    rect = list_widget.visualItemRect(item)
    qtbot.mouseClick(list_widget.viewport(), Qt.LeftButton, pos=rect.center())

    current_item = list_widget.currentItem()
    assert current_item is not None
    assert current_item.text() == "Second"
    qtbot.wait(_VISUAL_WAIT_MS)


def test_main_window_file_menu_actions_exist(qtbot) -> None:
    window = MainWindow(_StubPresenter(), _StubController())
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    qtbot.wait(_VISUAL_WAIT_MS)

    file_action = next(action for action in window.menuBar().actions() if action.text() == "File")
    file_menu = file_action.menu()
    assert file_menu is not None

    action_texts = {action.text() for action in file_menu.actions()}
    assert {"New Project", "Save", "Save As...", "Load"}.issubset(action_texts)
    qtbot.wait(_VISUAL_WAIT_MS)


def test_doc_units_new_unit_increments_list(qtbot, monkeypatch) -> None:
    project_store = MemCurrentProjectStore()
    project_store.set_data(new_project("project-id", "Demo"))

    bundle = build_doc_unit_tab(
        project_store=project_store,
        id_generator=UUIDGenerator(),
    )
    tab = bundle.tab
    qtbot.addWidget(tab)
    tab.show()
    qtbot.waitExposed(tab)
    qtbot.wait(_VISUAL_WAIT_MS)
    tab.on_project_available()

    monkeypatch.setattr(QInputDialog, "getText", lambda *_a, **_k: ("Unit 1", True))

    list_widget = tab.ui.unitListWidget
    assert list_widget.count() == 0
    qtbot.mouseClick(tab.ui.newUnitButton, Qt.LeftButton)
    qtbot.waitUntil(lambda: list_widget.count() == 1)
    qtbot.wait(_VISUAL_WAIT_MS)
