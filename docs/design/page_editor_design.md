# Page Editor Tab Design Notes
Date: 2025-12-02

Participants: Codex

## 1. Overview
- Dedicated tab for viewing manga hierarchy, previewing page images in order, and triggering mass translation actions (all/dirty/selected).
- Mirrors legacy Page Editor behaviors (hierarchy-driven ordering, shared pipeline assignment) while fitting the current layered Qt MVP conventions.
- Out of scope: actual translation engine internals, pipeline authoring, and low-level image editing.
- Show both original and translated renderings with a quick toggle so users can compare outputs.

## 2. Requirements & Constraints
- Provide a top bar with actions: Translate All (all pages in active manga), Translate Dirty (only pages whose assigned pipeline changed since last translation), Translate Selected (only currently selected hierarchy items).
- Show selected images in center renderer stacked in hierarchy order; support multi-select and mixed folder/image selections.
- Add a viewer switch for Original vs Translated; default to Original and fall back to Original when no translated file exists.
- Left dock: hierarchy tree for active manga; supports extended selection, reflects active unit changes from project state.
- Right dock: configuration panel for translation settings (at minimum pipeline assignment). Edits apply to all selected images or to all images within selected chapters/subchapters.
- Persist per-image pipeline assignment and last-translated pipeline signature to enable dirty detection.
- Must keep UI responsive; long-running translation actions should run asynchronously with progress and cancellation hooks.

## 3. Architecture & Flow
- Domain: unit hierarchy entities carry image metadata (pipeline assignment, last translation signature); translation use cases accept a list of image nodes and a pipeline id.
- Application: a PageEditorTranslationService orchestrates the three translation commands, resolves target nodes from selections, computes dirty sets, and dispatches jobs to translation workers.
- Interface_adapters: controllers/presenters map Qt events to application use cases; presenters update view models (pipeline options, selection state, progress).
- Frameworks: Qt widgets for the tab shell, docks, top bar buttons, and the shared ImageViewer component; factories wire controllers into views (view-owned wiring).
- Flow: selection in hierarchy -> controller resolves nodes -> presenter updates renderer order -> config dock shows shared/mixed pipeline value -> top bar commands call service with resolved targets and emit progress/events.

## 4. Data & Storage
- Persist per-image metadata: `settings.pipeline_id` (current assignment), `translation.last_pipeline_signature` (pipeline id/hash used on last translation), and `settings.translated_path` (absolute or project-relative path to the saved translated image).
- In-memory: selection state (ordered list of nodes), cached pipeline list from pipelines manager, dirty computation cache (pipeline_id vs last_signature), and resolved image paths for original/translated views.
- Translated images are written to disk: if a project is loaded, under `<project_root>/translated/<doc_unit_id>/`; otherwise to a shared temp folder (e.g., `%TEMP%/manga-translator/translated/<session>/`). When re-translating, overwrite the existing file to avoid growth.

## 5. Events & Communication
- Consumes: activeProjectChanged, activeUnitChanged/Updated, pipelinesUpdated (to refresh pipeline combo), projectDataStateChanged (to reflect dirty UI state).
- Produces: selectionChanged (ordered nodes), configChanged (pipeline assignment updates), translationRequested/Started/Progress/Completed/Failed events dispatched through the application bus, hierarchyUpdated with translated path updates.
- Controllers avoid direct domain imports from Qt; they communicate via ports/use cases.

## 6. Edge Cases & Risks
- Empty project/unit or missing pipelines (disable actions, show placeholder).
- Mixed selections with conflicting pipeline assignments (show blank/mixed state; bulk change writes to all).
- Dirty detection drift if pipeline definitions change without id/hash updates; require consistent pipeline signature calculation.
- Large selections could generate long jobs; ensure batching and cancellation, avoid blocking the UI thread.
- Missing image files in hierarchy should be skipped with surfaced warnings, not fatal errors.
- Translated view must gracefully fall back to originals if files are missing or not yet generated; avoid broken images.

## 7. Testing Strategy
- Unit tests for selection-to-target resolution (folders flatten to ordered images), dirty-set computation, and bulk pipeline assignment.
- Integration tests for translation commands ensuring correct target sets per action (all/dirty/selected), persistence of pipeline settings, translated path writes, and original/translated toggle behavior.
- GUI/Qt tests (or harnessed presenter tests) for mixed selection display state and ordering passed to the image renderer.

## 8. Implementation Checklist
- [x] Add Page Editor tab view (top bar actions, left/right docks, central renderer) with factory wiring in composition_root.
- [x] Implement PageEditor controller/presenter pair with selection handling and view-owned wiring to renderer and config dock.
- [x] Create application service/port for translation actions (all/dirty/selected) and pipeline signature tracking.
- [x] Persist pipeline assignment and last translation signature on image nodes; refresh dirty indicators and state-change notifications.
- [x] Integrate pipeline list updates and project/unit lifecycle events into the tab.
- [ ] Save translated images per page (project subfolder or temp) and store their paths in hierarchy metadata.
- [ ] Add Original/Translated toggle to the Page Editor viewer with safe fallback to originals.

## 9. Changelog
- 2025-12-02 - Initial design draft for Page Editor tab.
- 2025-12-02 - Added first-pass Page Editor implementation (tab UI, services, wiring).
