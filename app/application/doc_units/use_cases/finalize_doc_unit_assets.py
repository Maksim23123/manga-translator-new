from __future__ import annotations

from typing import List, Set, Tuple

from app.application.doc_units.events import HierarchyUpdated
from app.application.doc_units.ports import DocUnitRepository, MediaStore
from app.domain.doc_units.entities import DocUnit, HierarchyNode


class FinalizeDocUnitAssets:
    def __init__(
        self,
        repository: DocUnitRepository,
        media_store: MediaStore,
        events,
    ) -> None:
        self._repository = repository
        self._media_store = media_store
        self._events = events

    def execute(self) -> None:
        units = self._repository.list_units()
        referenced_final_paths: Set[str] = set()

        for unit in units:
            promoted_hierarchy, changed_node_ids, changed, node_references = self._promote_hierarchy(unit.hierarchy)
            referenced_final_paths.update(node_references)
            if not changed:
                continue

            updated = DocUnit(
                unit_id=unit.unit_id,
                name=unit.name,
                created_at=unit.created_at,
                hierarchy=promoted_hierarchy,
                metadata=unit.metadata,
            )
            self._repository.save_unit(updated)

            if changed_node_ids:
                self._events.publish(
                    HierarchyUpdated(
                        unit_id=unit.unit_id.value,
                        root=promoted_hierarchy,
                        changed_node_ids=list(dict.fromkeys(changed_node_ids)),
                    )
                )

        self._media_store.cleanup_temp()

        existing_assets = set(self._media_store.list_final_assets())
        orphaned = existing_assets - referenced_final_paths
        for path_hint in orphaned:
            self._media_store.delete_asset(path_hint)

    def _promote_hierarchy(self, node: HierarchyNode) -> Tuple[HierarchyNode, List[str], bool, Set[str]]:
        changed_ids: List[str] = []
        pointer = node.pointer
        pointer_changed = False
        referenced_paths: Set[str] = set()

        if pointer and pointer.status != "final":
            promoted = self._media_store.promote(pointer)
            pointer = promoted
            pointer_changed = True
            changed_ids.append(node.node_id)
        if pointer and pointer.path_hint and pointer.status == "final":
            referenced_paths.add(pointer.path_hint)

        new_children: List[HierarchyNode] = []
        children_changed = False

        for child in node.children:
            promoted_child, child_changed_ids, child_changed, child_references = self._promote_hierarchy(child)
            new_children.append(promoted_child)
            if child_changed_ids:
                changed_ids.extend(child_changed_ids)
            if child_changed:
                children_changed = True
            if child_references:
                referenced_paths.update(child_references)

        if pointer_changed or children_changed:
            promoted_node = HierarchyNode(
                node_id=node.node_id,
                name=node.name,
                node_type=node.node_type,
                settings=dict(node.settings),
                pointer=pointer,
                children=new_children,
            )
            return promoted_node, changed_ids, True, referenced_paths

        return node, changed_ids, False, referenced_paths

