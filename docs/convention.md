# Project Conventions

## Module Structure
- Every major feature (project, doc_units, pipelines, etc.) must have a dedicated directory at each architecture layer (`domain`, `application`, `interface_adapters`, `frameworks`, etc.).
- Place module-specific entities, ports, and use cases inside their respective module folders to keep boundaries explicit.
- Shared utilities that do not belong to a specific module live in clearly named `shared` or `common` folders.

## Factory Organization
- GUI factories are organized in a layered tree that mirrors the feature/modules layout (e.g., `composition_root/gui_factories/doc_units`).
- Each significant tab or window gets its own factory function/class in a dedicated file; higher-level factories compose lower-level ones to produce the full `MainWindow`.
- When introducing a new feature, create its factory module alongside the rest of the composition root tree rather than expanding monolithic factory files.

## Presentation Wiring
- Prefer view-owned wiring: framework widgets receive controllers and presenters, call controller methods on UI events, and attach themselves to presenters so controllers stay view-agnostic.
- If an external tool (e.g., PyFlow internals) cannot call controller methods directly, wrap it in a frameworks-level adapter that exposes the needed signals/slots, then connect that wrapper using the same view-owned pattern.

## Incomplete Work Markers
- Use `# TODO`, `raise NotImplementedError`, or the literal `PROMPT_REQUIRED` to mark intentional gaps only inside scratch/spike files.
- Production code must not contain those markers. Before committing, either implement the code or remove the marker.
- The pre-commit hook/CI lint must fail when markers appear outside approved scratch locations, preventing unfinished chunks from merging silently.

## Testing
- Pytest is the standard runner. Execute it from the repo root via `.\venv\Scripts\python.exe -m pytest`.
- Store tests under the top-level `tests/` directory, mirroring the application module structure.
- Test functions follow the snake_case behavior format `test_<method>_<condition>_<expected>()`, e.g., `test_execute_without_active_unit_raises()`.
