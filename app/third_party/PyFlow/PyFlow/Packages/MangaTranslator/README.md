# MangaTranslator PyFlow Package

Lightweight PyFlow package that wires the manga translation pipeline inside the GUI. Nodes now validate/normalize inputs and call concrete backend classes directly (no protocol wrappers or logic adapters).

## Layout
- `Nodes/`: PyFlow nodes (input, detect, inpaint, extract, translate, insert, output). Nodes construct backend classes, validate inputs, normalize shapes, handle pin wiring, events, and guard registration.
- `logic/`: Backend implementations (`TextDetectionBackend`, `InpainterBackend`, `TextExtractionBackend`, `TranslationBackend`, `TextInsertionBackend`), helpers (`ImageImportLogic`, `Hierarchy`, `copy_image`, `NodeLogicError`).
- `Pins/`: Custom pins (`ImageArrayPin`, `HierarchyPin`) plus `PIN_REGISTRY` for tests/mocking.
- Guard: `app/frameworks/pyside6_gui/tabs/pipelines/output_node_guard.py` enforces a single `PipelineOutputNode` per root graph.

## Adding a node
1) Implement or reuse a backend under `logic/` (e.g., `TextDetectionBackend.detect`, `TranslationBackend.translate`) that raises `NodeLogicError` on recoverable failures.  
2) In the PyFlow node, validate and normalize inputs (lengths/types/shapes), copy image inputs via `copy_image` before mutation, and call the backend method inside `compute`, catching `NodeLogicError` to surface `setError(...)` without crashing the GUI.  
3) Wire pins/events/guards as usual.

## Testing
- Minimal headless coverage lives in `tests/third_party/pyflow/`, including pin serialization, node smoke tests with patched pins, and guard dedupe logic.
- Run with the bundled venv: `.\venv\Scripts\python -m pytest tests/third_party/pyflow -q`.
