from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from app.domain.doc_units.entities import HierarchyNode


NodeMap = Dict[str, HierarchyNode]
ParentMap = Dict[str, Optional[HierarchyNode]]
IndexMap = Dict[str, int]


def collect_node_map(root: HierarchyNode) -> NodeMap:
    nodes: NodeMap = {}

    def _walk(node: HierarchyNode) -> None:
        nodes[node.node_id] = node
        for child in node.children:
            _walk(child)

    _walk(root)
    return nodes


def collect_parent_map(root: HierarchyNode) -> Tuple[ParentMap, IndexMap]:
    parents: ParentMap = {root.node_id: None}
    indices: IndexMap = {}

    def _walk(node: HierarchyNode) -> None:
        for idx, child in enumerate(node.children):
            parents[child.node_id] = node
            indices[child.node_id] = idx
            _walk(child)

    _walk(root)
    return parents, indices


def find_node(root: HierarchyNode, node_id: str) -> Optional[HierarchyNode]:
    if root.node_id == node_id:
        return root
    for child in root.children:
        found = find_node(child, node_id)
        if found:
            return found
    return None


def _clone_node(node: HierarchyNode, *, children: Optional[List[HierarchyNode]] = None, node_id: Optional[str] = None) -> HierarchyNode:
    return HierarchyNode(
        node_id=node_id or node.node_id,
        name=node.name,
        node_type=node.node_type,
        settings=deepcopy(node.settings),
        pointer=node.pointer,
        children=children if children is not None else [_clone_node(child) for child in node.children],
    )


def _clone_with_new_ids(node: HierarchyNode, id_factory: Callable[[], str]) -> HierarchyNode:
    new_id = id_factory()
    return HierarchyNode(
        node_id=new_id,
        name=node.name,
        node_type=node.node_type,
        settings=deepcopy(node.settings),
        pointer=node.pointer,
        children=[_clone_with_new_ids(child, id_factory) for child in node.children],
    )


def rename_node(root: HierarchyNode, target_id: str, new_name: str) -> HierarchyNode:
    if root.node_id == target_id:
        renamed_children = [_clone_node(child) for child in root.children]
        return replace(root, name=new_name, children=renamed_children)

    new_children: List[HierarchyNode] = []
    for child in root.children:
        if child.node_id == target_id:
            renamed_child = replace(child, name=new_name, children=[_clone_node(grand) for grand in child.children])
            new_children.append(renamed_child)
        else:
            new_children.append(rename_node(child, target_id, new_name))
    return replace(root, children=new_children)


def create_folder_node(node_id: str, name: str) -> HierarchyNode:
    return HierarchyNode(
        node_id=node_id,
        name=name,
        node_type=HierarchyNode.FOLDER_TYPE,
        settings={},
        children=[],
    )


def insert_nodes(root: HierarchyNode, parent_id: str, insert_index: int, nodes: Iterable[HierarchyNode]) -> HierarchyNode:
    nodes_to_insert = [_clone_node(node) for node in nodes]
    inserted = False

    def _insert(node: HierarchyNode) -> HierarchyNode:
        nonlocal inserted
        if node.node_id != parent_id:
            new_children = [_insert(child) for child in node.children]
            return replace(node, children=new_children)

        bounded_index = max(0, min(insert_index, len(node.children)))
        new_children: List[HierarchyNode] = []
        for idx, child in enumerate(node.children):
            if idx == bounded_index:
                new_children.extend(nodes_to_insert)
                inserted = True
            new_children.append(_clone_node(child))
        if bounded_index == len(node.children):
            new_children.extend(nodes_to_insert)
            inserted = True

        return replace(node, children=new_children)

    updated = _insert(root)
    if not inserted:
        raise KeyError(f"Parent node '{parent_id}' not found.")
    return updated


def delete_nodes(root: HierarchyNode, node_ids: Iterable[str]) -> HierarchyNode:
    ids = set(node_ids)
    node_map = collect_node_map(root)
    missing = ids - set(node_map.keys())
    if missing:
        raise KeyError(f"Nodes not found in hierarchy: {sorted(missing)}")

    if root.node_id in ids:
        raise ValueError("Cannot delete the root node of a hierarchy.")

    def _prune(node: HierarchyNode) -> Optional[HierarchyNode]:
        if node.node_id in ids:
            return None
        new_children: List[HierarchyNode] = []
        for child in node.children:
            pruned = _prune(child)
            if pruned:
                new_children.append(pruned)
        return replace(node, children=new_children)

    updated = _prune(root)
    if updated is None:
        raise ValueError("Hierarchy became empty after deletion.")
    return updated


def move_nodes(
    root: HierarchyNode,
    node_ids: List[str],
    target_parent_id: str,
    insert_index: int,
    *,
    copy: bool = False,
    id_factory: Optional[Callable[[], str]] = None,
) -> HierarchyNode:
    if not node_ids:
        return _clone_node(root)

    node_map = collect_node_map(root)
    parents, indices = collect_parent_map(root)

    if target_parent_id not in node_map and target_parent_id != root.node_id:
        if root.node_id != target_parent_id:
            raise KeyError(f"Target parent '{target_parent_id}' not found.")

    if any(node_id not in node_map for node_id in node_ids):
        missing = [node_id for node_id in node_ids if node_id not in node_map]
        raise KeyError(f"Nodes not found in hierarchy: {missing}")

    if target_parent_id in node_ids:
        raise ValueError("Cannot move nodes into themselves.")

    # Prevent moving a node into its descendant
    current_parent = parents.get(target_parent_id)
    while current_parent is not None:
        if current_parent.node_id in node_ids:
            raise ValueError("Cannot move a node into one of its descendants.")
        current_parent = parents.get(current_parent.node_id)

    # Prepare nodes to insert
    if copy:
        if id_factory:
            nodes_to_insert = [_clone_with_new_ids(node_map[node_id], id_factory) for node_id in node_ids]
        else:
            nodes_to_insert = [_clone_node(node_map[node_id]) for node_id in node_ids]
        working_root = _clone_node(root)
    else:
        nodes_to_insert = [_clone_node(node_map[node_id]) for node_id in node_ids]
        working_root = delete_nodes(root, node_ids)

        # adjust index when removing siblings before the insertion point
        for node_id in node_ids:
            parent = parents.get(node_id)
            if parent and parent.node_id == target_parent_id:
                node_index = indices.get(node_id, -1)
                if node_index != -1 and node_index < insert_index:
                    insert_index -= 1

    if working_root.node_id == target_parent_id:
        target_id = working_root.node_id
    else:
        target_id = target_parent_id

    return insert_nodes(working_root, target_id, insert_index, nodes_to_insert)


def replace_root(root: HierarchyNode, new_root: HierarchyNode) -> HierarchyNode:
    return _clone_node(new_root)
