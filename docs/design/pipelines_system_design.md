# Pipeline System Design Notes
Date: 2025-10-29

Participants: Assistant (Codex), Makss

## 1. Overview
- Provides project-scoped authoring, persistence, and execution support for Manga Translator pipelines.
- Couples a PyFlow-based visual editor with application/domain services that track pipeline metadata, active selection, and graph files.
- Out of scope: doc-unit asset workflows, non-PyFlow execution engines, or low-level PyFlow custom node authoring.

## 2. Requirements & Constraints
- Must allow CRUD operations on pipelines (create, rename, delete, select active) with unique naming guarantees.
- Active pipeline graph edits happen inside PyFlow; saves persist both metadata (embedded inside the project meta document) and `.pygraph` files alongside the project.
- Integrates with project lifecycle (new/load/save) so that pipeline state loads on project open and persists on save without user intervention.
- GUI behaviour should mirror the legacy application: pipeline list dock, properties pane, modified indicators, and preview image plumbing.
- Non-functional: support Windows-first filesystem semantics, tolerate missing/corrupted metadata sections, keep UI responsive, and avoid duplicating heavyweight PyFlow instances.

## 3. Architecture & Flow
- **Domain layer:** introduces `PipelineUnit` (name, graph path, dirty hooks), `PipelineCollection` (formerly `PipelineData`), and supporting services for name generation and graph path resolution.
- **Application layer:** use cases expose pipeline list retrieval, creation, rename/delete, active selection, preview image updates, graph save/load triggers, and execution entry points. Ports abstract persistence and PyFlow orchestration.
- **Interface adapters:** repositories read/write the pipeline section of the project metadata document, presenters/controllers translate use case responses into Qt view models, and an interaction gateway wraps PyFlow APIs (`PyFlowInteractionManager`, `PipelineExecutor`).
- **Frameworks layer:** PySide6 widgets compose the pipeline tab, integrate PyFlow widget tree, manage dock tools, and surface signals (modified state, selection). Filesystem adapters ensure graph files live under `<project>/pipelines/`. Dock widgets (pipeline list, properties, preview) remain packaged as PyFlow add-ons under the MangaTranslator plugin; they will be refactored to consume the new presenters/use cases instead of the legacy `Core` singleton.
- Flow: Qt action -> controller -> use case -> repository/interaction manager -> event bus -> presenter -> PySide6 view (including PyFlow component). Project save delegates to pipeline save use case, which persists metadata and graph files.

## 4. Data & Storage
- Project metadata: pipelines serialize into the existing project meta file (e.g., `project_meta.json`) under a dedicated `pipelines` key containing the list of pipeline entries. Each entry stores the pipeline name plus a `graph_pointer` structure (status, final path hint, temp draft path) so we can reuse the same promotion pattern as doc-unit assets.
- Graph artifacts: `.pygraph` files written initially into `<project>/temp/pipelines/` (draft) while editing; on project save the draft file is promoted into `<project>/pipelines/` and the pointer status flips to `final`. Naming still follows collision-free rules (e.g., `Pipeline (2).pygraph`).
- In-memory caches: application keeps a `PipelineCollection` for the current project and tracks the active `PipelineUnit`; PyFlow instance holds the live graph. The interaction manager resolves pointers to decide whether to load draft or final files.
- Cleanup rules: deleting a pipeline queues its draft/final graph files for removal; project switching clears cached state, removes orphaned drafts, and resets PyFlow to a blank graph.

## 5. Events & Communication
- Pipeline event bus (mirrors doc-unit pattern) emits: `PipelineListUpdated`, `PipelineAdded`, `PipelineRemoved`, `PipelineRenamed`, `ActivePipelineChanged`, `PipelineGraphDirtyChanged`, and `PreviewImagePathChanged`.
- Cross-module signals: project controller notifies pipelines bundle when a project loads/saves; PyFlow wrapper raises `modifiedChanged` which feeds dirty-state events; persistence manager requests pipeline data flush before project write.
- PyFlow interaction manager listens for project change events to reset state and publishes preview path updates into the GUI dock tools.

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

## 8. Implementation Checklist
- [ ] Port domain models (`PipelineUnit`, collection) with validation and change hooks.
- [ ] Build application use cases and repositories for metadata persistence (inline with project meta) and PyFlow interaction.
- [ ] Implement PySide6 pipeline tab, controllers, and presenters integrating the PyFlow widget.
- [ ] Refactor PyFlow dock tools (list, properties, preview) to invoke the new pipeline adapters/use cases while staying within the plugin package.
- [ ] Wire pipelines bundle into composition root and project lifecycle (load/save, dirty tracking).
- [ ] Implement graph pointer + temp promotion workflow (draft write, promotion on save, cleanup).
- [ ] Add automated tests and developer documentation updates covering setup and usage.

## 9. Changelog
- 2025-10-29 - Drafted pipelines system architecture covering domain/application structure, PyFlow integration strategy, persistence model, and testing plan.
