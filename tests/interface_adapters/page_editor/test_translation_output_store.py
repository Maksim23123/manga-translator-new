from pathlib import Path

from app.domain.doc_units.value_objects import DocUnitId
from app.domain.project.value_objects import ProjectData, ProjectID, ProjectName
from app.interface_adapters.page_editor.translation_output_store import (
    FilesystemTranslationOutputStore,
)


class FakeProjectStore:
    def __init__(self, project_data) -> None:
        self._data = project_data

    def get_data(self):
        return self._data

    def set_data(self, project_data) -> None:
        self._data = project_data


def _project_store_with_root(root: Path) -> FakeProjectStore:
    data = ProjectData(
        project_id=ProjectID("project-1"),
        name=ProjectName("Test Project"),
        metadata={"project_root_path": str(root)},
    )
    return FakeProjectStore(data)


def test_save_translated_image_writes_bytes_relative_to_project(tmp_path: Path) -> None:
    store = FilesystemTranslationOutputStore(_project_store_with_root(tmp_path), base_temp_dir=tmp_path)
    unit_id = DocUnitId("unit-1")
    original = tmp_path / "orig.png"
    original.write_bytes(b"orig")

    stored_path = store.save_translated_image(
        node_id="node-1",
        unit_id=unit_id,
        original_path=original,
        output=b"\x01\x02\x03",
    )

    assert stored_path == f"translated/{unit_id.value}/node-1.png"
    resolved = store.resolve_path(stored_path or "")
    assert resolved == tmp_path / "translated" / unit_id.value / "node-1.png"
    assert resolved.read_bytes() == b"\x01\x02\x03"
    assert store.exists(stored_path or "")


def test_save_translated_image_writes_int_sequence_without_project(tmp_path: Path) -> None:
    store = FilesystemTranslationOutputStore(FakeProjectStore(None), base_temp_dir=tmp_path)
    unit_id = DocUnitId("unit-2")
    original = tmp_path / "orig2.png"
    original.write_bytes(b"orig")

    stored_path = store.save_translated_image(
        node_id="node-2",
        unit_id=unit_id,
        original_path=original,
        output=[0, 1, 2, 255],
    )

    assert stored_path is not None
    resolved = Path(stored_path)
    assert resolved.is_absolute()
    assert resolved.read_bytes() == bytes([0, 1, 2, 255])
    assert store.exists(stored_path)


def test_save_translated_image_copies_existing_file(tmp_path: Path) -> None:
    store = FilesystemTranslationOutputStore(_project_store_with_root(tmp_path), base_temp_dir=tmp_path)
    unit_id = DocUnitId("unit-3")
    source = tmp_path / "source.png"
    source.write_bytes(b"image-bytes")
    original = tmp_path / "orig.png"
    original.write_bytes(b"orig")

    stored_path = store.save_translated_image(
        node_id="node-3",
        unit_id=unit_id,
        original_path=original,
        output=source,
    )

    assert stored_path == f"translated/{unit_id.value}/node-3.png"
    resolved = store.resolve_path(stored_path or "")
    assert resolved and resolved.read_bytes() == b"image-bytes"


def test_save_translated_image_none_returns_none(tmp_path: Path) -> None:
    store = FilesystemTranslationOutputStore(_project_store_with_root(tmp_path), base_temp_dir=tmp_path)
    unit_id = DocUnitId("unit-4")
    original = tmp_path / "orig.png"
    original.write_bytes(b"orig")

    stored_path = store.save_translated_image(
        node_id="node-4",
        unit_id=unit_id,
        original_path=original,
        output=None,
    )

    expected = tmp_path / "translated" / unit_id.value / "node-4.png"

    assert stored_path is None
    assert not expected.exists()
