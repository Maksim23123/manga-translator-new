# Pipeline System Design Notes
Date: 2025-10-29

Participants: Assistant (Codex), Makss

## 1. Overview
- Provides project-scoped authoring, persistence, and execution support for Manga Translator pipelines.
- Couples a PyFlow-based visual editor with application/domain services that track pipeline metadata, active selection, and graph files.
- Current UI ships with a placeholder "Graph Editor" tab that embeds the legacy MangaTranslator PyFlow add-on; its nodes/tools run in a dependency-stripped shell until the new pipeline stack replaces them.
- The tab now wires the PyFlow dock tools (pipelines list, pipeline properties) through framework-level adapters that attach presenters and controllers from the interface_adapters layer, keeping view ownership on the Qt side.
- Dirty/clean state flows through a shared `ProjectLifecycleEventBus` so pipelines and doc-units can each mark the project dirty without coupling tabs to one another.
- Out of scope: doc-unit asset workflows, non-PyFlow execution engines, or low-level PyFlow custom node authoring.

## 2. Requirements & Constraints
- Must allow CRUD operations on pipelines (create, rename, delete, select active) with unique naming guarantees.
- Active pipeline graph edits happen inside PyFlow; saves persist both metadata (embedded inside the project meta document) and `.pygraph` files alongside the project.
- Integrates with project lifecycle (new/load/save) so that pipeline state loads on project open and persists on save without user intervention.
- Dirty propagation must raise project-level dirty via the lifecycle bus on pipeline mutations; successful project save must clear it.
- GUI behaviour should mirror the legacy application: pipeline list dock, properties pane, modified indicators, and preview image plumbing.
- When no active pipeline exists, the PyFlow canvas is disabled/blocked to mirror legacy behaviour and avoid editing a non-existent pipeline.
- Non-functional: support Windows-first filesystem semantics, tolerate missing/corrupted metadata sections, keep UI responsive, and avoid duplicating heavyweight PyFlow instances.

## 3. Architecture & Flow
- **Domain layer:** introduces `PipelineUnit` (name, graph path, dirty hooks), `PipelineCollection` (formerly `PipelineData`), and supporting services for name generation and graph path resolution.
- **Application layer:** use cases expose pipeline list retrieval, creation, rename/delete, active selection, preview image updates, graph save/load triggers, and execution entry points. Ports abstract persistence and PyFlow orchestration; `PipelineService` now drives a PyFlow gateway and publishes events through `PipelineEventBus`.
- **Interface adapters:** in-memory metadata repository (`MemPipelineMetadataRepository`) and filesystem `LocalGraphStorage` sit behind ports; presenters/controllers translate use case responses into Qt view models; `DeferredPyFlowGateway` defers PyFlow calls until the wrapper attaches. A shared lifecycle bus is injected so pipeline dirty events promote to project dirty without depending on doc-unit wiring.
- **Frameworks layer:** PySide6 widgets compose the pipeline tab, integrate PyFlow widget tree, manage dock tools, and surface signals (modified state, selection). `PyFlowWrapper` exposes the PyFlow gateway API while wiring dock tool adapters. Dock widgets (pipeline list, properties, preview) remain packaged as PyFlow add-ons under the MangaTranslator plugin; adapters live in `frameworks` to bridge them to the presenters/controllers.
- Flow: Qt action -> controller -> use case -> repository/storage/PyFlow gateway -> event bus -> presenter -> PySide6 view (including PyFlow component and dock adapters). Project save delegates to pipeline save use case, which persists metadata and graph files.

## 4. Data & Storage
- Project metadata: pipelines serialize into the existing project meta file (e.g., `project_meta.json`) under a dedicated `pipelines` key containing the list of pipeline entries. Each entry stores the pipeline name plus a `graph_pointer` structure (status, final path hint, temp draft path) so we can reuse the same promotion pattern as doc-unit assets. The active pipeline is not persisted; it is tracked transiently to mirror doc-units.
- Graph artifacts: `.pygraph` files written initially into `<project>/temp/pipelines/` (draft) while editing; on project save the draft file is promoted into `<project>/pipelines/` and the pointer status flips to `final`. Naming still follows collision-free rules (e.g., `Pipeline (2).pygraph`). Storage now points at project roots when available and falls back to `data/pipelines/` with per-project shared-temp subfolders before the first save.
- Pre-project fallback: when there is no project path yet (e.g., new project before first save), write drafts to a shared temp root (e.g., `data/temp/pipelines` or an OS cache dir). Use per-project subfolders within the shared root (e.g., `data/temp/pipelines/<project_id_or_hash>/`) to isolate drafts; on first save, switch the base to `<project>/temp/pipelines/`, promote drafts to `<project>/pipelines/`, then delete that subfolder if promotion succeeds.
- In-memory caches: application keeps a `PipelineCollection` for the current project and tracks the active `PipelineUnit` via an `ActivePipelineStore` (transient, not persisted). PyFlow instance holds the live graph. The interaction manager resolves pointers to decide whether to load draft or final files.
- Active switch rule: when changing the active pipeline, persist the current pipeline’s graph to its draft path before switching (at minimum when marked dirty), then load the newly selected pipeline into PyFlow. Active selection resets on project load/create.
- Cleanup rules: deleting a pipeline removes only its draft graph; the final stays on disk only until the next project load, when the orphan sweep removes graphs not referenced by metadata. Deletion is therefore permanent once you reload.
- Promotion semantics: on project save, promote draft graphs into `<project>/pipelines/`, update graph pointers to `final`, replace prior finals, and if promotion fails keep the existing final and surface/log the error instead of leaving the pipeline unusable.
- Orphan cleanup: on startup/load sweep stale per-project temp subfolders in the shared root for projects not mounted; after successful promotion, delete only the current project’s shared-temp subfolder. The project-local orphan sweep (drafts/finals missing from the collection) runs during load rather than during save to avoid racing PyFlow writes while persisting the project.
- Save cleanup scope: `cleanup_after_save` is scoped to clearing the shared temp subfolder; graph orphan pruning is deferred to the load-time sweep, with draft removal on delete covering the main temp churn.

## 5. Events & Communication
- Pipeline event bus (mirrors doc-unit pattern) emits: `PipelineListUpdated`, `PipelineAdded`, `PipelineRemoved`, `PipelineRenamed`, `ActivePipelineChanged`, `PipelineGraphDirtyChanged`, and `PipelineGraphPointerUpdated` (preview events still pending).
- Cross-module signals: project controller notifies pipelines bundle when a project loads/saves; PyFlow wrapper raises `modifiedChanged` which feeds dirty-state events through the PyFlow gateway into `PipelineService`; persistence manager requests pipeline data flush before project write. Pipeline dirty/mutation events are bridged into the shared `ProjectLifecycleEventBus` to mark the project dirty; the controller publishes clean state after a successful save.
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
- File-based tests to validate load-time cleanup of orphaned draft/final `.pygraph` files (including ones left after pipeline deletion) and shared temp sweeping.
- Added coverage: `tests/interface_adapters/pipelines/test_local_graph_storage.py` exercises draft-to-final promotion; `tests/frameworks/pyside6_gui/tabs/pipelines/test_dock_adapters.py` verifies PyFlow dock adapters forward signals and follow view-owned wiring.

## 8. Implementation Checklist
- [x] Port domain models (`PipelineUnit`, collection) with validation and change hooks.
- [x] Build initial application service and ports for metadata, storage, and PyFlow interaction (`PipelineService`, `DeferredPyFlowGateway` stub).
- [x] Implement PySide6 pipeline tab, controllers, and presenters integrating the PyFlow widget with view-owned dock adapters for list/properties.
- [x] Implement graph pointer + temp promotion workflow in `LocalGraphStorage` (draft write, promotion on save, cleanup) with tests.
- [x] Persist pipeline metadata into project meta (`ProjectPipelineMetadataRepository` with relative paths, mem fallback for sandbox).
- [x] Wire pipelines bundle into project lifecycle (project-ready load, dirty propagation into lifecycle bus, finalize/promotion before project save).
- [ ] Refactor PyFlow dock tool preview wiring and replace legacy add-on shims once pipeline ports land; remove dependency guards when real implementations are available.
- [ ] Add automated tests for full service flow (create/rename/delete/set-active) and preview persistence round-trips.
- [x] Add `ActivePipelineStore` port + memory impl to keep active selection transient (not persisted) in parity with doc-units.
- [x] Add per-project shared temp subfolders, orphan cleanup (shared + project temp/finals), and guards around promotion failure.
- [x] Block/disable PyFlow editing when no active pipeline is selected to mirror legacy safety.

## 9. Changelog
- 2025-10-29 - Drafted pipelines system architecture covering domain/application structure, PyFlow integration strategy, persistence model, and testing plan.
- 2025-10-30 - Added interim Graph Editor tab wiring legacy PyFlow add-on in stripped-down mode pending full pipeline refactor.
- 2025-11-20 - Wired PyFlow dock list/properties via framework adapters and presenters/controllers, added deferred PyFlow gateway and local graph storage under `data/pipelines/`, composed the pipelines bundle inside the tab factory, and introduced tests for storage promotion and dock adapters.
- 2025-11-21 - Prompt pipeline name on creation through the PyFlow pipelines list dock to align with legacy/doc-unit UX.
- 2025-11-22 - Introduced shared project lifecycle event bus for dirty tracking and moved active pipeline tracking to a transient store (not persisted).
- 2025-11-23 - Implemented per-project shared temp isolation and orphan cleanup for pipeline drafts/finals.
- 2025-11-24 - Deferred pipeline deletion cleanup to load-time orphan sweeping, narrowed `cleanup_after_save` to shared-temp removal, and now delete drafts immediately while allowing finals to be swept on the next load (no recovery once reloaded).
- 2025-11-26 - Persisted pipeline metadata into project meta via the `ProjectPipelineMetadataRepository`, wired the graph editor tab into project lifecycle hooks (project-ready load, finalize/promotion before save), and bridged pipeline dirty events to the shared lifecycle bus.
- 2025-11-27 - Disabled PyFlow canvas interactions when no active pipeline is selected, using `ActivePipelineChanged` wiring to toggle the embedded editor.
- 2025-11-29 - Added a PyFlow output-node guard to enforce a single pipeline output node per graph, mirroring the legacy interaction manager.

## 10. Presentation Wiring Conventions
- Prefer the view-owned wiring already used in doc-units: framework widgets receive controllers and presenters, call controller methods in response to UI events, and attach themselves to presenters (controllers remain view-agnostic).
- Pipeline list/properties docks now use framework-level adapters that attach presenters and forward user actions to controllers, keeping controllers/presenters free of PyFlow widget knowledge.
- When an external tool (e.g., PyFlow internals) cannot easily call controller methods directly, wrap it in a frameworks-level adapter that exposes the needed signals/slots, then hook that wrapper to controllers using the same view-owned pattern.
