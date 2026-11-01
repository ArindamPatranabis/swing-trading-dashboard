# Architecture Decision Records

Format: Context · Decision · Consequences · Alternatives rejected. Statuses: Proposed → Accepted → Superseded. A superseded ADR stays in place and links to its replacement.

| ADR | Decision | Answers | Status |
| --- | --- | --- | --- |
| [ADR-001](ADR-001-modules-run-as-isolated-worker-processes.md) | Modules run as isolated worker processes | PRD Q8 | Proposed |
| [ADR-002](ADR-002-where-microservices-are-used.md) | Where microservices are used | Constraint 4 | Proposed |
| [ADR-003](ADR-003-one-versioned-output-contract.md) | One versioned output contract | PLAT-FR-01, Q17 | Proposed |
| [ADR-004](ADR-004-shared-ingestion-with-immutable-raw-snapshots.md) | Shared ingestion with immutable raw snapshots | PLAT-FR-05, rate-limit risk | Proposed |
| [ADR-005](ADR-005-files-parquet-duckdb-and-sqlite-no-database-server.md) | Files, Parquet, DuckDB and SQLite; no database server | Constraint 2 | Proposed |
| [ADR-006](ADR-006-cache-keyed-by-trading-day-parameters-and-versions.md) | Cache keyed by trading day, parameters and versions | PLAT-FR-04, PARAM-FR-03 | Proposed |
| [ADR-007](ADR-007-no-llm-in-the-core-ai-narrator-is-an-opt-in-plugin.md) | No LLM in the core; AI narrator is an opt-in plugin | Constraint 3 | Proposed |
| [ADR-008](ADR-008-server-rendered-html-with-small-js-no-spa-build.md) | Server-rendered HTML with small JS; no SPA build | DASH-FR-04, NFR-13 | Proposed |
| [ADR-009](ADR-009-local-first-runtime-optional-static-hosted-sample.md) | Local-first runtime; optional static hosted sample | Q11, NFR-09 | Proposed |
| [ADR-010](ADR-010-monorepo-of-independently-versioned-packages.md) | Monorepo of independently versioned packages | Constraint 1, PLAT-FR-03 | Proposed |
| [ADR-011](ADR-011-failure-isolation-and-run-logging-in-the-harness.md) | Failure isolation and run logging in the harness | PLAT-FR-02, PLAT-FR-08 | Proposed |
| [ADR-012](ADR-012-momentums-two-screens-become-two-modules.md) | Momentum's two screens become two modules | Spec 3 vs Screen A | Proposed |

Overview and diagram: [../07-architecture.md](../07-architecture.md)
