# ADR-008: Server-rendered HTML with small JS; no SPA build

| Field | Value |
| --- | --- |
| Status | Proposed |
| Date | 2026-10-31 |
| Deciders | Arindam Patranabis |
| Answers | DASH-FR-04, NFR-13 |
| Related | [07-architecture.md](../07-architecture.md) |

**Context.** The dashboard must stay thin (DASH-FR-04), render each section independently, and match `docs/wireframes/prototype.html`. Setup must not need a Node toolchain.

**Decision.** FastAPI with Jinja2 templates built from the prototype. htmx (one vendored file) refreshes single sections. Chart.js (vendored) draws the sector quadrant. About 50 lines of plain JavaScript compute position size from contract entry and stop values; capital and risk never leave the browser except to local settings. Each section renders from its own contract file, so a failed module shows an "unavailable" card. Print CSS plus the browser's Save as PDF covers ARCH-FR-03. Light and dark follow the system setting (NFR-12).

**Consequences.** No build step; works offline; the same templates produce the archived HTML snapshot.

**Alternatives rejected.** React or Vue with Vite: a Node build chain for one page. Streamlit: fast to start, but it re-runs one script per interaction, mixes logic with UI and makes per-section failure isolation harder.
