# 03 · PRD — Swing Trading Dashboard

Oct 25, 2026 · @Arindam Patranabis

## 1. Overview

The Swing Trading Dashboard is a research dashboard you open with one click. It cuts a research session from 3–5 hours to under 45 minutes. It has four independent core modules: Economic Data, Momentum, Value – Long Term and Value – PE Re-rating. Supporting views add context. The MVP ships at week 6. Version 1.0 ships at week 12.

| Field | Value |
| --- | --- |
| Product | Swing Trading Dashboard |
| Owner | Arindam Patranabis |
| Version | 1.0 (first PRD) |
| Status | Draft for review (Phase 0) |
| Repo location | docs/03-prd.md |
| Related docs | docs/01-vision.md v1.1 · docs/02-persona.md · Product Roadmap v1.1 · docs/04-signal-spec.md (to write) · docs/07-architecture.md (to write) |

**How to read this PRD.** It says what the product must do. It also says how we measure success. Exact formulas and thresholds are in the signal spec. Data fields are in the data dictionary. Design choices are in the architecture doc and ADRs. Every requirement has an ID, for example MOM-FR-03. User stories, tests and commits use these IDs.

**Priority and release tags.** Each requirement has a MoSCoW priority: Must, Should, Could or Won't. It also has a target release: v0.1, v0.2, v0.3 or v1.0.

## 2. Problem and evidence

Research today takes 3–5 hours per session. It uses 5+ tools. I apply the rules differently each time. It keeps no record of what worked. The deep dive is the most useful step, but it gets the least time. The slow steps take most of it: the macro check, screening and merging lists. Source: docs/02-persona.md, current-state journey.

| ID | Pain point | Impact today | Addressed by |
| --- | --- | --- | --- |
| P1 | Research spread across 5+ websites and tools | 3–5 hours per session; steps get skipped | Core modules, confluence list, one dashboard |
| P2 | Screening rules live in my head and change by mood | Inconsistent shortlists | Written, versioned rules in each module |
| P3 | Economic release timing is easy to miss | Entering trades right before CPI, NFP or FOMC | Economic Data module with countdown and flags |
| P4 | Earnings dates checked one stock at a time | Holding through an earnings gap by accident | Earnings flag on every module table |
| P5 | No quick "check now" option | Research only in long blocks; missed opportunities | Desktop launch, cache, on-demand refresh |
| P6 | No record of past picks | Can't tell which screens deserve trust | Archive and past-picks tracker |
| P7 | Hard to tell if the market supports buying | Momentum trades in weak markets | Regime banner and sector rotation |

**Current time spent per session:** macro check 30–45 min, screening 60–90 min, merging 30 min, deep dive 60–90 min, decision 15 min, review 0 min.

**Existing alternatives and why they fall short:** Finviz and TradingView screeners each cover only one lens. IBD and paid newsletters use someone else's rules. Spreadsheets and macro calendars are manual and scattered. No tool shows macro, momentum and valuation in one view. No tool keeps a record of past picks.

## 3. Goals and success metrics

v1.0 succeeds if three things are true. A session takes under 45 minutes. The dashboard opens in under 60 seconds from cache. One broken module never blocks the others.

**Goals**

- **G1 Faster research:** cut research time per session from 3–5 hours to under 45 minutes.
- **G2 Consistent rules:** apply the same written rules the same way on every run.
- **G3 Check any time:** open fresh results with one click, any day of the week.
- **G4 Learn what works:** measure each module's picks against the S&P 500.
- **G5 Portfolio proof:** show product ownership, modular architecture, data engineering and applied AI in a public repo.

**Outcome metrics**

| ID | Metric | Baseline | Target | How measured | Goal |
| --- | --- | --- | --- | --- | --- |
| M1 | Research time per session | 3–5 hrs | Under 45 min | Self-tracked session log | G1 |
| M2 | Click to dashboard, cached | n/a (no product) | Under 60 s | Launcher timing log | G3 |
| M3 | Full refresh, all modules | n/a | Under 5 min | Per-module run log | G3 |
| M4 | 1, 2 and 4-week return of flagged stocks vs S&P 500, per module | Not tracked | Tracked for every pick from week 7 | Past-picks tracker | G4 |
| M5 | Sessions using the dashboard instead of manual screening | 0 | 8+ sessions logged in weeks 7–12 | Session log | G1, G3 |

**Guardrail metrics (must not break)**

| ID | Metric | Target | How measured |
| --- | --- | --- | --- |
| M6 | Failure isolation: other modules load when one fails | 100% of runs | Automated failure-isolation test + run log |
| M7 | Data freshness: each module shows its as-of time from the last completed trading session | 100% of runs | Validation check |
| M8 | Running cost | Under $5/month (AI under $3) | Cost log per run |
| M9 | Test coverage | 80%+ per module, CI green | Coverage report |
| M10 | AI numbers grounded in module outputs | 100% | Grounding check |

## 4. Non-goals

The dashboard is a research aid. It never trades and never gives advice. In v1.0 it is not real-time, and it has only one user.

| Non-goal | Why | Revisit |
| --- | --- | --- |
| Placing trades or broker integration | Personal research tool; avoids execution risk | Not planned |
| Personalised buy/sell advice | Not licensed; outputs are rule results, not recommendations | Not planned |
| Real-time or intraday alerts | Swing horizon is 2–6 weeks; free data is end-of-day | Not planned |
| Multi-user accounts or subscriptions | Single user first | After v1.0 |
| Scheduled email delivery | Replaced by on-demand launch in vision v1.1 | Possible add-on after v1.0 |
| COT report module (beyond a placeholder) | Keeps v1.0 scope achievable | After v1.0 |
| Paid data sources | Cost target under $5/month | Only if free data fails validation |
| Universe beyond S&P 500 + Nasdaq 100 | ~550 tickers fit free API limits | Via config file at v1.0 |

## 5. Users and key scenarios

The primary user is "The After-Hours Swing Trader". This person has a full-time job and trades S&P 500 and Nasdaq 100 stocks part-time. They hold positions for 2–6 weeks, mostly long. The full persona is in docs/02-persona.md.

| User | Need | v1.0 implication |
| --- | --- | --- |
| Primary: the owner | Same rules, one place, in 30 spare minutes, any day | Everything in this PRD |
| Secondary: other retail swing traders (future) | A ready-made, configurable dashboard | Config file for thresholds and watchlists (v1.0, Could) |
| Secondary: recruiters and hiring managers | Quick evidence of product thinking and engineering | README, demo GIF, docs folder, sample snapshot |

**Key scenarios** (each maps to acceptance tests in section 8)

| ID | Scenario | What the dashboard must do | Requirements |
| --- | --- | --- | --- |
| S1 | Weekday quick check (Tuesday evening, 30 min) | Open in under 60 s from cache; highlight what's new since the last visit | PLAT-FR-04, DASH-FR-05 |
| S2 | Before a big release (Thursday before a jobs-report Friday) | Flag NFP at the top with date and time; show the latest jobless claims | ECON-FR-04, ECON-FR-05 |
| S3 | Weekend planning (Saturday, 2 hours) | Full refresh; complete module lists, confluence list and earnings flags for the next 2–6 weeks | PLAT-FR-05, CONF-FR-01, EARN-FR-01 |
| S4 | FOMC week | Flag the meeting date, statement (2:00 PM ET) and press conference (2:30 PM ET) | ECON-FR-05 |
| S5 | A data source is down | Show "unavailable" for that module only; every other module still loads | PLAT-FR-02 |
| S6 | Monthly review | Show 1, 2 and 4-week returns of past picks vs S&P 500, by module | TRACK-FR-01 |

## 6. Release scope

The MVP is v0.1, due at the end of week 6. It is a dashboard you open from a desktop icon. It has the Economic Data module and the RS/RSI screen, built on the full module platform. Later releases add more modules and views. The timeline and phases are in Product Roadmap v1.1.

| Release | Target | Scope | Gate to pass |
| --- | --- | --- | --- |
| v0.1 MVP | End of week 6 | Module platform (contract, template, cache, validation); Economic Data; Momentum screen A (RS + RSI); dashboard shell; desktop launcher; failure isolation; archive; disclaimer; COT placeholder | Opens correctly from the desktop icon on 3+ days across 2 weeks, incl. one cached reopen under 60 s and one run with a module's source disabled where the rest still loads |
| v0.2 | End of week 9 | Momentum screen B (RS + Ichimoku); Value – PE Re-rating; Value – Long Term; confluence list; regime banner; sector rotation; earnings flags | All four core modules pass their contract tests and a full refresh finishes under 5 min |
| v0.3 | End of week 11 | AI summary and "why flagged" notes; past-picks tracker; snapshot export (HTML/PDF); "what's new since last visit" | Grounding check passes on 5 consecutive AI runs; tracker fills from the archive |
| v1.0 | End of week 12 | Backtest sanity checks; config file; optional hosted link; 80%+ coverage; README, demo GIF, case study | All Musts and Shoulds green in CI; UAT checklist passed; repo public |

**Rule:** Should work starts only after every Must is green in CI. The v0.1 gate must also have passed.

## 7. Cross-cutting requirements

Every module follows the same platform rules. This lets the dashboard show any module without knowing how it works inside. It also stops one failure from spreading.

**Module platform (PLAT)**

| ID | Requirement | Priority | Release |
| --- | --- | --- | --- |
| PLAT-FR-01 | Every module returns results in one versioned output contract (JSON schema) containing at least: module name, module version, rule-spec version, as-of timestamp, status (ok / partial / unavailable), data source list, result rows, and warnings. | Must | v0.1 |
| PLAT-FR-02 | If a module or its data source fails or exceeds its timeout, the dashboard shows "unavailable" with the reason and last good as-of time for that section only, and loads every other section. | Must | v0.1 |
| PLAT-FR-03 | Each module lives in its own folder with its own data/cache, tests and version, and imports no code from any other module (the shared contract package is the only exception). | Must | v0.1 |
| PLAT-FR-04 | Results are cached per trading day; a repeat click on the same day reuses the cache unless the user requests a refresh. | Must | v0.1 |
| PLAT-FR-05 | A refresh re-runs only stale modules, runs modules in parallel, and respects a minimum refresh interval per module to stay within free API limits. | Must | v0.1 |
| PLAT-FR-06 | Each module validates its input data before running rules (schema, ranges, coverage). If fewer than 95% of the universe is fetched, the module status is "partial" and the dashboard says so. | Must | v0.1 |
| PLAT-FR-07 | Prices are split- and dividend-adjusted. On a market holiday, modules use the last completed trading session and show its date with a note. | Must | v0.1 |
| PLAT-FR-08 | Every module run logs its runtime, rows returned, API calls and cost. | Should | v0.2 |

**Launcher and dashboard (DASH)**

| ID | Requirement | Priority | Release |
| --- | --- | --- | --- |
| DASH-FR-01 | A Windows desktop icon starts everything with one command and opens the dashboard in the browser. | Must | v0.1 |
| DASH-FR-02 | Sections appear top to bottom: Economic Data, COT (placeholder), regime banner and sector rotation, Momentum, Value – PE Re-rating, Value – Long Term, confluence list, past-picks tracker, disclaimer. Sections not yet built show "Coming soon". | Must | v0.1 |
| DASH-FR-03 | Each section shows its as-of time and status. A visible "Refresh" control re-runs stale modules on demand. | Must | v0.1 |
| DASH-FR-04 | The dashboard contains no screening logic; it only calls modules and renders contract outputs. | Must | v0.1 |
| DASH-FR-05 | Changes since the previous snapshot are highlighted (new tickers, dropped tickers, new releases). | Could | v0.3 |
| DASH-FR-06 | Every stock in a module table links to an external chart page. | Should | v0.2 |

**Archive and export (ARCH)**

| ID | Requirement | Priority | Release |
| --- | --- | --- | --- |
| ARCH-FR-01 | Each refresh saves a dated snapshot (HTML + JSON) including module and rule-spec versions. | Must | v0.1 |
| ARCH-FR-02 | Any past snapshot can be opened by date. | Must | v0.1 |
| ARCH-FR-03 | A snapshot can be exported as HTML or PDF for printing. | Could | v0.3 |
| ARCH-FR-04 | The disclaimer "Personal research project, not investment advice" appears on the dashboard, in every snapshot and export, and in the README. | Must | v0.1 |

**Acceptance (sample)**

- Given the FMP source is disabled, when I click the desktop icon, then Value – PE Re-rating shows "unavailable" with the reason, and every other section loads (PLAT-FR-02).
- Given a refresh already ran today, when I click the icon again, then the dashboard is usable in under 60 s with no new API calls (PLAT-FR-04).

## 8. Functional requirements by module

The thresholds below are starter values. Exact formulas, lookbacks and edge cases are in docs/04-signal-spec.md. You can tune them there without changing this PRD. Stock modules use the S&P 500 + Nasdaq 100, about 550 tickers.

### 8.1 Economic Data (ECON) — top of the dashboard

Answers: what macro data moved recently and what's coming up?

| ID | Requirement | Priority | Release |
| --- | --- | --- | --- |
| ECON-FR-01 | Track 11 indicators: CPI (headline, core), PCE (headline, core), ISM Manufacturing PMI, ISM Services PMI, GDP (with estimate type), Fed funds target range / FOMC decision, retail sales (headline, ex-autos), light vehicle sales, jobs report (NFP, unemployment rate), weekly jobless claims (initial, 4-week average, continuing), 10Y–2Y spread. | Must | v0.1 |
| ECON-FR-02 | For each indicator show latest value, prior value, change, release date, next release date and days remaining. | Must | v0.1 |
| ECON-FR-03 | Show units and period (MoM, YoY, annualized, index level); PMIs show above or below 50 (expansion vs contraction). | Must | v0.1 |
| ECON-FR-04 | Highlight indicators releasing in the next 7 days, with release time in ET. | Must | v0.1 |
| ECON-FR-05 | If an FOMC meeting or jobs report falls in the next 7 days, flag it at the very top of the dashboard; FOMC flag shows statement (2:00 PM ET) and press conference (2:30 PM ET). | Must | v0.1 |
| ECON-FR-06 | Yield curve shows the current 10Y–2Y spread, inverted (below 0) or normal, and the 1-month trend. | Must | v0.1 |
| ECON-FR-07 | Release dates come from official calendars, not hard-coded; unknown dates show "date not confirmed". | Must | v0.1 |
| ECON-FR-08 | If no free ISM source is available, the two PMI values can be entered manually each month and are marked "manual". | Should | v0.1 |

Acceptance: given a jobs report is due in 2 days, when the dashboard loads, then the top flag shows "Jobs report · Fri 8:30 AM ET · in 2 days" and the jobless claims row shows the latest Thursday release.

### 8.2 Momentum (MOM)

Answers: which stocks are outperforming with healthy, confirmed trends? Two screens, one module.

| ID | Requirement | Priority | Release |
| --- | --- | --- | --- |
| MOM-FR-01 | Compute an RS rating 1–99 for every ticker: weighted 3/6/9/12-month return ranked against the universe (IBD-style). | Must | v0.1 |
| MOM-FR-02 | Screen A (RS + RSI): RS ≥ 80 AND RSI(14) between 50 and 70, or RSI pulling back to 40–50 while in an uptrend. Each result is tagged "strong" or "pullback". | Must | v0.1 |
| MOM-FR-03 | Screen B (RS + Ichimoku): RS ≥ 80 AND close above the cloud AND Tenkan above Kijun AND the cloud ahead is green. Bonus flag for a fresh breakout above the cloud in the last 5 trading days. | Should | v0.2 |
| MOM-FR-04 | Tables show ticker, sector, RS rating, RSI, week % change, distance from 50-day MA, ATR % and earnings date; sorted by RS rating, top 10 per screen. | Must | v0.1 |
| MOM-FR-05 | If fewer than 3 stocks qualify, the section says so instead of showing an empty table. | Must | v0.1 |
| MOM-FR-06 | Each stock shows a suggested stop reference (below Kijun or 2× ATR) as context, not advice. | Could | v0.3 |

Acceptance: RSI(14) on a fixed test series matches a reference value within 0.1. Only tickers that meet both conditions appear.

### 8.3 Value – Long Term (VLT)

Answers: which quality companies are trading cheap?

| ID | Requirement | Priority | Release |
| --- | --- | --- | --- |
| VLT-FR-01 | Screen: PE below sector median, FCF yield ≥ 5%, ROE ≥ 15%, debt/equity < 1, Piotroski F-score ≥ 7. | Should | v0.2 |
| VLT-FR-02 | Rank passing stocks by a composite value score (definition in the signal spec); show top 10. | Should | v0.2 |
| VLT-FR-03 | Table shows ticker, sector, PE vs sector median, FCF yield, ROE, debt/equity, F-score, value score and earnings date. | Should | v0.2 |
| VLT-FR-04 | Stocks with negative earnings or missing fundamentals are excluded and counted in the module's warnings. | Should | v0.2 |

### 8.4 Value – PE Re-rating (PER)

Answers: which stocks is the market paying a higher (or lower) multiple for, and is it backed by earnings?

| ID | Requirement | Priority | Release |
| --- | --- | --- | --- |
| PER-FR-01 | Healthy re-rating: forward PE up 15%+ vs its 52-week median AND forward EPS estimate rising. | Should | v0.2 |
| PER-FR-02 | Stretched: forward PE up 15%+ with flat or falling EPS estimates; listed separately and labeled "stretched". | Should | v0.2 |
| PER-FR-03 | De-rating: forward PE down 15%+ vs its 52-week median; listed separately. | Should | v0.2 |
| PER-FR-04 | Tables show ticker, sector, forward PE, 52-week median PE, % change, EPS-estimate trend and earnings date. | Should | v0.2 |

### 8.5 Supporting modules and combined views

| ID | Requirement | Priority | Release |
| --- | --- | --- | --- |
| REG-FR-01 | Regime banner: Risk-on (SPY above 50- and 200-day MA, VIX under 20), Caution (above 200-day only, or VIX 20–30), Risk-off (below 200-day, or VIX over 30). Shows S&P 500, Nasdaq, VIX and 10Y with week % change. | Should | v0.2 |
| REG-FR-02 | In Risk-off, Momentum sections carry a warning line. | Should | v0.2 |
| SECT-FR-01 | Sector rotation: 11 SPDR sector ETFs ranked by RS, with prior rank and 4-week change. | Should | v0.2 |
| EARN-FR-01 | Every module table shows each stock's next earnings date and flags dates within 10 trading days. | Should | v0.2 |
| CONF-FR-01 | Confluence list: stocks passing 2+ module screens, showing which ones; reads module outputs only. | Should | v0.2 |
| TRACK-FR-01 | Past-picks tracker: 1, 2 and 4-week returns of every flagged stock vs SPY, plus hit rate per module, built from the archive. | Could | v0.3 |
| AI-FR-01 | AI summary: about 150 words on macro and what the modules show, generated once per trading day from module output JSON only. | Could | v0.3 |
| AI-FR-02 | "Why flagged" note: one line per stock naming the rules it met, generated from rule results. | Could | v0.3 |
| AI-FR-03 | Every number in AI text must exist in module outputs; no buy/sell language; on failure the AI section shows a plain fallback and the rest loads. | Could | v0.3 |
| COT-FR-01 | COT section shows a "Coming soon" placeholder for crude oil, natural gas, gold and silver. | Must | v0.1 |

## 9. Non-functional requirements

Each item is measurable and checked by a test, log or checklist before its release.

| ID | Area | Requirement | Verified by | Release |
| --- | --- | --- | --- | --- |
| NFR-01 | Performance | Dashboard usable under 60 s from cache after clicking the icon | Launcher timing log | v0.1 |
| NFR-02 | Performance | Full refresh of all modules under 5 min on the owner's PC | Run log | v0.2 |
| NFR-03 | Reliability | One module failing or timing out never blocks another (100%) | Failure-isolation test in CI | v0.1 |
| NFR-04 | Correctness | Indicator math matches reference values (RSI within 0.1); no look-ahead bias (only data available at the as-of time) | Unit tests | v0.1 |
| NFR-05 | Data quality | No missing close for the last trading session; prices > 0; ≥ 95% universe coverage or status "partial" | Validation on every run | v0.1 |
| NFR-06 | Maintainability | Each module has its own tests and version; 80%+ coverage per module by v1.0; ruff and mypy clean | CI | v1.0 |
| NFR-07 | Compatibility | Output contract is versioned; a contract test in every module fails CI on schema drift | Contract tests | v0.1 |
| NFR-08 | API health | Live checks that yfinance, FRED and FMP still return required fields | Weekly scheduled CI job | v1.0 |
| NFR-09 | Cost | Total under $5/month; AI under $3/month with a hard monthly cap | Cost log | v0.3 |
| NFR-10 | Security | API keys only in .env or GitHub Secrets; secret scanner in pre-commit and CI | CI + pre-commit | v0.1 |
| NFR-11 | Legal | Raw third-party data never committed to the repo; data-source terms reviewed; disclaimer everywhere (ARCH-FR-04) | Repo check + snapshot test | v0.1 |
| NFR-12 | Usability | Readable in light and dark mode; tables usable at 1366 px wide; hosted view readable on a phone | UAT checklist | v1.0 |
| NFR-13 | Setup | Clone, configure .env and launch in under 5 minutes using the README | Fresh-machine test | v1.0 |
| NFR-14 | Traceability | Every snapshot records module and rule-spec versions | Snapshot test | v0.1 |

## 10. Dependencies, assumptions and risks

The biggest risk is free data: its quality and its limits. To reduce this risk, every module checks its own data. Every module also caches results for each trading day.

**External dependencies**

| Dependency | Used by | Fallback |
| --- | --- | --- |
| yfinance (prices, some fundamentals, earnings dates) | MOM, VLT, PER, REG, SECT, EARN | Cached last good data, status "partial" or "unavailable" |
| FRED API (macro series, yields, vehicle sales) | ECON | Cached last good value with its as-of date |
| Official release calendars (BLS, BEA, Census, DOL, Fed) | ECON | "Date not confirmed" |
| ISM press releases | ECON (PMIs) | Manual monthly entry (ECON-FR-08) |
| FMP free tier, SEC EDGAR (fundamentals, estimates) | VLT, PER | Module shows "unavailable" |
| Claude API | AI | Plain fallback text |

**Assumptions and risks**

| Assumption / risk | Likelihood | Impact | Mitigation | Validate by |
| --- | --- | --- | --- | --- |
| Free data is reliable enough for screening | Medium | High | Per-module validation; contract tests; "partial" status | Week 3 data spike |
| A free ISM PMI source exists | Medium | Low | Manual entry fallback | Week 2 |
| FMP free tier covers forward EPS estimates for ~550 tickers within its limits | Medium | High | Batch and cache fundamentals weekly; reduce universe for PER if needed | Week 2 spike |
| Full refresh fits in 5 minutes | Medium | Medium | Parallel modules; refresh only stale ones | Week 6 timing |
| Frequent clicks hit API rate limits | Medium | Medium | Daily cache; minimum refresh interval | Week 5 |
| Release dates shift (holidays, shutdowns) | Low | Medium | Official calendars; "date not confirmed" | Ongoing |
| Modules drift apart in output format | Medium | High | One versioned contract, tested in every module | Every PR |
| Running several isolated modules adds setup complexity | Medium | Medium | Worker processes, not servers; one start command (ADR) | Week 3 |
| AI summary states wrong numbers | Medium | High | Grounding check; fallback text | Every AI run |
| Screens produce overlapping or weak lists | Medium | Medium | Track overlap and 4-week performance from week 7 | Monthly review |
| Owner can sustain 8–10 hrs/week for 12 weeks | Medium | High | 2-week sprints with retros; MVP cut at week 6 | Each retro |

## 11. Open questions

The owner must decide each of these. Each decision goes in the doc named in the table, by the week shown.

| # | Question | Proposed default | Decide in | By |
| --- | --- | --- | --- | --- |
| Q1 | Do the v0.2 and v0.3 gates in section 6 look right? | As written | This PRD | Week 1 |
| Q2 | Show consensus forecasts next to economic releases? | No in v1.0 (no reliable free source) | Signal spec | Week 2 |
| Q3 | Keep DXY anywhere (dropped from Economic Data in vision v1.1)? | Add to regime banner market snapshot as a Could | This PRD | Week 1 |
| Q4 | Exact RS rating formula: weights for 3/6/9/12-month returns and how IPOs under 12 months are handled | IBD-style 40/20/20/20; exclude under 12 months | Signal spec | Week 2 |
| Q5 | Definition of "uptrend" for the RSI pullback case | Close above 50-day MA and 50-day above 200-day | Signal spec | Week 2 |
| Q6 | Composite value score formula and weights | Equal-weighted percentile ranks of the five metrics | Signal spec | Week 2 |
| Q7 | Sector median PE: GICS sector from which source? | yfinance sector field | Data dictionary | Week 2 |
| Q8 | Module runtime: worker processes vs local HTTP services | Worker processes with timeouts | ADR-001 | Week 2 |
| Q9 | Free ISM PMI source | ISM press release page; manual entry fallback | Data spike | Week 2 |
| Q10 | How "partial" results (under 95% coverage) are shown and used by the confluence list | Shown with warning; excluded from confluence | This PRD | Week 3 |
| Q11 | Hosted link: which data can be shown publicly given data-source terms? | Sample snapshot with fixture data only | ADR | Week 10 |

## 12. Glossary

| Term | Meaning in this product |
| --- | --- |
| As-of time | The date and time of the latest data a module used; for prices, the last completed trading session |
| ATR | Average True Range: average daily price range, used for volatility and stop context |
| Confluence | A stock passing screens in 2 or more modules |
| Core module | One of the four independent modules: Economic Data, Momentum, Value – Long Term, Value – PE Re-rating |
| De-rating | Forward PE falling 15%+ vs its 52-week median |
| F-score (Piotroski) | 0–9 score of financial strength from nine accounting tests |
| Failure isolation | One module failing never stops another from loading |
| Ichimoku cloud | Trend indicator; "above the cloud" means close above both cloud edges; Tenkan and Kijun are its fast and slow lines |
| Output contract | The versioned JSON schema every module returns |
| Partial | Module status when under 95% of the universe was fetched |
| Re-rating | Forward PE rising 15%+ vs its 52-week median; "healthy" when EPS estimates also rise, "stretched" when they don't |
| Regime | Overall market state (Risk-on, Caution, Risk-off) from SPY moving averages and VIX |
| RS rating | 1–99 rank of a stock's weighted 12-month performance vs the universe |
| RSI(14) | 14-day Relative Strength Index, 0–100 momentum oscillator |
| Rule-spec version | Version of docs/04-signal-spec.md used for a run |
| Snapshot | A dated, archived copy (HTML + JSON) of one dashboard refresh |
| Supporting module | Independent module that adds context: regime, sector rotation, earnings flags, COT |
| Universe | S&P 500 + Nasdaq 100 constituents, about 550 tickers |

## 13. Change log

| Date | Version | Change |
| --- | --- | --- |
| 2026-10-25 | 1.0 | First draft, aligned with vision v1.1, persona v1.0 and Product Roadmap v1.1 |

*Disclaimer: personal research project, not investment advice.*
