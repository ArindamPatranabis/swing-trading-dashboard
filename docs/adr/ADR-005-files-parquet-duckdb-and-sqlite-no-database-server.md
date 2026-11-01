# ADR-005: Files, Parquet, DuckDB and SQLite; no database server

| Field | Value |
| --- | --- |
| Status | Proposed |
| Date | 2026-10-31 |
| Deciders | Arindam Patranabis |
| Answers | Constraint 2 |
| Related | [07-architecture.md](../07-architecture.md) |

**Context.** The data is small: about 550 tickers × 252 trading days × 10 years is roughly 1.4 million daily price rows. There is one user, and setup must take under 5 minutes.

**Decision.** Raw data is Parquet. Modules query it with pandas or embedded DuckDB. Each run's output is a JSON file. The archive index, run log and cost log live in one SQLite file. Owner settings (capital, risk %, presets) live in `~/.stdash/settings.json`, outside the repo. The data root is configurable, and `data/` is in `.gitignore`, so no vendor data is ever committed (NFR-11).

**Consequences.** Nothing to install or pay for; backup is a folder copy; fixtures are ordinary files. Concurrent writers are not supported, which is fine because each file has exactly one writer.

**Alternatives rejected.** PostgreSQL or TimescaleDB: a server to run for data that fits in memory. Cloud object storage: keys and cost for no gain.
