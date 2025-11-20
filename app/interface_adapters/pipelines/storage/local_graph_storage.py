from __future__ import annotations

import shutil
from pathlib import Path

from app.application.pipelines.ports import GraphStoragePort
from app.domain.pipelines.graph_pointer import GraphPointer, GraphPointerStatus


class LocalGraphStorage(GraphStoragePort):
    """Stores pipeline graphs on disk under a base directory."""

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._drafts_dir = base_dir / "drafts"
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._drafts_dir.mkdir(parents=True, exist_ok=True)

    def draft_path_for(self, pipeline_name: str) -> Path:
        return self._drafts_dir / f"{pipeline_name}.pygraph"

    def final_path_for(self, pipeline_name: str) -> Path:
        return self._base_dir / f"{pipeline_name}.pygraph"

    def promote(self, pointer: GraphPointer) -> GraphPointer:
        if not pointer.draft_path:
            return pointer
        final_path = self.final_path_for(pointer.draft_path.stem)
        if not pointer.draft_path.exists():
            raise FileNotFoundError(f"Draft graph '{pointer.draft_path}' not found")

        final_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(pointer.draft_path), final_path)
        if not final_path.exists():
            raise RuntimeError(f"Failed to promote draft graph to '{final_path}'")
        return GraphPointer(final_path=final_path, draft_path=None, status=GraphPointerStatus.FINAL)

    def delete_graph(self, pointer: GraphPointer) -> None:
        for path in (pointer.final_path, pointer.draft_path):
            if path and path.exists():
                try:
                    path.unlink()
                except Exception:
                    pass
