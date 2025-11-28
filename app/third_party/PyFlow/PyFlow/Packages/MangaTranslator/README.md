# MangaTranslator PyFlow Package

Lightweight PyFlow package that wires the manga translation pipeline inside the GUI. Nodes are thin orchestrators; processing lives in colocated `logic` classes so the package no longer depends on legacy `pipeline.*`/`core.*` modules.

## Layout
- `Nodes/`: PyFlow nodes (input, detect, inpaint, extract, translate, insert, output). Nodes construct logic classes and handle pin wiring, events, and guard registration.
- `logic/`: Dependency-free processing stubs (`ImageImportLogic`, `TextDetectionLogic`, `InpainterLogic`, `TextExtractionLogic`, `TranslationLogic`, `TextInsertionLogic`, `Hierarchy`).
- `Pins/`: Custom pins (`ImageArrayPin`, `HierarchyPin`) plus `PIN_REGISTRY` for tests/mocking.
- Guard: `app/frameworks/pyside6_gui/tabs/pipelines/output_node_guard.py` enforces a single `PipelineOutputNode` per root graph.

## Adding a node
1) Add a logic class with a pure `run(...)` method under `logic/`, raising `NodeLogicError` on recoverable failures.  
2) Create the PyFlow node under `Nodes/`, instantiate the logic class in `__init__`, validate inputs, call `logic.run(...)` in `compute`, and catch `NodeLogicError` to surface `setError(...)` without crashing the GUI.  
3) Prefer copying image inputs via `copy_image` before mutation to avoid upstream side effects.

## Testing
- Minimal headless coverage lives in `tests/third_party/pyflow/`, including pin serialization, node smoke tests with patched pins, and guard dedupe logic.
- Run with the bundled venv: `.\venv\Scripts\python -m pytest tests/third_party/pyflow -q`.
