from __future__ import annotations

from unittest.mock import Mock

from app.application.doc_units.events import HierarchyUpdated
from app.application.doc_units.use_cases.finalize_doc_unit_assets import FinalizeDocUnitAssets
from app.domain.doc_units.entities import AssetPointer, DocUnit, HierarchyNode
from app.domain.doc_units.value_objects import AssetId, DocUnitId, DocUnitName


def _build_doc_unit(pointer_status: str, path_hint: str | None) -> DocUnit:
    child = HierarchyNode(
        node_id="image-node",
        name="Page 1",
        node_type=HierarchyNode.IMAGE_TYPE,
        settings={},
        pointer=AssetPointer(
            asset_id=AssetId("asset-1"),
            resolver="file",
            status=pointer_status,
            path_hint=path_hint,
        ),
    )
    root = HierarchyNode(
        node_id="root",
        name="Chapter",
        node_type=HierarchyNode.FOLDER_TYPE,
        settings={},
        children=[child],
    )

    return DocUnit(
        unit_id=DocUnitId("unit-1"),
        name=DocUnitName("Unit 1"),
        created_at=None,
        hierarchy=root,
        metadata={},
    )


def test_finalize_promotes_pending_assets():
    repo = Mock()
    doc_unit = _build_doc_unit(pointer_status="temp", path_hint=None)
    repo.list_units.return_value = [doc_unit]

    media = Mock()

    def promote(pointer: AssetPointer) -> AssetPointer:
        return AssetPointer(
            asset_id=pointer.asset_id,
            resolver=pointer.resolver,
            status="final",
            path_hint="media/final.png",
        )

    media.promote.side_effect = promote
    media.list_final_assets.return_value = ["media/final.png", "media/orphan.png"]

    events = Mock()

    use_case = FinalizeDocUnitAssets(repo, media, events)
    use_case.execute()

    repo.save_unit.assert_called_once()
    saved_unit = repo.save_unit.call_args[0][0]
    saved_pointer = saved_unit.hierarchy.children[0].pointer
    assert saved_pointer.status == "final"
    assert saved_pointer.path_hint == "media/final.png"

    media.promote.assert_called_once()
    media.cleanup_temp.assert_called_once_with()
    media.delete_asset.assert_called_once_with("media/orphan.png")

    events.publish.assert_called_once()
    event = events.publish.call_args[0][0]
    assert isinstance(event, HierarchyUpdated)
    assert event.unit_id == "unit-1"
    assert event.changed_node_ids == ["image-node"]


def test_finalize_skips_when_hierarchy_already_final():
    repo = Mock()
    doc_unit = _build_doc_unit(pointer_status="final", path_hint="media/final.png")
    repo.list_units.return_value = [doc_unit]

    media = Mock()
    media.list_final_assets.return_value = ["media/final.png"]

    events = Mock()

    use_case = FinalizeDocUnitAssets(repo, media, events)
    use_case.execute()

    repo.save_unit.assert_not_called()
    media.promote.assert_not_called()
    events.publish.assert_not_called()

    media.cleanup_temp.assert_called_once_with()
    media.delete_asset.assert_not_called()
