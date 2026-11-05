# ADR-003: One versioned output contract

| Field | Value |
| --- | --- |
| Status | Proposed |
| Date | 2026-10-31 |
| Deciders | Arindam Patranabis |
| Answers | PLAT-FR-01, Q17 |
| Related | [07-architecture.md](../07-architecture.md) |

**Context.** PLAT-FR-01 lists the fields every module must return, NFR-07 requires a contract test, and Q17 asks whether modules return every passing stock or only the top N.

**Decision.** `stdash_contract` defines Pydantic v2 models and publishes their JSON Schema as contract v1.0.0 (semantic versioning). The envelope holds module, module version, spec version, contract version, parameter set, as-of time, status (ok, partial, unavailable), sources, rows, warnings and run metrics (runtime, API calls, cost). Row types extend a base: `StockRow` (symbol, market cap, sector, earnings date, `rules_passed`), `MomentumRow` (adds entry, stop, stop basis), `SignalRow` (adds signal status), `IndicatorRow` for Economic Data and `TileRow` for the regime banner. Modules return every passing row; the dashboard applies top-N and universe filters (answers Q17). Capital and risk inputs never enter the contract.

**Consequences.** The dashboard renders any module without knowing its internals. Every module's `test_contract.py` validates its fixture output, so schema drift fails CI. A breaking change bumps the major version, and the dashboard reads the current and previous major versions during a migration.

**Alternatives rejected.** Free-form JSON per module: drift is caught only at render time. Protobuf: a code-generation step with no benefit for local files.
