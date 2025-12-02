from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.application.doc_units.ports import ActiveDocUnitStore
from app.application.pipelines.pipeline_executor import PipelineExecutionResult
from app.application.pipelines.pipeline_service import PipelineService
from app.application.pipelines.use_cases import (
    RunPipelinePreview,
    RunPipelinePreviewRequest,
    SelectPreviewImage,
    SelectPreviewImageRequest,
)
from app.application.project.ports import CurrentProjectStore
from app.domain.doc_units.entities import HierarchyNode
from app.interface_adapters.doc_units.repositories.project_doc_unit_repository import (
    ProjectDocUnitRepository,
)

log = logging.getLogger(__name__)


class PreviewGraphicsView(QGraphicsView):
    """Graphics view that supports zoom and pan for preview images."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._pixmap_item: Optional[QGraphicsPixmapItem] = None
        self._current_zoom = 1.0
        self._min_zoom = 0.1
        self._max_zoom = 8.0
        self._auto_fit_enabled = True
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def set_pixmap(self, pixmap: QPixmap) -> None:
        self._scene.clear()
        self._pixmap_item = QGraphicsPixmapItem(pixmap)
        self._scene.addItem(self._pixmap_item)
        self._scene.setSceneRect(self._pixmap_item.boundingRect())
        self.reset_view()
        self._auto_fit_enabled = True
        self._fit_if_needed()

    def wheelEvent(self, event) -> None:  # noqa: ANN001
        if not self._pixmap_item:
            return
        self._auto_fit_enabled = False
        angle = event.angleDelta().y()
        factor = 1.15 if angle > 0 else 0.85
        self._apply_zoom(factor)

    def fit_to_view(self) -> None:
        if not self._pixmap_item:
            return
        self.resetTransform()
        rect = self._pixmap_item.boundingRect()
        if rect.isNull():
            return
        view_rect = self.viewport().rect()
        if view_rect.width() <= 0 or view_rect.height() <= 0:
            return
        scale_x = view_rect.width() / rect.width()
        scale_y = view_rect.height() / rect.height()
        target = min(scale_x, scale_y)
        self._current_zoom = target
        super().scale(target, target)

    def reset_view(self) -> None:
        self._current_zoom = 1.0
        self.resetTransform()
        if self._pixmap_item:
            self.centerOn(self._pixmap_item)

    def _apply_zoom(self, factor: float) -> None:
        new_zoom = self._current_zoom * factor
        clamped = max(self._min_zoom, min(self._max_zoom, new_zoom))
        factor_to_apply = clamped / self._current_zoom
        self._current_zoom = clamped
        super().scale(factor_to_apply, factor_to_apply)

    def showEvent(self, event) -> None:  # noqa: ANN001
        super().showEvent(event)
        self._fit_if_needed()

    def resizeEvent(self, event) -> None:  # noqa: ANN001
        super().resizeEvent(event)
        self._fit_if_needed()

    def _fit_if_needed(self) -> None:
        if not self._auto_fit_enabled:
            return
        if not self._pixmap_item:
            return
        if self.viewport().width() <= 0 or self.viewport().height() <= 0:
            return
        self.fit_to_view()


class PreviewActions:
    """Orchestrates preview image selection and preview execution for the pipeline tab."""

    def __init__(
        self,
        *,
        parent: QWidget,
        pipeline_service: PipelineService,
        project_store: CurrentProjectStore,
        active_doc_unit_store: ActiveDocUnitStore | None,
        select_preview: SelectPreviewImage,
        run_preview: RunPipelinePreview,
    ) -> None:
        self._parent = parent
        self._service = pipeline_service
        self._project_store = project_store
        self._active_doc_unit_store = active_doc_unit_store
        self._select_preview = select_preview
        self._run_preview_uc = run_preview
        self._parent = parent

    def choose_image(self) -> Optional[Path]:
        """Open the hierarchy picker and persist the selected preview image."""
        active_pipeline = self._service.collection.active
        if not active_pipeline:
            QMessageBox.information(self._parent, "Preview image", "Select a pipeline first.")
            return None

        try:
            unit_name, hierarchy_root = self._load_active_doc_unit()
        except Exception as exc:
            QMessageBox.information(self._parent, "Preview image", str(exc))
            return None

        selected = self._open_picker_dialog(unit_name, hierarchy_root)
        if not selected:
            return None

        try:
            return self._select_preview.execute(SelectPreviewImageRequest(image_path=selected))
        except Exception as exc:  # pragma: no cover - UI feedback path
            QMessageBox.critical(self._parent, "Preview image", str(exc))
            return None

    def run_preview(self) -> None:
        """Run the active pipeline against the chosen preview image and show the result."""
        active_pipeline = self._service.collection.active
        if not active_pipeline:
            QMessageBox.information(self._parent, "Preview", "Select a pipeline first.")
            return

        if not active_pipeline.preview_path:
            selected = self.choose_image()
            if not selected:
                return

        try:
            result = self._run_preview_uc.execute(RunPipelinePreviewRequest())
        except Exception as exc:  # pragma: no cover - UI feedback path
            QMessageBox.critical(self._parent, "Preview", str(exc))
            return

        if result.error:
            message = f"{result.error.code}: {result.error.message}"
            QMessageBox.critical(self._parent, "Preview failed", message)
            return

        self._show_result_dialog(active_pipeline.name, result)

    def _show_result_dialog(self, pipeline_name: str, result: PipelineExecutionResult) -> None:
        dialog = QDialog(self._parent)
        dialog.setWindowTitle("Preview result")
        dialog.setFixedSize(900, 700)

        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"Pipeline: {pipeline_name}"))

        pixmap = self._pixmap_from_output(result.output.get("image"))
        if pixmap and not pixmap.isNull():
            view = PreviewGraphicsView(dialog)
            view.set_pixmap(pixmap)
            layout.addWidget(view, stretch=1)

            controls = QHBoxLayout()
            fit_btn = QPushButton("Fit to window", dialog)
            controls.addWidget(fit_btn)
            controls.addStretch(1)
            layout.addLayout(controls)

            fit_btn.clicked.connect(view.fit_to_view)
        else:
            placeholder = QLabel("Preview output unavailable")
            placeholder.setAlignment(Qt.AlignCenter)
            layout.addWidget(placeholder)

        close_box = QDialogButtonBox(QDialogButtonBox.Close)
        close_box.rejected.connect(dialog.reject)
        close_box.accepted.connect(dialog.accept)
        layout.addWidget(close_box)

        dialog.exec()

    def _open_picker_dialog(self, unit_name: str, root: HierarchyNode) -> Optional[Path]:
        dialog = QDialog(self._parent)
        dialog.setWindowTitle("Choose preview image")
        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel(f"Active doc unit: {unit_name}"))
        tree = QTreeWidget()
        tree.setHeaderHidden(True)
        layout.addWidget(tree)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_button = buttons.button(QDialogButtonBox.Ok)
        if ok_button:
            ok_button.setEnabled(False)
        layout.addWidget(buttons)

        def _add_node(node: HierarchyNode, parent_item: QTreeWidgetItem | None) -> None:
            item = QTreeWidgetItem([node.name])
            if parent_item:
                parent_item.addChild(item)
            else:
                tree.addTopLevelItem(item)
            image_path = self._resolve_image_path(node) if node.node_type == HierarchyNode.IMAGE_TYPE else None
            item.setData(0, Qt.UserRole, image_path)
            for child in node.children:
                _add_node(child, item)

        _add_node(root, None)
        tree.expandAll()

        def _on_selection_changed() -> None:
            item = tree.currentItem()
            selected_path = item.data(0, Qt.UserRole) if item else None
            if ok_button:
                ok_button.setEnabled(bool(selected_path and Path(selected_path).exists()))

        tree.currentItemChanged.connect(lambda _c, _p: _on_selection_changed())

        selected_path: Optional[Path] = None

        def _accept() -> None:
            nonlocal selected_path
            item = tree.currentItem()
            data = item.data(0, Qt.UserRole) if item else None
            selected_path = Path(data) if data else None
            dialog.accept()

        def _reject() -> None:
            dialog.reject()

        buttons.accepted.connect(_accept)
        buttons.rejected.connect(_reject)

        if dialog.exec() == QDialog.Accepted:
            return selected_path
        return None

    def set_parent(self, parent: QWidget) -> None:
        self._parent = parent

    def _load_active_doc_unit(self) -> tuple[str, HierarchyNode]:
        if not self._active_doc_unit_store:
            raise RuntimeError("Doc unit selection is unavailable.")

        unit_id = self._active_doc_unit_store.get()
        if not unit_id:
            raise RuntimeError("Select a doc unit to choose a preview image.")

        repository = ProjectDocUnitRepository(self._project_store)
        doc_unit = repository.get_unit(unit_id)
        if not doc_unit:
            raise RuntimeError(f"Doc unit '{unit_id.value}' not found.")

        return doc_unit.name.value, doc_unit.hierarchy

    def _resolve_image_path(self, node: HierarchyNode) -> Optional[str]:
        if not node.pointer or not node.pointer.path_hint:
            return None
        project_data = self._project_store.get_data()
        project_root = Path(project_data.metadata.get("project_root_path")) if project_data else None
        candidate = Path(node.pointer.path_hint)
        if project_root and not candidate.is_absolute():
            candidate = project_root / candidate
        if candidate.exists():
            return str(candidate)
        return None

    @staticmethod
    def _pixmap_from_output(image_obj) -> Optional[QPixmap]:
        if isinstance(image_obj, (str, Path)):
            pixmap = QPixmap(str(image_obj))
            return pixmap if not pixmap.isNull() else None
        if isinstance(image_obj, (bytes, bytearray, memoryview)):
            pixmap = QPixmap()
            if pixmap.loadFromData(bytes(image_obj)):
                return pixmap
            return None
        if isinstance(image_obj, (list, tuple)):
            try:
                if all(isinstance(v, int) and 0 <= v <= 255 for v in image_obj):
                    data = bytes(image_obj)
                    pixmap = QPixmap()
                    if pixmap.loadFromData(data):
                        return pixmap
            except Exception:
                log.debug("Failed to build pixmap from list output", exc_info=True)
        try:
            import numpy as np  # type: ignore
            import cv2  # type: ignore

            if "numpy" in str(type(image_obj)).lower():
                arr = np.asarray(image_obj)
                success, buf = cv2.imencode(".png", arr)
                if success:
                    pixmap = QPixmap()
                    if pixmap.loadFromData(buf.tobytes()):
                        return pixmap
        except Exception:
            log.debug("Failed to build pixmap from numpy output", exc_info=True)
        return None
