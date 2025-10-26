# Project Conventions

## Module Structure
- Every major feature (project, doc_units, pipelines, etc.) must have a dedicated directory at each architecture layer (`domain`, `application`, `interface_adapters`, `frameworks`, etc.).
- Place module-specific entities, ports, and use cases inside their respective module folders to keep boundaries explicit.
- Shared utilities that do not belong to a specific module live in clearly named `shared` or `common` folders.

## Factory Organization
- GUI factories are organized in a layered tree that mirrors the feature/modules layout (e.g., `composition_root/gui_factories/doc_units`).
- Each significant tab or window gets its own factory function/class in a dedicated file; higher-level factories compose lower-level ones to produce the full `MainWindow`.
- When introducing a new feature, create its factory module alongside the rest of the composition root tree rather than expanding monolithic factory files.

## Incomplete Work Markers
- Use `# TODO`, `raise NotImplementedError`, or the literal `PROMPT_REQUIRED` to mark intentional gaps only inside scratch/spike files.
- Production code must not contain those markers. Before committing, either implement the code or remove the marker.
- The pre-commit hook/CI lint must fail when markers appear outside approved scratch locations, preventing unfinished chunks from merging silently.
