from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from app.application.pipelines.pipeline_executor import (
    EngineParams,
    PipelineExecutionInput,
    PipelineExecutionRequest,
    PipelineExecutionResult,
)
from app.application.pipelines.pipeline_service import PipelineService
from app.application.pipelines.translation_engine import TranslationEngine


@dataclass(slots=True)
class RunPipelinePreviewRequest:
    executor_params: dict[str, Any] = field(default_factory=dict)
    engine_params: Optional[EngineParams] = None
    metadata: dict[str, Any] = field(default_factory=dict)


class RunPipelinePreview:
    """Runs the active pipeline against the selected preview image."""

    def __init__(
        self,
        service: PipelineService,
        engine: TranslationEngine,
    ) -> None:
        self._service = service
        self._engine = engine

    def execute(self, request: Optional[RunPipelinePreviewRequest] = None) -> PipelineExecutionResult:
        active = self._service.collection.active
        if not active:
            raise RuntimeError("No active pipeline selected.")

        if not active.preview_path:
            raise ValueError("No preview image selected.")

        image_path = Path(active.preview_path)
        if not image_path.exists():
            raise FileNotFoundError(image_path)

        if active.is_dirty:
            self._service.save_active()

        graph_path = active.graph.active_path()
        if graph_path is None or not graph_path.exists():
            raise FileNotFoundError(graph_path or Path("pipeline.pygraph"))

        if not self._engine:
            raise RuntimeError("Translation engine is not configured.")

        executor_request = request or RunPipelinePreviewRequest()
        execution_request = PipelineExecutionRequest(
            id=str(uuid.uuid4()),
            input=PipelineExecutionInput(images=[image_path], metadata=executor_request.metadata),
            executor_params=executor_request.executor_params,
            engine_params=executor_request.engine_params,
        )
        return self._engine.run(active.name, graph_path, execution_request)
