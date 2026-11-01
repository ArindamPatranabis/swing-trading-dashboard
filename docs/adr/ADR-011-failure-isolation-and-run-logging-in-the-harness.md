# ADR-011: Failure isolation and run logging in the harness

| Field | Value |
| --- | --- |
| Status | Proposed |
| Date | 2026-10-31 |
| Deciders | Arindam Patranabis |
| Answers | PLAT-FR-02, PLAT-FR-08 |
| Related | [07-architecture.md](../07-architecture.md) |

**Context.** One failing module must never block another (PLAT-FR-02, NFR-03), and every run must log runtime, rows, API calls and cost (PLAT-FR-08).

**Decision.** The contract library's run harness wraps every adapter, module and view the same way: validate inputs, run, validate output, write the file atomically (temp file, then rename), and append one row to the SQLite run log with status and error. Each section shows one of four states: ok, partial (under 95% coverage), stale (last good result shown, with its as-of) or unavailable (with the reason). A CI failure-isolation test breaks each adapter and module in turn and asserts that every other section still renders. A weekly scheduled CI job checks that yfinance, FRED and SEC EDGAR still return the required fields (NFR-08).

**Consequences.** Isolation is built into the harness, so new modules inherit it without extra code.

**Alternatives rejected.** Try/except in the dashboard only: misses crashes, hangs and malformed output.
