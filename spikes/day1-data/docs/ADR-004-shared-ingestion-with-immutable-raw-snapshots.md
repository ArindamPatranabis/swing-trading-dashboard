# ADR-004: Shared ingestion with immutable raw snapshots

| Field | Value |
| --- | --- |
| Status | Accepted (2026-10-31) |
| Date | 2026-10-31 |
| Deciders | Arindam Patranabis |
| Answers | PLAT-FR-05, rate-limit risk |
| Related | [07-architecture.md](../07-architecture.md) |

**Context.** The vision says each module fetches its own data. But six modules need the same yfinance prices for about 550 tickers, so per-module fetching multiplies API calls about six times, raises the rate-limit risk in the PRD, endangers the 5-minute refresh, and makes module tests depend on the network.

**Decision.** Three adapters (market, macro, fundamentals) are the only code that calls external APIs. Each writes dated, immutable Parquet partitions, `data/raw/<dataset>/as_of=YYYY-MM-DD/`, with a manifest (source, fetch time, coverage, schema version). Modules read these read-only and own everything they derive in `data/modules/<name>/`. Raw dataset schemas live in the contract library, so a module's fixtures are just small Parquet files. Each adapter has its own minimum refresh interval.

**Consequences.** One fetch per dataset; modules are testable offline; a parameter re-run makes no API calls by construction. The vision's intent holds, since no module can change data another depends on. An adapter failure affects every module that needs its dataset, so modules fall back to the last good partition and report "partial" with its as-of date. This changes the vision's "Own data" rule and needs the owner's sign-off.

**Alternatives rejected.** Per-module fetching through a shared HTTP cache: keeps the vision wording but hides shared state inside a cache. One central data HTTP service: more moving parts for the same result.
