# Post-Prompt Error Log

Keep a running list of issues that surfaced right after a prompt was implemented so Codex can double-check similar spots next time.

## 2025-10-22 — Metaclass conflict in `DocUnitTab`
- **Context:** Mixed `Tab` (PySide widget) with `DocUnitView`/`HierarchyDetailsView` protocols, which introduced a Qt metaclass conflict and crashed GUI startup.
- **Fix:** Reverted `DocUnitTab` to inherit from `Tab` only and kept the protocol methods implemented without subclassing.
- **Actionable reminder:** When extending Qt widgets, avoid multiple inheritance with Protocol/ABC bases; expose interfaces via composition instead.
