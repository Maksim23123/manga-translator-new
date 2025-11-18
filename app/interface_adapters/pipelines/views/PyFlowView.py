from __future__ import annotations

from typing import Protocol


class PyFlowView(Protocol):
    """Presentation contract for PyFlow UI surfaces."""

    def show_menu(self, menu_title: str) -> None: ...

    def show_preferences(self) -> None: ...
