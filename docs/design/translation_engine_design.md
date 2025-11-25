# Translation Engine & Node Design Notes
Date: 2025-11-27

Participants: Assistant (Codex), Makss

## 1. Overview
- Provide a unified engine that drives translation by orchestrating pipeline-specific node wrappers.
- Each node wraps a graph manager (PyFlow pipeline variant) and exposes a common lifecycle so the same node can serve multiple execution modes.
- Pipeline selection and parameters are provided by the caller; the engine stays UI-agnostic to avoid configuration drift.

## 2. Requirements & Constraints
- Engine accepts caller-supplied pipeline selection + parameters, triggers translation, and routes pages/images through the correct pipeline.
- Engine reuses nodes across executions to avoid reloading heavy resources (models, caches).
- Must tolerate multiple pipelines per project and dispatch work to the correct node while keeping the UI responsive on Windows-first targets.
- Support non-blocking execution: independent nodes can progress without forcing global waits; callers can receive results incrementally.

## 3. Architecture & Flow
- Engine controller loads a saved PyFlow graph definition, instantiates node wrappers, wires IO edges, and exposes execution entry points (e.g., `run(batch, params)`).
- Node wrapper interface: `prepare(params, resources)`, `run(request) -> result`, `cleanup()`.
- Data contract: standardized request/response envelope with:
  - `id` (correlation), `engine_params` (device/mode/priority/timeouts), `node_params` (defaults + per-node overrides), `input` (image references + metadata), `context` (project/session).
  - Outputs echo `id`, include per-node results, diagnostics (timings/device), and structured errors.
- Scheduling: controller coordinates access to node instances; queued or parallel execution uses per-node locks to protect mutable resources/GPU memory. Downstream tasks are posted when prerequisites complete.
- External callers invoke the engine API; engine makes no assumptions about tab or UI ownership.

## 4. Data & Storage
- Graph definitions stay as `.pygraph` artifacts managed by the existing pipeline persistence flow; the engine reads from the active graph and does not mutate it during preview.
- Parameter snapshots come from the caller; engine treats them as inputs, not as durable config.
- Nodes cache loaded models/resources in memory and share them across executions; cache invalidation occurs on parameter changes that affect model choice.

## 5. Events & Communication
- Engine emits run results (translated pages + logs) to the UI layer via the existing event bus/presenter pattern.
- Node-level emissions: each node produces a result event (success/error) as it finishes; downstream nodes subscribe based on graph edges. Callers can register callbacks (e.g., `on_node_result(node_id, output, ctx)`) or consume from a channel/queue.
- Errors bubble as structured failures with user-friendly messages while logging stack traces for diagnostics.
- Lifecycle signals: node prepare/cleanup events so the UI can show busy/ready states if needed.

## 6. Edge Cases & Risks
- Parameter drift between callers: mitigate by using a shared parameter store or explicit parameter handoff.
- GPU/CPU contention when executions overlap; adopt conservative locking/queuing as a default.
- Large model reloads on parameter changes; prefer lazy reload + reuse where compatible.
- Graph mutation during execution could desync state; enforce read-only operations unless explicitly requested.

## 7. Implementation Checklist
- [ ] Define node wrapper interface and stub implementations around existing graph managers.
- [ ] Build engine controller that loads/wires PyFlow graphs and exposes execution entry points.
- [ ] Expose a caller-facing run API and route results back through presenters/event bus.

## 8. Changelog
- 2025-11-27 - Initial high-level design for the translation engine and node wrapper approach unifying preview and translation flows.
