# Pipeline System Design Notes
Date: 2025-10-29

Participants: Assistant (Codex), Makss

## 1. Overview
- Provides project-scoped authoring, persistence, and execution support for Manga Translator pipelines.
- Couples a PyFlow-based visual editor with application/domain services that track pipeline metadata, active selection, and graph files.
- Current UI ships with a placeholder "Graph Editor" tab that embeds the legacy MangaTranslator PyFlow add-on; its nodes/tools run in a dependency-stripped shell until the new pipeline stack replaces them.
- The tab now wires the PyFlow dock tools (pipelines list, pipeline properties) through framework-level adapters that attach presenters and controllers from the interface_adapters layer, keeping view ownership on the Qt side.
- Out of scope: doc-unit asset workflows, non-PyFlow execution engines, or low-level PyFlow custom node authoring.

## 2. Requirements & Constraints
- Must allow CRUD operations on pipelines (create, rename, delete, select active) with unique naming guarantees.
- Active pipeline graph edits happen inside PyFlow; saves persist both metadata (embedded inside the project meta document) and `.pygraph` files alongside the project.
- Integrates with project lifecycle (new/load/save) so that pipeline state loads on project open and persists on save without user intervention.
- GUI behaviour should mirror the legacy application: pipeline list dock, properties pane, modified indicators, and preview image plumbing.
- Non-functional: support Windows-first filesystem semantics, tolerate missing/corrupted metadata sections, keep UI responsive, and avoid duplicating heavyweight PyFlow instances.

## 3. Architecture & Flow
- **Domain layer:** introduces `PipelineUnit` (name, graph path, dirty hooks), `PipelineCollection` (formerly `PipelineData`), and supporting services for name generation and graph path resolution.
- **Application layer:** use cases expose pipeline list retrieval, creation, rename/delete, active selection, preview image updates, graph save/load triggers, and execution entry points. Ports abstract persistence and PyFlow orchestration; `PipelineService` now drives a PyFlow gateway and publishes events through `PipelineEventBus`.
- **Interface adapters:** in-memory metadata repository (`MemPipelineMetadataRepository`) and filesystem `LocalGraphStorage` sit behind ports; presenters/controllers translate use case responses into Qt view models; `DeferredPyFlowGateway` defers PyFlow calls until the wrapper attaches.
- **Frameworks layer:** PySide6 widgets compose the pipeline tab, integrate PyFlow widget tree, manage dock tools, and surface signals (modified state, selection). `PyFlowWrapper` exposes the PyFlow gateway API while wiring dock tool adapters. Dock widgets (pipeline list, properties, preview) remain packaged as PyFlow add-ons under the MangaTranslator plugin; adapters live in `frameworks` to bridge them to the presenters/controllers.
- Flow: Qt action -> controller -> use case -> repository/storage/PyFlow gateway -> event bus -> presenter -> PySide6 view (including PyFlow component and dock adapters). Project save delegates to pipeline save use case, which persists metadata and graph files.

## 4. Data & Storage
- Project metadata: pipelines serialize into the existing project meta file (e.g., `project_meta.json`) under a dedicated `pipelines` key containing the list of pipeline entries. Each entry stores the pipeline name plus a `graph_pointer` structure (status, final path hint, temp draft path) so we can reuse the same promotion pattern as doc-unit assets.
- Graph artifacts: `.pygraph` files written initially into `<project>/temp/pipelines/` (draft) while editing; on project save the draft file is promoted into `<project>/pipelines/` and the pointer status flips to `final`. Naming still follows collision-free rules (e.g., `Pipeline (2).pygraph`). Current stub storage writes to `data/pipelines/` (with `drafts/` subfolder) until project-level integration arrives.
- Pre-project fallback: when there is no project path yet (e.g., new project before first save), write drafts to a shared temp root (e.g., `data/temp/pipelines` or an OS cache dir); on first save, switch the base to `<project>/temp/pipelines/`, promote drafts to `<project>/pipelines/`, and periodically sweep the shared temp root to avoid orphans.
- In-memory caches: application keeps a `PipelineCollection` for the current project and tracks the active `PipelineUnit`; PyFlow instance holds the live graph. The interaction manager resolves pointers to decide whether to load draft or final files.
- Cleanup rules: deleting a pipeline queues its draft/final graph files for removal; project switching clears cached state, removes orphaned drafts, and resets PyFlow to a blank graph.

## 5. Events & Communication
- Pipeline event bus (mirrors doc-unit pattern) emits: `PipelineListUpdated`, `PipelineAdded`, `PipelineRemoved`, `PipelineRenamed`, `ActivePipelineChanged`, `PipelineGraphDirtyChanged`, and `PreviewImagePathChanged`.
- Cross-module signals: project controller notifies pipelines bundle when a project loads/saves; PyFlow wrapper raises `modifiedChanged` which feeds dirty-state events through the PyFlow gateway into `PipelineService`; persistence manager requests pipeline data flush before project write.
- PyFlow interaction manager (currently `DeferredPyFlowGateway` + `PyFlowWrapper`) listens for delegate attachment and publishes dirty events; dock adapters in frameworks attach presenters to the PyFlow plugin widgets to reflect list/properties updates.

## 6. Edge Cases & Risks
- Corrupted or missing pipeline metadata inside the project meta document should fail gracefully (log, reset to empty) instead of crashing load.
- Graph files missing on disk must trigger regeneration rather than leaving PyFlow in an inconsistent state.
- Name collisions during rename/create require deterministic suffixing to avoid silent overwrites.
- PyFlow modified flag can desync if graph saves fail; guard with filesystem exception handling and user feedback.
- Concurrent saves (autosave + manual) risk race conditions on `.pygraph` files; serialize writes through the pipelines manager and ensure promotion from temp to final is atomic.

## 7. Testing Strategy
- Unit tests for pipeline use cases (create/rename/delete/set-active, metadata persistence round-trips, unique name generator).
- Integration tests exercising PyFlow interaction manager with a stubbed PyFlow facade to verify graph load/save and preview updates.
- Acceptance-level smoke test that boots the GUI tab with a mocked project store to confirm widgets bind and dirty signals propagate.
- File-based tests to validate cleanup of orphaned draft/final `.pygraph` files when pipelines are removed or saves fail mid-promotion.
- Added coverage: `tests/interface_adapters/pipelines/test_local_graph_storage.py` exercises draft-to-final promotion; `tests/frameworks/pyside6_gui/tabs/pipelines/test_dock_adapters.py` verifies PyFlow dock adapters forward signals and follow view-owned wiring.

## 8. Implementation Checklist
- [x] Port domain models (`PipelineUnit`, collection) with validation and change hooks.
- [x] Build initial application service and ports for metadata, storage, and PyFlow interaction (`PipelineService`, `DeferredPyFlowGateway` stub).
- [x] Implement PySide6 pipeline tab, controllers, and presenters integrating the PyFlow widget with view-owned dock adapters for list/properties.
- [x] Implement graph pointer + temp promotion workflow in `LocalGraphStorage` (draft write, promotion on save, cleanup) with tests.
- [ ] Persist pipeline metadata into project meta (currently in-memory `MemPipelineMetadataRepository`).
- [ ] Wire pipelines bundle into project lifecycle (load/save coordination, dirty tracking tied to project save).
- [ ] Refactor PyFlow dock tool preview wiring and replace legacy add-on shims once pipeline ports land; remove dependency guards when real implementations are available.
- [ ] Add automated tests for full service flow (create/rename/delete/set-active) and preview persistence round-trips.

## 9. Changelog
- 2025-10-29 - Drafted pipelines system architecture covering domain/application structure, PyFlow integration strategy, persistence model, and testing plan.
- 2025-10-30 - Added interim Graph Editor tab wiring legacy PyFlow add-on in stripped-down mode pending full pipeline refactor.
- 2025-11-20 - Wired PyFlow dock list/properties via framework adapters and presenters/controllers, added deferred PyFlow gateway and local graph storage under `data/pipelines/`, composed the pipelines bundle inside the tab factory, and introduced tests for storage promotion and dock adapters.
- 2025-11-21 - Prompt pipeline name on creation through the PyFlow pipelines list dock to align with legacy/doc-unit UX.

## 10. Presentation Wiring Conventions
- Prefer the view-owned wiring already used in doc-units: framework widgets receive controllers and presenters, call controller methods in response to UI events, and attach themselves to presenters (controllers remain view-agnostic).
- Pipeline list/properties docks now use framework-level adapters that attach presenters and forward user actions to controllers, keeping controllers/presenters free of PyFlow widget knowledge.
- When an external tool (e.g., PyFlow internals) cannot easily call controller methods directly, wrap it in a frameworks-level adapter that exposes the needed signals/slots, then hook that wrapper to controllers using the same view-owned pattern.
