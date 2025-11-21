from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Optional

from app.application.pipelines.ports import GraphStoragePort
from app.domain.pipelines.graph_pointer import GraphPointer, GraphPointerStatus

log = logging.getLogger(__name__)


class LocalGraphStorage(GraphStoragePort):
    """Stores pipeline graphs on disk with project-aware paths."""

    def __init__(self, finals_dir: Path, drafts_dir: Optional[Path] = None) -> None:
        self._fallback_finals_dir = finals_dir
        self._fallback_drafts_dir = drafts_dir or finals_dir / "drafts"

        self._finals_dir = self._fallback_finals_dir
        self._drafts_dir = self._fallback_drafts_dir
        self._ensure_dirs()

    def set_project_root(self, project_root: Optional[Path]) -> None:
        """Point drafts/finals to a project root or revert to fallback."""
        if project_root:
            self._finals_dir = project_root / "pipelines"
            self._drafts_dir = project_root / "temp" / "pipelines"
        else:
            self._finals_dir = self._fallback_finals_dir
            self._drafts_dir = self._fallback_drafts_dir
        self._ensure_dirs()

    def draft_path_for(self, pipeline_name: str) -> Path:
        return self._drafts_dir / f"{pipeline_name}.pygraph"

    def final_path_for(self, pipeline_name: str) -> Path:
        return self._finals_dir / f"{pipeline_name}.pygraph"

    def promote(self, pointer: GraphPointer) -> GraphPointer:
        if not pointer.draft_path:
            return pointer
        draft_path = pointer.draft_path
        final_path = pointer.final_path or self.final_path_for(draft_path.stem)
        if not draft_path.exists():
            log.warning("Draft graph missing; cannot promote %s", draft_path)
            raise FileNotFoundError(f"Draft graph '{pointer.draft_path}' not found")

        final_path.parent.mkdir(parents=True, exist_ok=True)
        backup_path = final_path.with_suffix(f"{final_path.suffix}.bak")
        temp_path = final_path.with_suffix(f"{final_path.suffix}.tmp")

        # Best-effort cleanup of prior temp/backup files.
        for stale in (backup_path, temp_path):
            if stale.exists():
                try:
                    stale.unlink()
                except Exception:
                    pass

        log.debug("Promoting draft graph from %s to %s", draft_path, final_path)
        shutil.copy2(draft_path, temp_path)

        restore_needed = False
        try:
            if final_path.exists():
                final_path.replace(backup_path)
                restore_needed = True

            temp_path.replace(final_path)
            draft_path.unlink(missing_ok=True)
            if backup_path.exists():
                backup_path.unlink()
        except Exception:
            # Attempt to restore the previous final on failure.
            try:
                if restore_needed and backup_path.exists():
                    backup_path.replace(final_path)
            except Exception:
                pass
            # Leave the draft in place for another attempt.
            log.exception("Failed to promote draft graph to '%s'", final_path)
            raise RuntimeError(f"Failed to promote draft graph to '{final_path}'")
        finally:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass

        log.info("Promoted draft graph to %s", final_path)
        return GraphPointer(final_path=final_path, draft_path=None, status=GraphPointerStatus.FINAL)

    def delete_graph(self, pointer: GraphPointer) -> None:
        for path in (pointer.final_path, pointer.draft_path):
            if path and path.exists():
                try:
                    path.unlink()
                except Exception:
                    pass

    def _ensure_dirs(self) -> None:
        self._finals_dir.mkdir(parents=True, exist_ok=True)
        self._drafts_dir.mkdir(parents=True, exist_ok=True)
