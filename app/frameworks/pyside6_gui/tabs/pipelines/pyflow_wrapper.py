from __future__ import annotations

from typing import Optional

import sys
from pathlib import Path

_PYFLOW_PACKAGE_DIR = Path(__file__).resolve().parents[4] / "third_party" / "PyFlow"
if _PYFLOW_PACKAGE_DIR.exists():
    pyflow_path = str(_PYFLOW_PACKAGE_DIR)
    if pyflow_path not in sys.path:
        sys.path.insert(0, pyflow_path)

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget

from PyFlow.App import PyFlow
from PyFlow.UI.Tool.Tool import ShelfTool

# NOTE: Keep imports of MangaTranslator-specific shelf tools in place even if they
# are not fully wired yet. They will be used once pipelines lifecycle ports land.
try:
    from PyFlow.Packages.MangaTranslator.Tools.InformationShelfTool import InformationShelfTool  # noqa: F401
    from PyFlow.Packages.MangaTranslator.Tools.PluginsShelfTool import PluginsShelfTool  # noqa: F401
    from PyFlow.Packages.MangaTranslator.Tools.PreferencesShelfTool import PreferencesShelfTool  # noqa: F401
    from PyFlow.Packages.MangaTranslator.Tools.PreviewShelfTool import PreviewShelfTool  # noqa: F401
    from PyFlow.Packages.MangaTranslator.Tools.ToolsMenuShelfTool import ToolsMenuShelfTool  # noqa: F401
except ModuleNotFoundError:
    # Legacy tools rely on auxiliary packages (e.g., icons). They will be re-enabled once
    # the dependencies migrate into the layered architecture.
    InformationShelfTool = None  # type: ignore[assignment]
    PluginsShelfTool = None  # type: ignore[assignment]
    PreferencesShelfTool = None  # type: ignore[assignment]
    PreviewShelfTool = None  # type: ignore[assignment]
    ToolsMenuShelfTool = None  # type: ignore[assignment]


class PyFlowWrapper(QWidget, QObject):
    """Minimal wrapper that embeds a PyFlow main window inside a QWidget.

    Mirrors the legacy integration so later pipeline orchestration code can slot in.
    """

    SOFTWARE = "manga-translator"
    modifiedChanged = Signal(bool)

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        hide_menu_bar: bool = True,
    ) -> None:
        super().__init__(parent)

        self._hide_menu_bar = hide_menu_bar
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._pyflow_instance = self._setup_pyflow()
        self._layout.addWidget(self._pyflow_instance)

    @property
    def pyflow_instance(self) -> PyFlow:
        return self._pyflow_instance

    def _setup_pyflow(self) -> PyFlow:
        instance = PyFlow.instance(software=self.SOFTWARE)
        instance.setParent(self)

        self._remove_empty_shelf_tools(instance)
        self._wrap_modified_property(instance)

        # Legacy UI hides the menu bar inside the tab container.
        if self._hide_menu_bar:
            menu_bar_fn = getattr(instance, "getMenuBar", None)
            if callable(menu_bar_fn):
                try:
                    menu_bar = menu_bar_fn()
                    menu_bar.hide()
                except Exception:
                    # PyFlow internals are noisy; skip failures until full orchestration lands.
                    pass

        return instance

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
