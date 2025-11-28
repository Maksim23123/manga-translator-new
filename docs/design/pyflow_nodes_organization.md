# PyFlow Nodes Organization Design Notes
Date: 2025-11-27

Participants: Codex (assistant), Makss

## 1. Overview
- Captures current state of the custom PyFlow node package `MangaTranslator`, which wires the image-processing pipeline inside the GUI.
- Focused on node classes, pin types, and guard logic that enforce graph constraints; does not redesign the pipeline algorithm itself.
- Goal: establish a baseline so we can replace the legacy-dependent pieces with a new node organization that does not rely on the old `pipeline.*`/`core.*` modules.
- Out of scope: reintroducing legacy `pipeline.*`/`core.*` dependencies or reviving the old execution flow; those will be superseded by new components.
- Target shape: Node classes orchestrate data flow and output wiring; they construct and delegate work to "logic" classes that perform the actual processing. Both node and logic classes will live at the frameworks level within the MangaTranslator PyFlow package.

## 2. Requirements & Constraints
- Functional: supply PyFlow nodes for ingesting an image, detecting text areas, inpainting, extracting and translating text, re-inserting translated text, and returning the final image.
- Functional: expose custom pin types for images and detection hierarchies so PyFlow can type-check connections.
- Non-functional: must tolerate absent legacy modules at import time (current code uses try/except and `setError` fallbacks) until new replacements are built.
- Non-functional: only one `PipelineOutputNode` should exist per root graph (enforced by a guard).
- Non-functional: nodes run inside the PySide6 GUI (PyFlow canvas); errors should not crash the UI.
- Organizational intent: Node classes own orchestration (pin wiring, signal hookup, data routing); logic classes encapsulate processing (e.g., inpainting, detection, translation).

## 3. Architecture & Flow
- Layering: nodes live in `app/third_party/PyFlow/PyFlow/Packages/MangaTranslator`; a singleton guard sits in `app/frameworks/pyside6_gui/tabs/pipelines/output_node_guard.py`.
- Planned layering: keep nodes and add colocated logic classes inside the MangaTranslator package under a frameworks namespace (so PyFlow can import without reaching into domain/application layers).
- Pins: `ImageArrayPin` (wraps numpy/OpenCV matrix) and `HierarchyPin` (wraps detection hierarchy object) extend `PinBase` with colors and serialization rules.
- Node catalog:
  - `PipelineInputImageNode`: pulls preview image path from `core.pipelines_manager.pyflow_interaction_manager`, imports via `pipeline.image_importer.ImageImporter`, outputs `ImageArrayPin`, subscribes to preview path change events.
  - `TextDetectorNode`: in `ImageArrayPin`, out `HierarchyPin`; calls `pipeline.text_detector.TextDetector.get_detection_hierarchy`.
  - `InpainterNode`: inputs `ImageArrayPin` + `HierarchyPin`; uses `pipeline.inpainter.Inpainter.inpaint_bboxes` with `hierarchy.chunks_deepest_boxes`; outputs inpainted image.
  - `TextExtractorNode`: inputs `ImageArrayPin` + `HierarchyPin`; outputs text areas (`IntPin[]`) and original text (`StringPin[]`) via `pipeline.text_extractor.TextExtractor`.
  - `TranslationNode`: input `StringPin[]`, output `StringPin[]`; calls `pipeline.translator.Translator.translate_text_list`.
  - `TextInserterNode`: inputs image (`ImageArrayPin`), text areas (`IntPin[]`), text (`StringPin[]`); outputs image with text via `pipeline.text_inserter.TextInserter`.
  - `PipelineOutputNode`: single `ImageArrayPin` input; registers itself through the output guard and returns the image in `compute`.
- Typical data flow (when all deps exist): Input -> Detect -> Inpaint -> Extract -> Translate -> Insert -> Output.

### 3.1 Logic interfaces (new)
- `ImageImportLogic.run(path: str) -> ImageType`: validate/resolve preview path and return an image payload (cv2 matrix when available, numpy buffer, or a byte-list fallback). Raises `NodeLogicError` when the path is missing or unreadable.
- `TextDetectionLogic.run(image) -> Hierarchy`: accepts image payload, produces a `Hierarchy` container (empty placeholder until a detector backend is wired).
- `InpainterLogic.run(image, hierarchy) -> image`: validates both inputs, returns a copy of the image (placeholder until backend exists).
- `TextExtractionLogic.run(image, hierarchy) -> Tuple[List[Seq[int]], List[str]]`: emits text areas and original text lists, deriving content from hierarchy chunks; lengths always align.
- `TranslationLogic.run(texts: Iterable[str]) -> List[str]`: deterministic translation stub prepending `[translated]` to preserve 1:1 ordering.
- `TextInsertionLogic.run(image, areas, texts) -> image`: validates input alignment, returns a copy of the image (placeholder until backend exists).
- `Hierarchy` now lives in `logic/hierarchy.py`, exposed via pins to decouple from legacy `pipeline.text_detector.*` imports.

### 3.2 Node orchestration contract
- Nodes should construct their logic collaborator eagerly (no side-effects), call `logic.run(...)` inside `compute`, and catch `NodeLogicError` to surface a user-friendly node error without crashing the GUI.
- Inputs must be validated before calling logic; array inputs get copied (via `copy_image`) to avoid mutating upstream pins.
- Legacy imports remain optional/guarded; the new logic path is the primary execution path.
- Nodes should keep event subscriptions optional (e.g., input node listening to preview changes) and callable guards safe for headless tests.

## 4. Data & Storage
- Pins:
  - `ImageArrayPin` defaults to an empty numpy array (or list fallback), serializes by clearing data to avoid bloating saved graphs.
  - `HierarchyPin` holds the hierarchy object; also clears data on serialize.
- Graph persistence relies on PyFlow's package analysis; this doc does not cover file formats, but custom pins deliberately drop runtime payloads on save.

## 5. Events & Communication
- Nodes derive from `NodeBase`, inheriting Signals (`killed`, `computed`, `errorOccurred`, etc.).
- `PipelineInputImageNode` listens to `previewImagePathChanged` on `core.event_bus.pipeline_manager_event_bus.pyflow_iteraction_manager_event_bus` to auto-import images when the preview changes.
- `PipelineOutputNode` uses `get_global_output_guard()`; guard attaches to the node's `killed` signal to remove tracking.

## 6. Edge Cases & Risks
- Legacy imports missing: `pipeline.*` and `core.*` modules are absent in the current repo; nodes catch `ModuleNotFoundError` and either stub classes or set node errors at runtime.
- Output duplication: without the guard, multiple `PipelineOutputNode`s could exist; guard mitigates this but will silently kill extras.
- Graph reference resolution: guard falls back to allowing nodes if graph UIDs cannot be determined to avoid crashes, which can reintroduce duplicates.
- Input validation gaps: some nodes only check for `None` and type, not for shape/length alignment (e.g., text areas vs. text lists).
- Strategic risk: current nodes are tightly coupled to missing legacy modules; the plan is to replace those dependencies rather than resurrect them, so bridging layers will be needed during migration.

## 7. Testing Strategy
- Current state: no explicit tests for PyFlow nodes or guard; GUI-driven usage makes headless testing harder.
- Proposed near-term tests: unit tests for `PipelineOutputGuard` registration/dedupe logic (mock `GraphManager`/graph objects); lightweight tests for pin serialization behavior.
- Integration tests would need stubs/mocks for missing `pipeline.*` modules to validate node `compute` error handling.

## 8. Implementation Checklist
- [x] Define replacement interfaces for import/detect/inpaint/extract/translate/insert/output that will supersede the legacy `pipeline.*`/`core.*` modules, implemented as logic classes colocated with nodes.
- [x] Add a thin orchestration contract for nodes (construct logic, connect signals, set outputs) and document it.
- [x] Add unit tests for `PipelineOutputGuard` happy path and duplicate cleanup.
- [x] Add smoke tests for node `compute` methods with new dependency stubs to confirm error messaging and data propagation.

## 9. Changelog
- 2025-11-27 - Initial snapshot of PyFlow nodes organization and known dependency gaps.
