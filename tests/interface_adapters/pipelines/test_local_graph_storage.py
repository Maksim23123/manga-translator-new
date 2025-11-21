from __future__ import annotations

from pathlib import Path

import pytest

from app.domain.pipelines.graph_pointer import GraphPointer, GraphPointerStatus
from app.interface_adapters.pipelines.storage.local_graph_storage import LocalGraphStorage


def test_promote_moves_draft_to_final(tmp_path: Path) -> None:
    storage = LocalGraphStorage(finals_dir=tmp_path)
    draft_path = storage.draft_path_for("example")
    draft_path.write_text("graph-data")

    pointer = GraphPointer(final_path=None, draft_path=draft_path, status=GraphPointerStatus.DRAFT)

    promoted = storage.promote(pointer)

    assert promoted.status is GraphPointerStatus.FINAL
    assert promoted.draft_path is None
    assert promoted.final_path == storage.final_path_for("example")
    assert promoted.final_path and promoted.final_path.read_text() == "graph-data"
    assert not draft_path.exists()
    assert not promoted.final_path.with_suffix(f"{promoted.final_path.suffix}.bak").exists()
    assert not promoted.final_path.with_suffix(f"{promoted.final_path.suffix}.tmp").exists()


def test_promote_raises_when_draft_missing(tmp_path: Path) -> None:
    storage = LocalGraphStorage(finals_dir=tmp_path)
    missing_path = storage.draft_path_for("ghost")
    pointer = GraphPointer(final_path=None, draft_path=missing_path, status=GraphPointerStatus.DRAFT)

    with pytest.raises(FileNotFoundError):
        storage.promote(pointer)


def test_set_project_root_updates_paths(tmp_path: Path) -> None:
    fallback_final = tmp_path / "fallback"
    shared_drafts = tmp_path / "shared" / "drafts"
    storage = LocalGraphStorage(finals_dir=fallback_final, drafts_dir=shared_drafts)

    storage.set_project_root(tmp_path / "project")

    assert storage.final_path_for("pipe").parent == tmp_path / "project" / "pipelines"
    assert storage.draft_path_for("pipe").parent == tmp_path / "project" / "temp" / "pipelines"


def test_promote_replaces_existing_final_safely(tmp_path: Path) -> None:
    storage = LocalGraphStorage(finals_dir=tmp_path)
    draft_path = storage.draft_path_for("example")
    draft_path.write_text("new-data")

    final_path = storage.final_path_for("example")
    final_path.write_text("old-data")

    pointer = GraphPointer(final_path=final_path, draft_path=draft_path, status=GraphPointerStatus.DRAFT)
    promoted = storage.promote(pointer)

    assert promoted.final_path.read_text() == "new-data"
    assert not final_path.with_suffix(f"{final_path.suffix}.bak").exists()
    assert not final_path.with_suffix(f"{final_path.suffix}.tmp").exists()
