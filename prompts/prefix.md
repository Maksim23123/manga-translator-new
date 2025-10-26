# Project Starter Prompt

You are working on the Manga Translator project. Follow these steps before and after coding:

1. Review the key documents and keep their expectations in mind:
   - docs.local/convention.md (layered architecture, factory rules, incomplete work markers).
   - docs/design/unit_system_design.md (current system design decisions and open checklist items).
   - prompts/pre_commit_check.md (must pass before final handoff).

2. Confirm the goal of the task and note any missing pieces. If a lifecycle or flow is partially implemented, identify the gap and propose the completion path.

3. While implementing:
   - Respect the architecture (domain <- application <- interface_adapters <- frameworks) (The arhitecture of this project).
   - Prefer existing patterns and abstractions already present in the codebase before introducing new ones.
   - Avoid leaving bare TODO/NotImplementedError markers; use tagged markers only when explicitly requested.
   - Update changelog/design docs when behaviour or architecture changes.

4. After coding:
   - Run or describe applicable tests.
   - Execute the pre-commit checklist and report PASS/FAIL with reasons.

5. Before final handoff, review prompts/codex_post_prompt_errors.md and confirm the change does not repeat any logged mistakes.
