from __future__ import annotations

import shutil
from pathlib import Path

from app.application.doc_units.ports import MediaStore
from app.application.project.ports import CurrentProjectStore, IdGenerator
from app.domain.doc_units.entities import AssetPointer
from app.domain.doc_units.value_objects import AssetId


class FileSystemMediaStore(MediaStore):
    TEMP_DIR = "temp/doc_units"
    FINAL_DIR = "docs_units/assets"
    RESOLVER_KEY = "doc_media"

    def __init__(self, project_store: CurrentProjectStore, ids: IdGenerator) -> None:
        self._project_store = project_store
        self._ids = ids

    def import_temp(self, source_path: str) -> AssetPointer:
        project_root = self._require_project_root()
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(source_path)

        asset_id = AssetId(self._ids.generate())
        dest_dir = project_root.joinpath(self.TEMP_DIR)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir.joinpath(f"{asset_id.value}{source.suffix}")

        shutil.copy2(str(source), dest_path)

        relative_path = dest_path.relative_to(project_root).as_posix()
        return AssetPointer(
            asset_id=asset_id,
            resolver=self.RESOLVER_KEY,
            status="tmp",
            path_hint=relative_path,
        )

    def promote(self, pointer: AssetPointer) -> AssetPointer:
        if pointer.status == "final":
            return pointer

        project_root = self._require_project_root()
        if not pointer.path_hint:
            raise ValueError("Pointer without path_hint cannot be promoted.")

        source_path = project_root.joinpath(pointer.path_hint)
        if not source_path.exists():
            raise FileNotFoundError(str(source_path))

        dest_dir = project_root.joinpath(self.FINAL_DIR)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir.joinpath(source_path.name)

        shutil.move(str(source_path), dest_path)

        relative_path = dest_path.relative_to(project_root).as_posix()
        return AssetPointer(
            asset_id=pointer.asset_id,
            resolver=pointer.resolver,
            status="final",
            path_hint=relative_path,
        )

    def resolve_path(self, pointer: AssetPointer) -> str:
        project_root = self._require_project_root()
        if not pointer.path_hint:
            raise ValueError("Pointer has no path hint to resolve.")
        return str(project_root.joinpath(pointer.path_hint))

    def list_final_assets(self) -> list[str]:
        project_root = self._require_project_root()
        final_dir = project_root.joinpath(self.FINAL_DIR)
        if not final_dir.exists():
            return []
        assets: list[str] = []
        for child in final_dir.rglob("*"):
            if child.is_file():
                assets.append(child.relative_to(project_root).as_posix())
        return assets

    def delete_asset(self, path_hint: str) -> None:
        project_root = self._require_project_root()
        target = project_root.joinpath(path_hint)
        try:
            target.relative_to(project_root.joinpath(self.FINAL_DIR))
        except ValueError:
            raise ValueError("Cannot delete asset outside final directory") from None
        if target.exists():
            target.unlink()
            self._prune_empty_parents(target.parent, project_root.joinpath(self.FINAL_DIR))
        else:
            return

    def cleanup_temp(self) -> None:
        project_root = self._require_project_root()
        temp_dir = project_root.joinpath(self.TEMP_DIR)
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _require_project_root(self) -> Path:
        project_data = self._project_store.get_data()
        if not project_data:
            raise RuntimeError("Project must be loaded before using media store.")
        root = project_data.metadata.get("project_root_path")
        if not root:
            raise RuntimeError("Project metadata missing 'project_root_path'.")
        return Path(root)

    def _prune_empty_parents(self, path: Path, stop: Path) -> None:
        while path != stop and path.is_dir():
            try:
                path.rmdir()
            except OSError:
                break
            path = path.parent


