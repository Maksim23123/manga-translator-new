# Unit System Design Notes
Date: 2025-10-18

Participants: Assistant (Codex), Makss

## 1. Metadata Storage
- Requirement: keep all unit metadata inside the project meta document.
- Benefits: a single source of truth simplifies project-level persistence and keeps save/load atomic.
- Risks: the project file may grow quickly; we need partial updates rather than rewriting the entire document each time.
- Proposal: maintain an in-memory projection of the project meta. `UnitRepository` persists via the existing project gateway, updating only the unit slice. Introduce helpers that patch just that slice when saving so the rest of the project meta stays untouched.
- Asset reference options:
  1. **Inline pointers (store everything in project meta)**  
     - Structure: each doc unit embeds objects like `{ "asset_id": "...", "resolver": "image", "status": "tmp" }`.  
     - Pros: project meta is self-contained; easier to snapshot/serialize; no extra lookups when loading a project.  
     - Cons: document grows with every asset; any pointer update dirties the whole meta document; harder to rotate secrets or migrate assets without rewriting the project file.
  2. **Opaque IDs + external registry**  
     - Structure: project meta stores only IDs, e.g. `"cover_image_id": "img-123"`, while the shared media service keeps the detailed pointer/relocation table.  
     - Pros: project meta stays small; asset moves/metadata updates happen without touching the project file; enables cross-module reuse (pipelines, etc.).  
     - Cons: requires loading two sources (project meta + media registry); project snapshots must include both artifacts; stronger coordination needed to keep IDs and registry in sync.
- Decision: adopt inline pointers kept inside the project meta for the initial implementation. Keep serialization helpers and service boundaries modular so we can pivot to an external registry later without cascading changes.

## 2. Temporary Asset Storage and Pointers
- Requirement: write imported images to a project-scoped temp folder, later move them to a permanent location.
- Proposal: introduce an `AssetPointer` (id + logical uri + status). Consumers ask an `AssetResolver` to resolve pointer -> file system path, abstracting whether the asset still lives in `tmp` or in its final location.
- Keep a relocation table keyed by pointer id so moves do not break references.
- Decision: build a shared media/document service responsible for asset storage, pointer resolution, and future reuse by pipelines. The service reads/writes pointer data inside the project meta (inline), but exposes interfaces that allow swapping in an external registry later.

## 3. Cross-Module Communication
- Requirement: broadcast dirty/clean state changes and similar events.
- Proposal: raise domain events (simple dataclasses) from use cases. An application-level `EventBus` adapts them to Qt signals for the GUI.
- Candidate events: `ProjectDirtyStateChanged`, `ActiveDocUnitChanged`, `DocUnitListUpdated`.
- Alternative: presenters receive callbacks directly, but the bus gives better decoupling and makes different frontends possible.

## 4. Documentation
- This file records design decisions and open questions. Update it as discussions converge.
- Once implementation begins, add a changelog section to capture schema changes.

## 5. Repository Structure
- Proposed interfaces:
  - `DocUnitRepository`: CRUD, list, and persistence of unit definitions inside the project meta.
  - `HierarchyRepository`: focused on the node tree, but can reuse the same backing data while providing a clearer API boundary.
- Implementation can still hit the single project meta document to respect requirement (1) while keeping the SRP separation at the port level.
- Shared media/document service will expose complementary ports for asset resolution; doc unit use cases depend on those instead of direct filesystem access. The pointer data it manipulates remains inline with each doc unit for now.

## 6. Active Unit State
- Observation: the GUI can own selection, but use cases (import image, rename) need the target unit.
- Proposal: introduce an application-level `ActiveDocUnitStore`. GUI controllers set it; use cases read it. This mirrors the existing `MemCurrentProjectStore`.
- If session persistence is needed later, store the last active unit id in the project meta.

## 7. Terminology
- Rename approved: use `DocUnit` (instead of `Unit`) and keep `HierarchyNode`.
- Update repository/use case/presenter names to reduce confusion with pipeline units (apply to new project only; legacy app untouched).

## 8. Additional Considerations
- Validation: version the project meta schema so evolving unit data does not break older projects.
- Concurrency: guard against simultaneous writes (autosave plus user action) by queuing mutations or applying lightweight locks.
- Testing: prepare fixtures that simulate project meta documents for repository/unit tests.
- Performance: cache resolved asset pointers; if the project meta grows large, consider lazy loading of the unit slice.

## 9. Implementation Notes (2025-10-18)
- Added the `doc_units` module across domain, application, interface adapters, and frameworks, with inline asset pointers persisted inside the project meta document.
- Introduced a shared filesystem-backed media service responsible for temp/final asset moves while keeping pointers modular.
- Implemented a PySide6 doc-unit tab mirroring the legacy layout and wired it through layered factories (`composition_root/gui_factories/doc_units`).

## 10. Hierarchy Dock Integration (2025-10-22)
- Added `domain.doc_units.services.hierarchy` helpers for pure, copy-on-write tree mutations (rename, insert, delete, move) so application use cases no longer mutate shared node instances.
- Introduced dedicated hierarchy use cases (`LoadHierarchy`, `CreateHierarchyFolder`, `RenameHierarchyNode`, `DeleteHierarchyNodes`, `MoveHierarchyNodes`, `SelectHierarchyNode`) that reuse the existing repository via the hierarchy port and publish `Hierarchy*` events.
- Extended the doc-unit event bus with `HierarchyLoaded`, `HierarchyUpdated`, and `HierarchySelectionChanged` to keep the dock, details view, and other widgets in sync with domain state.
- Implemented a `HierarchyPresenter` + `HierarchyDock` pair to mirror the legacy Manga hierarchy behavior (context menu, drag/drop, rename, expansion memory) while routing all mutations through controllers/use cases.
- Updated the composition root to wire the new hierarchy stack alongside the existing doc-unit tab dependencies.
- Refined selection handling to surface both primary and aggregated hierarchy selections, enabling multi-select operations and driving a new hierarchy-details presenter that updates the dock’s detail pane like the legacy app.
- Importing page assets now preserves the original filename (sans extension) for the hierarchy node label to maintain user expectations.
- Save operations now finalize imported doc-unit assets by promoting temp pointers, clearing the project temp directory, and deleting orphaned assets before persisting the project.
