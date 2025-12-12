from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Callable, Iterable, Optional, Tuple

from app.application.doc_units.events import (
    ActiveDocUnitChanged,
    HierarchyUpdated,
    ProjectDirtyStateChanged,
)
from app.application.doc_units.ports import (
    ActiveDocUnitStore,
    DocUnitHierarchyRepository,
    MediaStore,
)
from app.application.page_editor.dto import ImageSelection, TranslationSummary
from app.application.pipelines.pipeline_service import PipelineService
from app.domain.doc_units.entities import HierarchyNode
from app.domain.doc_units.value_objects import DocUnitId


class PageEditorService:
    """Coordinates Page Editor selections, pipeline assignments, and translations."""

    PIPELINE_KEY = "pipeline_id"
    SIGNATURE_KEY = "last_pipeline_signature"

    def __init__(
        self,
        repository: DocUnitHierarchyRepository,
        active_store: ActiveDocUnitStore,
        media_store: MediaStore,
        pipeline_service: PipelineService,
        doc_unit_events,
    ) -> None:
        self._repository = repository
        self._active_store = active_store
        self._media_store = media_store
        self._pipeline_service = pipeline_service
        self._events = doc_unit_events
        current_unit = self._active_store.get()
        self._active_unit_id: Optional[str] = current_unit.value if current_unit else None

        self._events.subscribe(ActiveDocUnitChanged, self._on_active_unit_changed)

    # region Queries
    def list_pipelines(self) -> list[str]:
        return [p.name for p in self._pipeline_service.collection.list()]

    def resolve_selection(self, selected_ids: Iterable[str]) -> list[ImageSelection]:
        """Resolve selected nodes (folders/images) into ordered images."""
        unit_id = self._require_active_unit()
        root = self._repository.get_hierarchy(unit_id)
        selection_set = set(selected_ids)
        return self._resolve_images(root, selection_set)

    def resolve_all_images(self) -> list[ImageSelection]:
        """Resolve all images for the active doc unit in hierarchy order."""
        unit_id = self._require_active_unit()
        root = self._repository.get_hierarchy(unit_id)
        return self._resolve_images(root, None)

    # endregion

    # region Commands
    def apply_pipeline(self, selected_ids: Iterable[str], pipeline_id: str) -> list[str]:
        """Assign a pipeline to selected images (and descendant images)."""
        unit_id = self._require_active_unit()
        if not pipeline_id:
            raise ValueError("Pipeline id must not be empty.")
        if not self._pipeline_service.collection.get(pipeline_id):
            raise KeyError(f"Pipeline '{pipeline_id}' not found.")

        root = self._repository.get_hierarchy(unit_id)
        selection_set = set(selected_ids)

        def _updater(node: HierarchyNode) -> Optional[dict]:
            current_pipeline = node.settings.get(self.PIPELINE_KEY)
            current_sig = node.settings.get(self.SIGNATURE_KEY)
            updated = dict(node.settings)
            updated[self.PIPELINE_KEY] = pipeline_id
            # Clear signature so dirty detection treats as needing re-translation.
            updated[self.SIGNATURE_KEY] = None
            if updated == node.settings and current_pipeline == pipeline_id and current_sig is None:
                return None
            return updated

        new_root, changed_ids, changed = self._update_hierarchy(
            root,
            selection_set,
            _updater,
            include_descendants=True,
        )
        if not changed:
            return []

        self._repository.save_hierarchy(unit_id, new_root)
        self._events.publish(
            HierarchyUpdated(
                unit_id=unit_id.value,
                root=new_root,
                changed_node_ids=changed_ids,
            )
        )
        self._events.publish(ProjectDirtyStateChanged(True))
        return changed_ids

    def translate_all(self) -> TranslationSummary:
        images = self.resolve_all_images()
        return self._translate_images(images, dirty_only=False)

    def translate_selected(self, selected_ids: Iterable[str]) -> TranslationSummary:
        images = self.resolve_selection(selected_ids)
        return self._translate_images(images, dirty_only=False)

    def translate_dirty(self) -> TranslationSummary:
        images = self.resolve_all_images()
        return self._translate_images(images, dirty_only=True)

    # endregion

    # region Internal helpers
    def _translate_images(self, images: list[ImageSelection], *, dirty_only: bool) -> TranslationSummary:
        if not images:
            return TranslationSummary(requested=0, translated=0, skipped=[], failures=[])

        grouped: dict[str, list[ImageSelection]] = defaultdict(list)
        skipped: list[str] = []
        for img in images:
            if img.pipeline_id:
                grouped[img.pipeline_id].append(img)
            else:
                skipped.append(img.node_id)

        requested = len(images)
        translated_ids: list[str] = []
        failures: list[str] = []

        for pipeline_id, pipeline_images in grouped.items():
            try:
                signature = self._pipeline_service.build_signature(pipeline_id)
            except Exception as exc:
                failures.append(f"{pipeline_id}: {exc}")
                continue

            targets = pipeline_images
            if dirty_only:
                targets = [
                    img for img in pipeline_images if img.last_pipeline_signature != signature
                ]
            if not targets:
                skipped.extend([img.node_id for img in pipeline_images])
                continue

            image_paths = [img.path for img in targets if img.path and img.path.exists()]
            missing = [img.node_id for img in targets if not img.path or not img.path.exists()]
            if missing:
                skipped.extend(missing)
            if not image_paths:
                continue

            try:
                result = self._pipeline_service.run_pipeline(pipeline_id, image_paths)
                if result.error:
                    failures.append(f"{pipeline_id}: {result.error.code} {result.error.message}")
                    continue
            except Exception as exc:
                failures.append(f"{pipeline_id}: {exc}")
                continue

            translated_ids.extend([img.node_id for img in targets])
            # Update signatures immediately for the nodes we attempted.
            self._update_translation_signatures(target_ids=[img.node_id for img in targets], signature=signature)

        return TranslationSummary(
            requested=requested,
            translated=len(translated_ids),
            skipped=skipped,
            failures=failures,
        )

    def _resolve_images(
        self,
        root: HierarchyNode,
        selection: Optional[set[str]],
    ) -> list[ImageSelection]:
        images: list[ImageSelection] = []
        for node in self._iter_ordered_images(root, selection):
            path = self._resolve_image_path(node)
            images.append(
                ImageSelection(
                    node_id=node.node_id,
                    path=path,
                    pipeline_id=node.settings.get(self.PIPELINE_KEY),
                    last_pipeline_signature=node.settings.get(self.SIGNATURE_KEY),
                )
            )
        return images

    def _iter_ordered_images(
        self,
        node: HierarchyNode,
        selection: Optional[set[str]],
        ancestor_selected: bool = False,
    ):
        is_selected = ancestor_selected or selection is None or node.node_id in selection
        if node.node_type == HierarchyNode.IMAGE_TYPE:
            if is_selected:
                yield node
        for child in node.children:
            yield from self._iter_ordered_images(
                child,
                selection,
                ancestor_selected=is_selected if node.node_type == HierarchyNode.FOLDER_TYPE else ancestor_selected,
            )

    def _resolve_image_path(self, node: HierarchyNode) -> Optional[Path]:
        if not node.pointer:
            return None
        try:
            resolved = self._media_store.resolve_path(node.pointer)
            return Path(resolved)
        except Exception:
            return None

    def _update_translation_signatures(self, target_ids: Iterable[str], signature: str) -> None:
        unit_id = self._require_active_unit()
        root = self._repository.get_hierarchy(unit_id)
        target_set = set(target_ids)

        def _updater(node: HierarchyNode) -> Optional[dict]:
            current = node.settings.get(self.SIGNATURE_KEY)
            if current == signature:
                return None
            updated = dict(node.settings)
            updated[self.SIGNATURE_KEY] = signature
            return updated

        new_root, changed_ids, changed = self._update_hierarchy(
            root,
            target_set,
            _updater,
            include_descendants=False,
        )
        if not changed:
            return

        self._repository.save_hierarchy(unit_id, new_root)
        self._events.publish(
            HierarchyUpdated(
                unit_id=unit_id.value,
                root=new_root,
                changed_node_ids=changed_ids,
            )
        )
        self._events.publish(ProjectDirtyStateChanged(True))

    def _update_hierarchy(
        self,
        node: HierarchyNode,
        selected_ids: Optional[set[str]],
        updater: Callable[[HierarchyNode], Optional[dict]],
        *,
        include_descendants: bool,
        ancestor_selected: bool = False,
    ) -> Tuple[HierarchyNode, list[str], bool]:
        is_selected = ancestor_selected or selected_ids is None or node.node_id in selected_ids
        changed_ids: list[str] = []
        any_changed = False
        new_children: list[HierarchyNode] = []

        for child in node.children:
            child_new, child_changed_ids, child_changed = self._update_hierarchy(
                child,
                selected_ids,
                updater,
                include_descendants=include_descendants,
                ancestor_selected=is_selected if include_descendants else False,
            )
            new_children.append(child_new)
            if child_changed:
                any_changed = True
            changed_ids.extend(child_changed_ids)

        new_settings = node.settings
        node_changed = False
        if node.node_type == HierarchyNode.IMAGE_TYPE and is_selected:
            maybe_new_settings = updater(node)
            if maybe_new_settings is not None and maybe_new_settings != node.settings:
                new_settings = maybe_new_settings
                node_changed = True
                changed_ids.append(node.node_id)

        if node_changed or any_changed:
            any_changed = True
            new_node = HierarchyNode(
                node_id=node.node_id,
                name=node.name,
                node_type=node.node_type,
                settings=new_settings,
                pointer=node.pointer,
                children=new_children,
            )
            return new_node, changed_ids, any_changed

        return node, changed_ids, False

    def _require_active_unit(self) -> DocUnitId:
        unit = self._active_store.get()
        if unit is None:
            raise RuntimeError("No active doc unit.")
        return unit

    def _on_active_unit_changed(self, event: ActiveDocUnitChanged) -> None:
        self._active_unit_id = event.unit_id

    # endregion
