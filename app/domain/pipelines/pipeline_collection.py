from __future__ import annotations

from typing import Callable, Iterable, List, Optional

from .graph_pointer import GraphPointer
from .pipeline_unit import PipelineUnit


class PipelineCollection:
    """In-memory set of pipelines with uniqueness rules and active tracking."""

    def __init__(self, pipelines: Optional[Iterable[PipelineUnit]] = None) -> None:
        self._pipelines: List[PipelineUnit] = []
        self._active_name: Optional[str] = None

        for pipeline in pipelines or []:
            self.add(pipeline)

    def list(self) -> List[PipelineUnit]:
        return list(self._pipelines)

    def get(self, name: str) -> Optional[PipelineUnit]:
        return next((p for p in self._pipelines if p.name == name), None)

    @property
    def active(self) -> Optional[PipelineUnit]:
        if self._active_name is None:
            return None
        return self.get(self._active_name)

    def set_active(self, name: Optional[str]) -> Optional[PipelineUnit]:
        if name is None:
            self._active_name = None
            return None
        pipeline = self.get(name)
        if not pipeline:
            raise KeyError(f"Pipeline '{name}' not found")
        self._active_name = pipeline.name
        return pipeline

    def add(self, pipeline: PipelineUnit) -> PipelineUnit:
        if self.get(pipeline.name):
            raise ValueError(f"Pipeline '{pipeline.name}' already exists")
        self._pipelines.append(pipeline)
        if self._active_name is None:
            self._active_name = pipeline.name
        return pipeline

    def add_with_name(self, base_name: str, pointer: GraphPointer, name_generator: Optional[Callable[[str, set[str]], str]] = None) -> PipelineUnit:
        unique_name = self.ensure_unique_name(base_name, name_generator)
        pipeline = PipelineUnit(name=unique_name, graph=pointer)
        return self.add(pipeline)

    def ensure_unique_name(self, desired_name: str, name_generator: Optional[Callable[[str, set[str]], str]] = None) -> str:
        clean_name = desired_name.strip()
        if not clean_name:
            raise ValueError("Pipeline name cannot be empty")

        existing = {p.name for p in self._pipelines}
        if clean_name not in existing:
            return clean_name

        if name_generator:
            return name_generator(clean_name, existing)

        suffix = 2
        candidate = f"{clean_name} ({suffix})"
        while candidate in existing:
            suffix += 1
            candidate = f"{clean_name} ({suffix})"
        return candidate

    def remove(self, name: str) -> PipelineUnit:
        pipeline = self.get(name)
        if not pipeline:
            raise KeyError(f"Pipeline '{name}' not found")
        self._pipelines = [p for p in self._pipelines if p.name != name]
        if self._active_name == name:
            self._active_name = self._pipelines[0].name if self._pipelines else None
        return pipeline

    def rename(self, old_name: str, new_name: str) -> PipelineUnit:
        pipeline = self.get(old_name)
        if not pipeline:
            raise KeyError(f"Pipeline '{old_name}' not found")
        unique_name = self.ensure_unique_name(new_name)
        pipeline.rename(unique_name)
        if self._active_name == old_name:
            self._active_name = unique_name
        return pipeline
