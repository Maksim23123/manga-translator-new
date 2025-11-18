from __future__ import annotations

from unittest.mock import Mock

from app.interface_adapters.pipelines.controllers.pyflow_controller import PyFlowController
from app.interface_adapters.pipelines.presenters.pyflow_presenter import PyFlowPresenter
from app.interface_adapters.pipelines.views.PyFlowView import PyFlowView


class _FakeView(PyFlowView):
    def __init__(self) -> None:
        self.menus_shown: list[str] = []
        self.preferences_shown = 0

    def show_menu(self, menu_title: str) -> None:
        self.menus_shown.append(menu_title)

    def show_preferences(self) -> None:
        self.preferences_shown += 1


def test_presenter_forwards_menu_to_view() -> None:
    presenter = PyFlowPresenter()
    view = _FakeView()
    presenter.attach_view(view)

    presenter.show_menu("Tools")

    assert view.menus_shown == ["Tools"]


def test_presenter_forwards_preferences_to_view() -> None:
    presenter = PyFlowPresenter()
    view = _FakeView()
    presenter.attach_view(view)

    presenter.show_preferences()

    assert view.preferences_shown == 1


def test_controller_routes_shelf_actions_to_presenter() -> None:
    presenter = Mock(spec=PyFlowPresenter)
    controller = PyFlowController(presenter)

    controller.open_tools_menu()
    controller.open_plugins_menu()
    controller.open_information_menu()
    controller.open_preferences()

    presenter.show_menu.assert_any_call("Tools")
    presenter.show_menu.assert_any_call("Plugins")
    presenter.show_menu.assert_any_call("Help")
    presenter.show_preferences.assert_called_once_with()
