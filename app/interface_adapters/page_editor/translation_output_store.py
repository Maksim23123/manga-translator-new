from __future__ import annotations

import tempfile
import uuid
from pathlib import Path
from typing import Any, Iterable, Optional

from app.application.page_editor.ports import TranslationOutputStore
from app.application.project.ports import CurrentProjectStore
from app.domain.doc_units.value_objects import DocUnitId

try:  # Optional dependencies; guard imports so adapter stays lightweight.
    import cv2  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - environment without OpenCV
    cv2 = None  # type: ignore

try:
    import numpy as np  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - environment without NumPy
    np = None  # type: ignore


def _is_byte_sequence(candidate: Iterable[Any]) -> bool:
    try:
        return all(isinstance(v, int) and 0 <= v <= 255 for v in candidate)
    except Exception:
        return False


def _save_image_output(image: Any, output_path: Path) -> Optional[Path]:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if image is None:
        return None

    if isinstance(image, (bytes, bytearray, memoryview)):
        output_path.write_bytes(bytes(image))
        return output_path

    if isinstance(image, (list, tuple)) and _is_byte_sequence(image):
        output_path.write_bytes(bytes(image))
        return output_path

    if isinstance(image, (str, Path)):
        candidate = Path(image)
        if candidate.exists() and candidate.is_file():
            output_path.write_bytes(candidate.read_bytes())
            return output_path

    if cv2 is not None:
        try:
            if cv2.imwrite(str(output_path), image):
                return output_path
        except Exception:
            pass

    if np is not None:
        try:
            arr = np.asarray(image)
            if arr.size > 0:
                if cv2 is not None:
                    if cv2.imwrite(str(output_path), arr):
                        return output_path
                else:
                    np.save(output_path.with_suffix(".npy"), arr)
                    return output_path.with_suffix(".npy")
        except Exception:
            pass

    try:
        output_path.write_text(repr(image))
        return output_path
    except Exception:
        return None


class FilesystemTranslationOutputStore(TranslationOutputStore):
    """Persists translated images to disk, project-relative when possible."""

    def __init__(self, project_store: CurrentProjectStore, base_temp_dir: Optional[Path] = None) -> None:
        self._project_store = project_store
        temp_base = base_temp_dir or Path(tempfile.gettempdir())
        self._temp_session_dir = temp_base / "manga-translator" / "translated" / str(uuid.uuid4())

    def save_translated_image(
        self,
        *,
        node_id: str,
        unit_id: DocUnitId,
        original_path: Path,
        output: Any,
    ) -> Optional[str]:
        suffix = original_path.suffix or ".png"
        target_dir = self._translation_root(unit_id)
        target_path = target_dir.joinpath(f"{node_id}{suffix}")

        saved = _save_image_output(output, target_path)
        if not saved:
            return None
        return self._path_for_storage(saved)

    def resolve_path(self, stored_path: str) -> Optional[Path]:
        if not stored_path:
            return None
        candidate = Path(stored_path)
        if candidate.is_absolute():
            return candidate
        project_root = self._project_root()
        if project_root:
            return project_root.joinpath(stored_path)
        return None

    def exists(self, stored_path: str) -> bool:
        resolved = self.resolve_path(stored_path) or (Path(stored_path) if Path(stored_path).is_absolute() else None)
        if not resolved:
            return False
        try:
            return resolved.exists()
        except Exception:
            return False

    def _project_root(self) -> Optional[Path]:
        project_data = self._project_store.get_data()
        if not project_data:
            return None
        path = project_data.metadata.get("project_root_path")
        if not path:
            return None
        return Path(path)

    def _translation_root(self, unit_id: DocUnitId) -> Path:
        project_root = self._project_root()
        if project_root:
            return project_root.joinpath("translated", unit_id.value)
        return self._temp_session_dir.joinpath(unit_id.value)

    def _path_for_storage(self, path: Path) -> str:
        project_root = self._project_root()
        if project_root:
            try:
                relative = path.relative_to(project_root)
                return relative.as_posix()
            except ValueError:
                pass
        return str(path)
