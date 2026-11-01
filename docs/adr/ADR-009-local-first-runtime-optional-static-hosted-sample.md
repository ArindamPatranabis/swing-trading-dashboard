# ADR-009: Local-first runtime; optional static hosted sample

| Field | Value |
| --- | --- |
| Status | Proposed |
| Date | 2026-10-31 |
| Deciders | Arindam Patranabis |
| Answers | Q11, NFR-09 |
| Related | [07-architecture.md](../07-architecture.md) |

**Context.** Cost must stay under $5/month (NFR-09). Q11 asks what a hosted link may show, given data-source terms and the privacy rule for sizing inputs (NFR-15).

**Decision.** Everything runs on the owner's PC. The desktop shortcut calls `start.ps1`, which runs `uv run stdash up`: it starts `dashboard_api` on 127.0.0.1 and opens the browser, or just opens the browser if the API is already running. An optional Windows Task Scheduler job runs `stdash refresh` on weekday evenings so the first click is already cached. The optional hosted link is a static snapshot that CI builds from synthetic fixture data, with no vendor data and no sizing inputs, published to GitHub Pages (answers Q11).

**Consequences.** $0 compute and hosting. The hosted page is a demo for the portfolio audience, not live research. A phone can reach the live dashboard only on the home network, if the owner chooses to bind beyond localhost.

**Alternatives rejected.** A cloud VM or container service: an always-on cost and a public attack surface for a single user. Serverless functions per module: cold starts, vendor lock-in and secrets management for no need.
