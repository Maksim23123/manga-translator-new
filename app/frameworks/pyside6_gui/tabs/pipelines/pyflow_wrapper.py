from __future__ import annotations

import logging
from typing import Callable, Dict, List, Optional, cast

import sys
from pathlib import Path

_PYFLOW_PACKAGE_DIR = Path(__file__).resolve().parents[4] / "third_party" / "PyFlow"
if _PYFLOW_PACKAGE_DIR.exists():
    pyflow_path = str(_PYFLOW_PACKAGE_DIR)
    if pyflow_path not in sys.path:
        sys.path.insert(0, pyflow_path)

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QMenu, QVBoxLayout, QWidget

from app.interface_adapters.pipelines.controllers.pyflow_controller import PyFlowController
from app.interface_adapters.pipelines.controllers.pipeline_list_controller import PipelineListController
from app.interface_adapters.pipelines.controllers.pipeline_properties_controller import (
    PipelinePropertiesController,
)
from app.interface_adapters.pipelines.presenters.pipeline_list_presenter import PipelineListPresenter
from app.interface_adapters.pipelines.presenters.pipeline_properties_presenter import (
    PipelinePropertiesPresenter,
)
from app.interface_adapters.pipelines.presenters.pyflow_presenter import PyFlowPresenter
from app.interface_adapters.pipelines.views.PyFlowView import PyFlowView
from app.third_party.PyFlow.PyFlow.App import PyFlow
from app.third_party.PyFlow.PyFlow.UI.Tool.Tool import DockTool, ShelfTool
from app.third_party.PyFlow.PyFlow.Packages.MangaTranslator.Tools.PipelinePropertiesDockTool import (
    PipelinePropertiesDockTool,
)
from app.third_party.PyFlow.PyFlow.Packages.MangaTranslator.Tools.PipelinesListDockTool import (
    PipelinesListDockTool,
)
from app.frameworks.pyside6_gui.tabs.pipelines.dock_adapters import (
    PipelinePropertiesDockAdapter,
    PipelinesListDockAdapter,
)

# NOTE: Keep imports of MangaTranslator-specific shelf tools in place even if they
# are not fully wired yet. They will be used once pipelines lifecycle ports land.
try:
    from app.third_party.PyFlow.PyFlow.Packages.MangaTranslator.Tools.InformationShelfTool import InformationShelfTool  # noqa: F401
    from app.third_party.PyFlow.PyFlow.Packages.MangaTranslator.Tools.PluginsShelfTool import PluginsShelfTool  # noqa: F401
    from app.third_party.PyFlow.PyFlow.Packages.MangaTranslator.Tools.PreferencesShelfTool import PreferencesShelfTool  # noqa: F401
    from app.third_party.PyFlow.PyFlow.Packages.MangaTranslator.Tools.PreviewShelfTool import PreviewShelfTool  # noqa: F401
    from app.third_party.PyFlow.PyFlow.Packages.MangaTranslator.Tools.ToolsMenuShelfTool import ToolsMenuShelfTool  # noqa: F401
except ModuleNotFoundError:
    # Legacy tools rely on auxiliary packages (e.g., icons). They will be re-enabled once
    # the dependencies migrate into the layered architecture.
    InformationShelfTool = None  # type: ignore[assignment]
    PluginsShelfTool = None  # type: ignore[assignment]
    PreferencesShelfTool = None  # type: ignore[assignment]
    PreviewShelfTool = None  # type: ignore[assignment]
    ToolsMenuShelfTool = None  # type: ignore[assignment]


log = logging.getLogger(__name__)


class PyFlowWrapper(QWidget, QObject):
    """Minimal wrapper that embeds a PyFlow main window inside a QWidget.

    Mirrors the legacy integration so later pipeline orchestration code can slot in.
    """

    SOFTWARE = "manga-translator"
    modifiedChanged = Signal(bool)

    def __init__(
        self,
        presenter: PyFlowPresenter,
        controller: PyFlowController,
        parent: Optional[QWidget] = None,
        *,
        hide_menu_bar: bool = True,
        pyflow_instance: Optional[PyFlow] = None,
        pipeline_list_controller: Optional[PipelineListController] = None,
        pipeline_list_presenter: Optional[PipelineListPresenter] = None,
        pipeline_properties_controller: Optional[PipelinePropertiesController] = None,
        pipeline_properties_presenter: Optional[PipelinePropertiesPresenter] = None,
    ) -> None:
        super().__init__(parent)

        self._presenter = presenter
        self._controller = controller
        self._pipeline_list_controller = pipeline_list_controller
        self._pipeline_list_presenter = pipeline_list_presenter
        self._pipeline_properties_controller = pipeline_properties_controller
        self._pipeline_properties_presenter = pipeline_properties_presenter
        self._shelf_tools: Dict[str, Optional[ShelfTool]] = {}
        self._dock_tools: Dict[str, DockTool] = {}
        self._dock_adapters: Dict[str, object] = {}
        self._shelf_tool_slots: List[Callable[..., None]] = []
        self._menu_cache: Dict[str, QMenu] = {}
        self._hide_menu_bar = hide_menu_bar
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._pyflow_instance = self._setup_pyflow(pyflow_instance)
        self._layout.addWidget(self._pyflow_instance)
        self._cache_shelf_tools(self._pyflow_instance)
        self._cache_dock_tools(self._pyflow_instance)
        self._connect_shelf_tools()
        self._wire_dock_tools()
        self._presenter.attach_view(cast(PyFlowView, self))

    @property
    def pyflow_instance(self) -> PyFlow:
        return self._pyflow_instance

    def _setup_pyflow(self, instance: Optional[PyFlow]) -> PyFlow:
        pyflow = instance or PyFlow.instance(software=self.SOFTWARE)
        pyflow.setParent(self)

        self._remove_empty_shelf_tools(pyflow)
        self._wrap_modified_property(pyflow)

        # Legacy UI hides the menu bar inside the tab container.
        if self._hide_menu_bar:
            menu_bar_fn = getattr(pyflow, "getMenuBar", None)
            if callable(menu_bar_fn):
                try:
                    menu_bar = menu_bar_fn()
                    menu_bar.hide()
                except Exception:
                    # PyFlow internals are noisy; skip failures until full orchestration lands.
                    pass

        return pyflow

    def _remove_empty_shelf_tools(self, instance: PyFlow) -> None:
        """Drop placeholder ShelfTool entries to match the legacy setup."""
        shelf_tool_stub = ShelfTool()

        registered_tools_fn = getattr(instance, "getRegisteredTools", None)
        registered_tools = list(registered_tools_fn()) if callable(registered_tools_fn) else []
        empty_tools = [
            tool for tool in registered_tools if type(tool).__name__ == type(shelf_tool_stub).__name__
        ]
        for tool in empty_tools:
            try:
                instance.unregisterToolInstance(tool)
            except Exception:
                pass

        toolbar_fn = getattr(instance, "getToolbar", None)
        if callable(toolbar_fn):
            toolbar = toolbar_fn()
            actions = list(toolbar.actions())
            empty_actions = [action for action in actions if action.text() == shelf_tool_stub.name()]
            for action in empty_actions:
                toolbar.removeAction(action)

    def _cache_shelf_tools(self, instance: PyFlow) -> None:
        """Cache MangaTranslator shelf tool instances for signal wiring."""
        registered_tools_fn = getattr(instance, "getRegisteredTools", None)
        tools = list(registered_tools_fn()) if callable(registered_tools_fn) else []

        def _match(cls):
            if cls is None:
                return None
            for tool in tools:
                if type(tool).__name__ == cls.__name__:
                    return tool
            return None

        self._shelf_tools = {
            "preview": _match(PreviewShelfTool),
            "preferences": _match(PreferencesShelfTool),
            "tools_menu": _match(ToolsMenuShelfTool),
            "plugins": _match(PluginsShelfTool),
            "information": _match(InformationShelfTool),
        }

    def _cache_dock_tools(self, instance: PyFlow) -> None:
        """Cache dock tool instances (e.g., pipeline list, properties)."""
        registered_tools_fn = getattr(instance, "getRegisteredTools", None)
        tools = list(registered_tools_fn()) if callable(registered_tools_fn) else []
        self._dock_tools = {}
        for tool in tools:
            if isinstance(tool, DockTool):
                self._dock_tools[type(tool).__name__] = tool

    def _connect_shelf_tools(self) -> None:
        """Wire shelf tools into controller callbacks."""
        if not self._controller:
            return
        self._shelf_tool_slots.clear()

        wiring: list[tuple[str, Callable[[], None]]] = [
            ("tools_menu", self._controller.open_tools_menu),
            ("plugins", self._controller.open_plugins_menu),
            ("information", self._controller.open_information_menu),
            ("preferences", self._controller.open_preferences),
        ]

        for key, callback in wiring:
            shelf_tool = self._shelf_tools.get(key)
            if not shelf_tool:
                continue
            slot = self._make_tool_slot(callback)
            shelf_tool.triggered.connect(slot)
            self._shelf_tool_slots.append(slot)

    @staticmethod
    def _make_tool_slot(callback: Callable[[], None]):
        def _slot(*_args, **_kwargs):
            callback()

        return _slot

    def _wrap_modified_property(self, instance: PyFlow) -> None:
        """Emit the modifiedChanged signal whenever the PyFlow modified flag flips."""
        pyflow_cls = type(instance)
        modified_prop = getattr(pyflow_cls, "modified", None)
        if not isinstance(modified_prop, property) or modified_prop.fset is None:
            return

        original_setter = modified_prop.fset

        def wrapper(inst: PyFlow, value: bool) -> None:
            previous = modified_prop.fget(inst) if modified_prop.fget else inst.modified
            original_setter(inst, value)
            if previous != value:
                self.modifiedChanged.emit(value)

        pyflow_cls.modified = modified_prop.setter(wrapper)  # type: ignore[assignment]

    def get_shelf_tools(self) -> Dict[str, Optional[ShelfTool]]:
        """Expose cached shelf tool instances for inspection/testing."""
        return dict(self._shelf_tools)

    def get_dock_tools(self) -> Dict[str, DockTool]:
        """Expose cached dock tool instances for wiring."""
        return dict(self._dock_tools)

    def _wire_dock_tools(self) -> None:
        """Attach controllers/presenters to PyFlow dock tools if provided."""
        self._dock_adapters.clear()
        self._wire_pipelines_list_dock()
        self._wire_pipeline_properties_dock()

    def _wire_pipelines_list_dock(self) -> None:
        if not (self._pipeline_list_controller and self._pipeline_list_presenter):
            return
        dock = self._resolve_manga_dock_tool(
            class_name=PipelinesListDockTool.__name__, tool_name=PipelinesListDockTool.name()
        )
        if not dock:
            log.debug("PipelinesListDockTool not available for wiring")
            return

        adapter = PipelinesListDockAdapter(
            cast(PipelinesListDockTool, dock),
            controller=self._pipeline_list_controller,
            presenter=self._pipeline_list_presenter,
        )
        self._dock_adapters["pipelines_list"] = adapter

    def _wire_pipeline_properties_dock(self) -> None:
        if not (self._pipeline_properties_controller and self._pipeline_properties_presenter):
            return
        dock = self._resolve_manga_dock_tool(
            class_name=PipelinePropertiesDockTool.__name__,
            tool_name=PipelinePropertiesDockTool.name(),
        )
        if not dock:
            log.debug("PipelinePropertiesDockTool not available for wiring")
            return

        adapter = PipelinePropertiesDockAdapter(
            cast(PipelinePropertiesDockTool, dock),
            controller=self._pipeline_properties_controller,
            presenter=self._pipeline_properties_presenter,
        )
        self._dock_adapters["pipeline_properties"] = adapter

    def _resolve_manga_dock_tool(self, *, class_name: str, tool_name: str) -> Optional[DockTool]:
        dock = self._dock_tools.get(class_name)
        if dock:
            return dock

        invoke = getattr(self._pyflow_instance, "invokeDockToolByName", None)
        if callable(invoke):
            try:
                dock = invoke("MangaTranslator", tool_name)
                if dock:
                    self._dock_tools[class_name] = dock
                    return dock
            except Exception:
                log.exception("Failed to invoke dock tool '%s'", tool_name)

        return None

    # region PyFlowView implementation
    def show_menu(self, menu_title: str) -> None:
        menu = self._resolve_menu(menu_title)
        if menu:
            menu.exec(QCursor.pos())
        else:
            log.debug("Requested menu '%s' is not available", menu_title)

    def show_preferences(self) -> None:
        try:
            self._pyflow_instance.showPreferencesWindow()
        except Exception as exc:  # pragma: no cover - depends on PyFlow internals
            log.exception("Failed to open PyFlow preferences window: %s", exc)

    # endregion

    # region PyFlowGateway implementation
    def load_graph(self, graph_path: Path) -> None:
        try:
            self._pyflow_instance.loadFromFile(str(graph_path))
        except Exception as exc:
            log.exception("Failed to load graph '%s': %s", graph_path, exc)

    def save_graph(self, target_path: Path) -> None:
        try:
            self._pyflow_instance.currentFileName = str(target_path)
            self._pyflow_instance.save(False)
        except Exception as exc:
            log.exception("Failed to save graph to '%s': %s", target_path, exc)

    def new_blank(self) -> None:
        try:
            self._pyflow_instance.newFile()
        except Exception as exc:
            log.exception("Failed to create a blank PyFlow graph: %s", exc)

    def on_dirty_changed(self, callback: Callable[[bool], None]) -> None:
        self.modifiedChanged.connect(callback)

    # endregion

    def _resolve_menu(self, menu_title: str) -> Optional[QMenu]:
        if menu_title in self._menu_cache and self._menu_cache[menu_title]:
            return self._menu_cache[menu_title]

        menu = self._find_menu(menu_title)
        if menu:
            self._menu_cache[menu_title] = menu
        return menu

    def _find_menu(self, menu_title: str) -> Optional[QMenu]:
        get_menu_bar = getattr(self._pyflow_instance, "getMenuBar", None)
        if not callable(get_menu_bar):
            log.warning("PyFlow instance does not expose getMenuBar(); menu '%s' unavailable", menu_title)
            return None

        menu_bar = get_menu_bar()
        for child in menu_bar.findChildren(QMenu):
            if child.title() == menu_title:
                return child

        log.warning("Menu '%s' not found in PyFlow instance", menu_title)
        return None
