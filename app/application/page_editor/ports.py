from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Protocol

from app.domain.doc_units.value_objects import DocUnitId


class TranslationOutputStore(Protocol):
    """Persistence boundary for translated images."""

    def save_translated_image(
        self,
        *,
        node_id: str,
        unit_id: DocUnitId,
        original_path: Path,
        output: Any,
    ) -> Optional[str]:
        """
        Persist a translated image payload and return the path string to store in metadata.

        Implementations may return project-relative paths when a project root is available,
        or absolute paths when operating in a temp/session directory.
        """

    def resolve_path(self, stored_path: str) -> Optional[Path]:
        """Resolve a stored path string to an absolute path, if possible."""

    def exists(self, stored_path: str) -> bool:
        """Return True if the stored path string points to an existing file."""
