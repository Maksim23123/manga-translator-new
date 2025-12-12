from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QWheelEvent
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView


class ImageListViewer(QGraphicsView):
    """Displays a vertical stack of images with basic zoom and pan."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._pixmap_items: list[QGraphicsPixmapItem] = []
        self._current_zoom = 1.0
        self._auto_fit_enabled = True

        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def clear_images(self) -> None:
        self._scene.clear()
        self._pixmap_items.clear()
        self._current_zoom = 1.0
        self.resetTransform()

    def set_images(self, images: Iterable[str | Path]) -> None:
        self.clear_images()
        pixmaps = []
        max_width = 0
        for img in images:
            pixmap = QPixmap(str(img))
            if pixmap.isNull():
                continue
            pixmaps.append(pixmap)
            max_width = max(max_width, pixmap.width())

        y_offset = 0
        for pixmap in pixmaps:
            x = (max_width - pixmap.width()) // 2
            item = self._scene.addPixmap(pixmap)
            item.setPos(x, y_offset)
            self._pixmap_items.append(item)
            y_offset += pixmap.height()

        self._fit_if_needed()

    def wheelEvent(self, event: QWheelEvent) -> None:  # noqa: N802
        modifiers = event.modifiers()
        ctrl_pressed = modifiers & Qt.ControlModifier
        meta_pressed = modifiers & Qt.MetaModifier
        if ctrl_pressed or meta_pressed:
            factor = 1.15 if event.angleDelta().y() > 0 else 0.85
            self._apply_zoom(factor)
        else:
            super().wheelEvent(event)

    def resizeEvent(self, event) -> None:  # noqa: ANN001
        super().resizeEvent(event)
        self._fit_if_needed()

    def _apply_zoom(self, factor: float) -> None:
        self._auto_fit_enabled = False
        self._current_zoom *= factor
        self.scale(factor, factor)

    def _fit_if_needed(self) -> None:
        if not self._pixmap_items or not self._auto_fit_enabled:
            return
        rect = self._scene.itemsBoundingRect()
        if rect.isNull():
            return
        self.fitInView(rect, Qt.KeepAspectRatio)
        self._current_zoom = 1.0
