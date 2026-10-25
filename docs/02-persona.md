# 02 · Persona & User Journey

**Product:** Swing Trading Dashboard — on-demand research dashboard
**Owner:** _Your name_ · **Version:** 1.0 · **Last updated:** 2026-10-23
**Status:** Draft for review (Phase 0)
**Related:** [01-vision.md](01-vision.md)

---

## 1. Primary persona

### "The After-Hours Swing Trader"

| | |
| --- | --- |
| **Who** | Me — a working professional who trades US stocks part-time |
| **Trading style** | Swing trading; holds positions 2–6 weeks; mostly long positions |
| **Universe** | S&P 500 and Nasdaq 100 stocks |
| **Experience** | Comfortable with technical indicators (RS, RSI, Ichimoku) and basic valuation (PE, FCF yield) |
| **When I research** | Irregular: early mornings, evenings after work, weekends, and right before big economic releases |
| **Time available** | 30–60 minutes on a weekday; 2–3 hours on a weekend |
| **Devices** | Windows PC (main); phone for quick checks |
| **Current tools** | TradingView / Finviz screeners, broker platform, news sites, economic calendar websites, spreadsheets |
| **Tech comfort** | Learning Python and Git; codes with AI help |

> _"I don't need more data. I need the same rules applied the same way every time, in one place, whenever I have 30 minutes."_

### Goals

1. Know the macro picture before risking money: what was just released, and what's coming this week.
2. Find a short list of strong stocks (momentum) and fairly priced quality stocks (value) without screening by hand.
3. Spot stocks that pass more than one lens, since those deserve the deepest look.
4. Avoid surprises: earnings dates, FOMC meetings and jobs reports inside the holding period.
5. Learn over time which screens actually work for me.

### Frustrations (pain points)

| # | Pain point | Impact |
| --- | --- | --- |
| P1 | Research is spread across 5+ websites and tools | 3–5 hours per session; easy to skip a step |
| P2 | Screening rules live in my head and change by mood | Inconsistent shortlists week to week |
| P3 | Economic releases are easy to miss or forget the timing of | Entering a trade right before CPI, NFP or FOMC |
| P4 | Earnings dates are checked one stock at a time | Holding through an earnings gap by accident |
| P5 | No quick "check now" option on a busy weekday | Research only happens in long blocks, so opportunities are missed |
| P6 | No record of past picks and how they performed | Can't tell which screens deserve trust |
| P7 | Hard to tell if the overall market supports buying | Taking momentum trades in weak markets |

### Needs → product features

| Need | Pain point | Module / feature |
| --- | --- | --- |
| See macro releases and next dates at a glance | P3 | **Economic Data** (top of dashboard) |
| Strong, trending stocks in one list | P1, P2 | **Momentum** (RS + RSI, RS + Ichimoku) |
| Quality stocks at fair prices | P1, P2 | **Value – Long Term** |
| Stocks gaining or losing valuation support | P1, P2 | **Value – PE Re-rating** |
| Stocks passing several lenses | P1 | Confluence list |
| Warning about upcoming earnings | P4 | Earnings calendar flags |
| Market health check before buying | P7 | Market regime banner, sector rotation |
| Check any time in one click | P5 | Desktop icon, on-demand refresh, caching |
| Proof of which screens work | P6 | Archive + past-picks tracker |
| Commodity positioning (later) | — | COT report module (placeholder) |

### Jobs to be done

- **When** I have 30 spare minutes on a weekday, **I want to** see what changed in the market and in my screens, **so I can** decide whether anything needs my attention today.
- **When** a big release (CPI, NFP, FOMC) is coming, **I want to** know the date and time in advance, **so I can** avoid opening new positions right before it.
- **When** I plan trades for the coming weeks, **I want** a short, ranked list of candidates with earnings dates, **so I can** spend my time on charts and risk, not on screening.
- **When** I review my process, **I want to** see how past picks performed by module, **so I can** keep the rules that work and drop those that don't.

---

## 2. Secondary persona (future)

| | |
| --- | --- |
| **Who** | A fellow retail swing trader, or a recruiter/hiring manager reviewing the GitHub project |
| **Need** | Trader: a ready-made, configurable research dashboard. Recruiter: quick evidence of product thinking and clean engineering |
| **Implication** | Configurable thresholds and watchlists (later); a clear README, demo GIF and docs folder (now) |

---

## 3. User journey — current state (today)

A typical full research session, without the product.

| Stage | 1. Trigger | 2. Macro check | 3. Screening | 4. Shortlist | 5. Deep dive | 6. Decide | 7. Review |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **What I do** | Find free time; decide to research | Open economic calendar sites; look up recent CPI, jobs, Fed news | Run separate screeners for momentum, value and PE; copy results | Merge lists in a spreadsheet; remove duplicates | Check charts, earnings dates, news one stock at a time | Pick 2–5 candidates; set alerts | Rarely done; no record kept |
| **Tools** | — | 2–3 websites | Finviz, TradingView | Excel | TradingView, broker, news | Broker | None |
| **Time** | — | 30–45 min | 60–90 min | 30 min | 60–90 min | 15 min | 0 |
| **Feeling** | 🙂 Motivated | 😐 Scattered | 😩 Tedious | 😩 Tedious | 🙂 Engaged | 😟 Unsure | 😕 Guilty |
| **Pain points** | P5 | P1, P3 | P1, P2 | P1, P2 | P4 | P7 | P6 |

**Total:** about 3–5 hours. The most valuable stage (deep dive) gets squeezed by the most tedious ones (macro check, screening, merging).

---

## 4. User journey — future state (with the dashboard)

| Stage | 1. Trigger | 2. Launch | 3. Macro check | 4. Market health | 5. Candidates | 6. Deep dive | 7. Decide | 8. Review |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **What I do** | Have 30+ spare minutes, any day | Click the desktop icon | Read the Economic Data section at the top; see releases due in the next 7 days | Check the regime banner and sector rotation | Scan Momentum, PE Re-rating and Value lists; start with the confluence list | Open charts only for shortlisted stocks; earnings dates already shown | Pick 2–5 candidates | Check the past-picks tracker |
| **Dashboard feature** | — | One-click launch, cached results | Economic Data module, FOMC/NFP flag | Regime banner, sector rotation | Core modules, confluence list, earnings flags | Links to charts | — | Archive, past-picks tracker |
| **Time** | — | Under 1 min | 3–5 min | 2 min | 10 min | 20–30 min | 5 min | 3 min |
| **Feeling** | 🙂 Motivated | 😀 Easy | 🙂 Informed | 🙂 Confident | 😀 Focused | 🙂 Engaged | 🙂 Confident | 😀 Learning |
| **Pain point solved** | P5 | P1, P5 | P3 | P7 | P1, P2, P4 | P4 | P7 | P6 |

**Total:** about 45 minutes, with most of it spent on the deep dive and decisions.

---

## 5. Key scenarios

| # | Scenario | What the dashboard must do |
| --- | --- | --- |
| S1 | **Weekday quick check** (Tuesday evening, 30 min) | Open in under 60 seconds from cache; highlight what's new since my last visit |
| S2 | **Before a big release** (Thursday before a jobs-report Friday) | Flag NFP at the top with date and time; show the latest jobless claims |
| S3 | **Weekend planning** (Saturday, 2 hours) | Full refresh; complete module lists, confluence list and earnings flags for the next 2–6 weeks |
| S4 | **FOMC week** | Flag the meeting date, statement time (2:00 PM ET) and press conference (2:30 PM ET) |
| S5 | **A data source is down** | Show "unavailable" for that one module; every other module still loads |
| S6 | **Monthly review** | Show 1, 2 and 4-week returns of past picks vs S&P 500, by module |

---

## 6. Opportunities for the backlog

These insights become epics and user stories in the backlog (artifact 8).

| Insight from the journey | Backlog item | Epic |
| --- | --- | --- |
| Macro checking is scattered and timing is easy to miss | Economic Data section with next-release countdown and 7-day highlight | E2 Macro module |
| Screening and merging is the most tedious stage | Automated core modules plus confluence list | E3, E4 |
| Earnings are checked one stock at a time | Earnings date column on every module table | E4 |
| No quick check option on busy days | Desktop icon launch with cached results | E6 Dashboard |
| "What's new since last time?" | Highlight changes since the previous snapshot | E6 Dashboard |
| Review never happens | Past-picks tracker built on the archive | E8 Performance tracking |
| One failure shouldn't block research | Failure isolation per module | E9 DevOps and quality |

---

_Disclaimer: personal research project, not investment advice._
