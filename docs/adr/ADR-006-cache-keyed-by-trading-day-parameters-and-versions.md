# ADR-006: Cache keyed by trading day, parameters and versions

| Field | Value |
| --- | --- |
| Status | Proposed |
| Date | 2026-10-31 |
| Deciders | Arindam Patranabis |
| Answers | PLAT-FR-04, PARAM-FR-03 |
| Related | [07-architecture.md](../07-architecture.md) |

**Context.** A repeat click must open in under 60 s (PLAT-FR-04), a refresh must re-run only stale modules (PLAT-FR-05), and a parameter change must finish in under 10 s with no API calls (PARAM-FR-03).

**Decision.** A module result is keyed by (module, module version, spec version, parameter hash, input partitions). Trading days come from an exchange calendar library; on a holiday the last completed session is used and labelled (PLAT-FR-07). Weekly modules key on the last completed week. Each module declares its inputs in `module.toml`, so the orchestrator builds a dependency graph:

1. On click, serve cached outputs at once.
2. On "Refresh", run only adapters whose datasets are older than their minimum interval.
3. Re-run only modules whose input partitions or keys changed, in parallel.
4. Re-run views last, since they read module outputs.

A parameter change skips step 2 and re-runs only the affected modules on today's partitions.

**Consequences.** Cache invalidation is mechanical: any version, parameter or input change produces a new key. Old keys stay on disk, which also gives the archive its history.

**Alternatives rejected.** A time-to-live cache: can serve results computed from yesterday's data or old rules without saying so.
