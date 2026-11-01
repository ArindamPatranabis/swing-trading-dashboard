# ADR-010: Monorepo of independently versioned packages

| Field | Value |
| --- | --- |
| Status | Proposed |
| Date | 2026-10-31 |
| Deciders | Arindam Patranabis |
| Answers | Constraint 1, PLAT-FR-03 |
| Related | [07-architecture.md](../07-architecture.md) |

**Context.** Constraint 1 and PLAT-FR-03 require each module to be built, tested, versioned and released alone. The owner is a solo developer.

**Decision.** One repo managed as a uv workspace:

```
contract/            stdash_contract (library)
adapters/            market, macro, fundamentals
modules/             econ, momentum_rs_rsi, momentum_rs_ichimoku, value_long_term,
                     value_pe_history, market_regime, sector_rotation, earnings_flags, cot
views/               confluence, whats_new, tracker, summary, archive
apps/                dashboard_api (+ web templates), launcher
plugins/             ai_narrator (optional)
templates/module/    copier template for new modules (COT, Spec 6)
```

Each package has its own `pyproject.toml`, version and tests. An import-linter contract allows packages under `adapters/`, `modules/` and `views/` to import only `stdash_contract` and third-party libraries. CI uses path filters so a change to one module runs that module's tests plus every contract test; a nightly job runs everything. Releases are tagged per package, for example `momentum_rs_rsi-v0.2.0`.

**Consequences.** One clone and one command for setup, with real independence enforced by tooling rather than by discipline.

**Alternatives rejected.** One repo per module: release and dependency overhead for one person. One package with sub-folders: cannot version or release modules separately.
