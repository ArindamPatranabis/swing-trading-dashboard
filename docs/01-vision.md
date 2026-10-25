# 01 · Vision Board & Lean Canvas

**Product:** Swing Trading Dashboard — on-demand research dashboard
**Owner:** Arindam Patranabis · **Version:** 1.1 · **Last updated:** 2026-10-23
**Status:** Draft for review (Phase 0)

> **Changes in v1.1:**
> 1. Frequency changed from a fixed weekly newsletter to **on-demand**: one click on a desktop icon opens a fresh dashboard any day of the week.
> 2. Product restructured into **four independent core modules** (Economic Data, Momentum, Value – Long Term, Value – PE Re-rating) plus independent supporting modules. A change to one module must not affect any other.
> 3. Economic Data module defined (11 indicators with release schedule) and placed at the top of the dashboard.
> 4. COT report section added as a placeholder for a later release.

---

## Vision statement

> Whenever I want, one click opens a dashboard that shows what's moving the macro picture, which stocks have strong momentum, which quality companies are cheap for the long term, and which are being re-rated — with no manual screening.

---

## Vision board

| Target group | Needs | Product | Goals |
| --- | --- | --- | --- |
| Part-time swing trader (me) who holds positions 2–6 weeks and researches whenever I have time, not only on weekends | Cut research time from 3–5 hours to under 45 minutes per session | A dashboard launched from a desktop icon, refreshed on demand | **Personal:** faster, more consistent research, any day of the week |
| Later: other retail swing traders | One consistent, rules-based shortlist instead of several separate screeners | Four independent core modules: Economic Data, Momentum, Value – Long Term, Value – PE Re-rating | **Career:** a portfolio project showing product ownership, modular (service-based) architecture, data engineering and applied AI |
| | Fresh results whenever I check, without waiting for a schedule | Supporting modules: market regime banner, sector rotation, earnings flags, archive, past-picks tracker, AI summary | **Learning:** test which screens actually work, using my own data |
| | Confidence that one broken data source doesn't break everything | Each module runs, fails and is updated on its own | |

---

## Lean canvas

| Box | Content |
| --- | --- |
| **1. Problem** | (1) Screening macro, momentum and valuation by hand across ~550 stocks takes 3–5 hours each time. (2) Results are inconsistent because rules live in my head. (3) Research only happens when I set aside a block of time; there is no quick "check now" option. (4) No record of past picks, so I can't tell which screens work. |
| **Existing alternatives** | Finviz / TradingView screeners, IBD and paid newsletters, manual spreadsheets, scattered macro calendars. |
| **2. Customer segment** | Primary: me, a part-time swing trader. Future: retail swing traders who research at irregular times. |
| **Early adopter** | Me — first user, product owner and tester. |
| **3. Unique value proposition** | Macro + momentum + long-term value + PE re-rating in **one click**, any time — with a "confluence list" of stocks that pass several modules and a tracker that scores past picks. |
| **High-level concept** | "A personal IBD-style research desk on my desktop, refreshed whenever I click." |
| **4. Solution** | Desktop icon → launches the dashboard → the dashboard calls each independent module → each module fetches its own data, validates it, runs its own rules and returns results in a standard format → the dashboard shows each module as its own section and saves a dated snapshot to the archive. Results are cached so repeat clicks on the same day are instant. |
| **5. Channels** | Desktop icon on my PC launching the local dashboard; optional hosted dashboard link; exported snapshot (HTML/PDF) for printing; GitHub repo, README and LinkedIn post for the portfolio audience. |
| **6. Revenue streams** | None — personal tool. Value is time saved, better decisions and career leverage. A paid tier is out of scope for v1.0. |
| **7. Cost structure** | Target under $5/month: free data (yfinance, FRED, FMP free tier), free GitHub Actions for CI, ~$1–3/month AI API depending on how often I run it. Main cost: my time, ~8–10 hrs/week for 12 weeks. |
| **8. Key metrics** | Research time under 45 min per session · click-to-dashboard under 60 seconds from cache, under 5 minutes for a full refresh · if one module fails, the other modules still load (100% of the time) · 4-week return of flagged stocks vs S&P 500 · test coverage 80%+ per module. |
| **9. Unfair advantage** | Rules tuned to my own trading style, plus my own pick-performance history that no generic screener has. |

---

## Product modules

### Core modules (independent)

| # | Module | Question it answers | Includes |
| --- | --- | --- | --- |
| 1 | **Economic Data** (top of dashboard) | What macro data moved recently and what's coming up? | CPI, PCE, ISM Manufacturing PMI, ISM Services PMI, GDP, Fed rate / FOMC, retail sales, car sales, jobs report (NFP), weekly jobless claims, 10Y–2Y yield curve; latest vs prior and next release date |
| 2 | **Momentum** | Which stocks are outperforming with healthy, confirmed trends? | RS rating + RSI screen; RS + Ichimoku cloud screen |
| 3 | **Value – Long Term** | Which quality companies are trading cheap? | Value score, FCF yield, ROE, debt/equity, Piotroski F-score |
| 4 | **Value – PE Re-rating** | Which stocks is the market paying a higher (or lower) multiple for, and is it backed by earnings? | Forward PE vs 52-week median, EPS-estimate trend |

### Economic Data module: indicators and release schedule

This section sits at the **top of the dashboard**. All times are US Eastern (ET).

| Indicator | Frequency | Release timing | Source | What the dashboard shows |
| --- | --- | --- | --- | --- |
| CPI (inflation) | Monthly | Around mid-month, usually 8:30 AM ET | U.S. Bureau of Labor Statistics (BLS) | Headline and core CPI, month-over-month and year-over-year |
| PCE inflation | Monthly | Near the end of the month, 8:30 AM ET (Personal Income and Outlays report) | Bureau of Economic Analysis (BEA) | Headline and core PCE (the Fed's preferred inflation gauge), month-over-month and year-over-year |
| PMI – Manufacturing | Monthly | 1st business day, 10:00 AM ET | ISM | Index value; above or below 50 (expansion vs contraction) |
| PMI – Services | Monthly | 3rd business day, 10:00 AM ET | ISM | Index value; above or below 50 |
| GDP | Quarterly | Advance, second and third (final) estimates each quarter | Bureau of Economic Analysis (BEA) | Annualized growth rate; which estimate it is |
| Fed rate / FOMC | 8 meetings a year | Statement 2:00 PM ET; press conference 2:30 PM ET | Federal Reserve | Current target range; last decision (hike, hold, cut); next meeting date |
| Retail sales | Monthly | Around mid-month, 8:30 AM ET | U.S. Census Bureau | Headline and ex-autos, month-over-month % change |
| Car sales | Monthly | Start of month | BEA light vehicle sales (via FRED) | Annualized units vs prior month |
| Jobs report (NFP) | Monthly | First Friday, 8:30 AM ET | BLS | Payrolls added and unemployment rate vs prior month |
| Weekly jobless claims | Weekly | Every Thursday, 8:30 AM ET | U.S. Department of Labor | Initial claims, 4-week average, continuing claims |
| 10Y–2Y yield curve | Daily (market data) | Updated each trading day | U.S. Treasury yields (via FRED) | 10-year minus 2-year spread; inverted (below 0) or normal; 1-month trend |

**For each indicator, the dashboard shows:** latest value, prior value, change, release date, and the next release date with days remaining. Indicators releasing in the next 7 days are highlighted. If any FOMC meeting or jobs report falls within the next 7 days, it is flagged at the very top.

### COT report section (placeholder — built later)

A reserved dashboard section for the CFTC **Commitments of Traders (COT)** report, covering **crude oil, natural gas, gold and silver**. The report is published weekly. In v1.0 this section shows only a "Coming soon" placeholder. It will be built as its own independent module, so adding it later won't affect the other modules.

### Dashboard layout (top to bottom)

1. Economic Data
2. COT report (placeholder)
3. Market regime banner and sector rotation
4. Momentum
5. Value – PE Re-rating
6. Value – Long Term
7. Confluence list (stocks passing 2+ modules)
8. Past-picks tracker
9. Disclaimer

### Supporting modules (also independent)

Market regime banner · sector rotation view · earnings calendar flags · archive · past-picks tracker (feedback loop) · AI summary · confluence list.

---

## Architecture principle: module independence

Each module is built as its own service, so a change to one never affects another.

| Rule | What it means in practice |
| --- | --- |
| Own code | Each module lives in its own folder/package with no imports from other modules |
| Own data | Each module fetches and caches the data it needs; no shared tables that one module can change for another |
| Own tests and version | Each module has its own test suite and version number, and can be released on its own |
| Standard output contract | Every module returns results in the same agreed format (JSON schema), so the dashboard can show any module without knowing its internals |
| Failure isolation | If a module or its data source fails, the dashboard shows "unavailable" for that section and loads the rest |
| Thin dashboard | The dashboard only calls modules and displays results; it contains no screening logic |
| Combined views read outputs only | The confluence list, AI summary and past-picks tracker read module outputs; they never call into a module's internals |

---

## Scope boundaries

**In scope (v1.0):** four core modules, supporting modules listed above, one-click desktop launch, on-demand refresh with caching, dated snapshots, snapshot export.

**Planned for later (placeholder only in v1.0):** COT report module (crude oil, natural gas, gold, silver).

**Out of scope:** placing trades, broker integration, real-time intraday alerts, personalized buy/sell advice, multi-user subscriptions. Scheduled email delivery is a possible later add-on.

---

## Top risks and assumptions

| Assumption / risk | How I'll test or reduce it |
| --- | --- |
| Free data is reliable enough for screening | Each module validates its own data on every run; contract tests on APIs |
| A full refresh may be too slow for on-demand use | Per-module caching; refresh only stale modules; run modules in parallel |
| ISM PMI data is proprietary and not available free through FRED | Confirm a free source early (e.g., ISM's monthly press release); if none, enter the two PMI values manually each month |
| Release dates shift (holidays, government shutdowns) | Pull official release calendars rather than hard-coding dates; show "date not confirmed" when unknown |
| Frequent clicks may hit free API rate limits | Cache results per trading day; minimum refresh interval per module |
| Independent modules may drift apart in output format | One versioned output contract, checked by a contract test in every module |
| Running several services adds setup complexity for a solo project | Keep each service small; one command (behind the desktop icon) starts everything |
| The modules may produce overlapping or weak lists | Track overlap and 4-week performance from week 7 onward |
| I can keep 8–10 hrs/week for 12 weeks | 2-week sprints with a retro; MVP cut at week 6 |
| AI summary may state wrong numbers | Grounding check: every number must exist in the module outputs |

---

_Disclaimer: personal research project, not investment advice._
