# Unit System Design Notes
Date: 2025-10-18

Participants: Assistant (Codex), Makss

## 1. Overview
- Manages manga doc units (chapters/pages) within a project, including metadata, hierarchy, and asset lifecycle.
- Exposes a layered, Qt-driven UI that mirrors legacy behaviour while remaining swappable for other frontends.
- Out of scope: pipeline execution, non-doc-unit media flows, and legacy backports.

## 2. Requirements & Constraints
- All doc-unit metadata must persist inside the project meta document to keep saves atomic.
- Imported assets land in a project-scoped temp directory and must be promoted/cleaned during save.
- GUI interactions require dirty-state signalling, active-unit tracking, and hierarchy manipulation.
- Design should allow future asset registries or alternate clients without major refactors.

## 3. Architecture & Flow
- **Domain:** entities (`DocUnit`, `HierarchyNode`, `AssetPointer`) and value objects capture invariants.
- **Application:** use cases orchestrate behaviour via ports (create/delete/rename/import/set-active, hierarchy edits, asset finalisation).
- **Interface Adapters:** repositories, media store, presenters, and controllers translate to framework operations.
- **Frameworks:** PySide6 widgets, Qt main window, and filesystem utilities deliver the concrete UI.
- Flow: Qt controller ? use case ? repository/media ? event bus ? presenter ? Qt view.

## 4. Data & Storage
- Project meta stores doc units inline, keyed by ID; hierarchy nodes embed serialised asset pointers.
- `AssetPointer` contains `asset_id`, resolver key, status (`tmp`/`final`), and a project-relative `path_hint`.
- Temp assets live in `<project>/temp/doc_units`; promoted assets move to `<project>/docs_units/assets`.
- `FinalizeDocUnitAssets` promotes staged files, clears temp storage, and deletes orphaned final assets before persistence.

## 5. Events & Communication
- Event bus emits `DocUnitListUpdated`, `ActiveDocUnitChanged`, `ProjectDirtyStateChanged`, `HierarchyLoaded`, `HierarchyUpdated`, and `HierarchySelectionChanged`.
- Presenters subscribe and push view models into PySide6 components, keeping GUI state in sync.
- Dirty events drive tab title indicators; hierarchy events refresh tree models and detail panes.

## 6. Edge Cases & Risks
- **Meta size:** large hierarchies may slow saves—consider partial update helpers.
- **Concurrency:** autosave + user actions need sequencing/locking to avoid overlapping writes.
- **Asset lifecycle:** promotion/cleanup must run on every save to prevent temp bloat or orphaned files.
- **Migration:** version project meta schema when structure evolves.

## 7. Testing Strategy
- Unit tests for repositories and use cases using fixture meta documents.
- Integration tests for asset lifecycle (import ? save ? reload) to confirm promotion and cleanup.
- GUI smoke tests (presenter-level) for hierarchy operations: drag/drop, multi-select, rename.

## 8. Implementation Checklist
- [x] Persist doc-unit metadata inline with project meta document.
- [x] Support temp asset import, promotion, cleanup, and orphan removal on save.
- [x] Deliver hierarchy drag/drop, multi-select, and detail view parity with the legacy app.
- [ ] Add automated tests covering asset finalisation and orphan cleanup.
- [ ] Monitor project meta size/performance; evaluate partial-update helpers.

## 9. Changelog
- 2025-10-18 – Bootstrapped doc-unit modules, inline metadata persistence, filesystem media service, and PySide6 doc-unit tab integration.
- 2025-10-22 – Added hierarchy helpers, GUI parity (multi-select, drag/drop), filename preservation, and save-time asset promotion/cleanup with orphan removal.
