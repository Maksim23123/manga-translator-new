from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from app.application.pipelines.ports import PipelineMetadataRepository
from app.application.project.ports import CurrentProjectStore
from app.domain.pipelines.graph_pointer import GraphPointer, GraphPointerStatus
from app.domain.pipelines.pipeline_collection import PipelineCollection
from app.domain.pipelines.pipeline_unit import PipelineUnit


class ProjectPipelineMetadataRepository(PipelineMetadataRepository):
    """Persists pipeline metadata inside the current project's metadata."""

    _META_KEY = "pipelines"

    def __init__(self, project_store: CurrentProjectStore) -> None:
        self._project_store = project_store

    def load(self) -> PipelineCollection:
        project = self._get_project()
        meta = project.metadata.get(self._META_KEY) or []
        project_root = self._project_root(project)

        pipelines: List[PipelineUnit] = []
        for entry in meta if isinstance(meta, list) else []:
            name = getattr(entry, "get", lambda *_: None)("name")
            if not name:
                continue

            status_raw = entry.get("status") if isinstance(entry, dict) else None
            try:
                status = GraphPointerStatus(status_raw) if status_raw else GraphPointerStatus.MISSING
            except ValueError:
                status = GraphPointerStatus.MISSING
            final_path = self._resolve_path(entry.get("final_path"), project_root) if isinstance(entry, dict) else None
            draft_path = self._resolve_path(entry.get("draft_path"), project_root) if isinstance(entry, dict) else None
            pointer = GraphPointer(final_path=final_path, draft_path=draft_path, status=status)
            pipelines.append(PipelineUnit(name=name, graph=pointer))

        collection = PipelineCollection(pipelines)
        collection.set_active(None)
        return collection

    def save(self, collection: PipelineCollection) -> None:
        project = self._get_project()
        project_root = self._project_root(project)

        serialized: List[dict] = []
        for pipeline in collection.list():
            serialized.append(
                {
                    "name": pipeline.name,
                    "status": pipeline.graph.status.value,
                    "final_path": self._to_rel(pipeline.graph.final_path, project_root),
                    "draft_path": self._to_rel(pipeline.graph.draft_path, project_root),
                }
            )

        project.metadata[self._META_KEY] = serialized
        self._project_store.set_data(project)

    def _get_project(self):
        project = self._project_store.get_data()
        if not project:
            raise RuntimeError("No project loaded.")
        return project

    def _project_root(self, project) -> Optional[Path]:
        raw = project.metadata.get("project_root_path")
        return Path(raw) if raw else None

    def _to_rel(self, path: Optional[Path], root: Optional[Path]) -> Optional[str]:
        if not path:
            return None
        if not root:
            return str(path)
        try:
            return str(path.relative_to(root))
        except ValueError:
            return str(path)

    def _resolve_path(self, path_str: Optional[str], root: Optional[Path]) -> Optional[Path]:
        if not path_str:
            return None
        path = Path(path_str)
        if root and not path.is_absolute():
            return root / path
        return path
