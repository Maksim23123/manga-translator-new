from __future__ import annotations

from pathlib import Path
from typing import Optional, Protocol

from app.domain.pipelines.graph_pointer import GraphPointer
from app.domain.pipelines.pipeline_collection import PipelineCollection
from app.domain.pipelines.pipeline_unit import PipelineUnit


class PipelineMetadataRepository(Protocol):
    """Persistence port for pipeline metadata embedded in the project."""

    def load(self) -> PipelineCollection: ...
    def save(self, collection: PipelineCollection) -> None: ...


class GraphStoragePort(Protocol):
    """Filesystem operations for pipeline graph artifacts."""

    def draft_path_for(self, pipeline_name: str) -> Path: ...
    def final_path_for(self, pipeline_name: str) -> Path: ...
    def promote(self, pointer: GraphPointer) -> GraphPointer: ...
    def delete_graph(self, pointer: GraphPointer) -> None: ...


class PipelinePreviewPort(Protocol):
    """Handles preview asset persistence for pipelines."""

    def save_preview(self, pipeline: PipelineUnit, image_path: Path) -> Path: ...
    def delete_preview(self, pipeline: PipelineUnit) -> None: ...


class PyFlowGateway(Protocol):
    """UI-facing facade for manipulating the embedded PyFlow instance."""

    def load_graph(self, graph_path: Path) -> None: ...
    def save_graph(self, target_path: Path) -> None: ...
    def new_blank(self) -> None: ...
    def on_dirty_changed(self, callback: callable) -> None: ...
