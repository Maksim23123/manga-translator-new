from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class ImageSelection:
    node_id: str
    path: Optional[Path]
    pipeline_id: Optional[str]
    last_pipeline_signature: Optional[str]


@dataclass(slots=True)
class TranslationSummary:
    requested: int
    translated: int
    skipped: list[str]
    failures: list[str]
