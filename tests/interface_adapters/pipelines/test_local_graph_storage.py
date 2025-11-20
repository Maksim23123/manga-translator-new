from __future__ import annotations

from pathlib import Path

import pytest

from app.domain.pipelines.graph_pointer import GraphPointer, GraphPointerStatus
from app.interface_adapters.pipelines.storage.local_graph_storage import LocalGraphStorage


def test_promote_moves_draft_to_final(tmp_path: Path) -> None:
    storage = LocalGraphStorage(tmp_path)
    draft_path = storage.draft_path_for("example")
    draft_path.write_text("graph-data")

    pointer = GraphPointer(final_path=None, draft_path=draft_path, status=GraphPointerStatus.DRAFT)

    promoted = storage.promote(pointer)

    assert promoted.status is GraphPointerStatus.FINAL
    assert promoted.draft_path is None
    assert promoted.final_path == storage.final_path_for("example")
    assert promoted.final_path and promoted.final_path.read_text() == "graph-data"
    assert not draft_path.exists()


def test_promote_raises_when_draft_missing(tmp_path: Path) -> None:
    storage = LocalGraphStorage(tmp_path)
    missing_path = storage.draft_path_for("ghost")
    pointer = GraphPointer(final_path=None, draft_path=missing_path, status=GraphPointerStatus.DRAFT)

    with pytest.raises(FileNotFoundError):
        storage.promote(pointer)
