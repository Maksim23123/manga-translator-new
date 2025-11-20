from __future__ import annotations

from app.application.pipelines.ports import PipelineMetadataRepository
from app.domain.pipelines.pipeline_collection import PipelineCollection


class MemPipelineMetadataRepository(PipelineMetadataRepository):
    """Simple in-memory repository for pipeline metadata."""

    def __init__(self) -> None:
        self._collection = PipelineCollection()

    def load(self) -> PipelineCollection:
        return self._collection

    def save(self, collection: PipelineCollection) -> None:
        self._collection = collection
