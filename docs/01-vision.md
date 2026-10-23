# 01 · Vision Board & Lean Canvas

**Product:** Swing Trading Dashboard — weekly newsletter
**Owner:** _Your name_ · **Version:** 1.0 · **Last updated:** 2026-10-23
**Status:** Approved for build (Phase 0)

---

## Vision statement

> Every Saturday morning, one email tells me what moved the macro picture, which stocks are being re-rated, and which setups are worth a look for the next 2–6 weeks — with no manual screening.

---

## Vision board

| Target group | Needs | Product | Goals |
| --- | --- | --- | --- |
| Part-time swing trader (me) who holds positions 2–6 weeks and researches on weekends | Cut weekend research from 3–5 hours to under 45 minutes | Automated weekly newsletter (email) + Streamlit dashboard | **Personal:** faster, more consistent weekly research |
| Later: other retail swing traders with the same weekend routine | One consistent, rules-based shortlist instead of five separate screeners | Five modules: US economic data, PE re-rating, RS + RSI, RS + Ichimoku cloud, value investing | **Career:** a portfolio project showing product ownership, data engineering and applied AI |
| | Macro context before Monday's open | Plus: market regime banner, sector rotation, earnings flags, past-picks tracker | **Learning:** test which screens actually work, using my own data |
| | Confidence the data is correct and on time | Runs itself every Saturday via GitHub Actions; free data sources | |

---

## Lean canvas

| Box | Content |
| --- | --- |
| **1. Problem** | (1) Screening five lenses by hand across ~550 stocks takes 3–5 hours every weekend. (2) Results are inconsistent week to week because rules live in my head. (3) No record of past picks, so I can't tell which screens work. |
| **Existing alternatives** | Finviz / TradingView screeners, IBD and paid newsletters, manual spreadsheets, scattered macro calendars. |
| **2. Customer segment** | Primary: me, a part-time swing trader. Future: retail swing traders who review markets on weekends. |
| **Early adopter** | Me — first user, product owner and tester. |
| **3. Unique value proposition** | Macro + valuation + momentum + trend + value in **one** rules-based weekly email, with a "confluence list" of stocks that pass several screens and a tracker that scores past picks. |
| **High-level concept** | "A personal IBD-style research desk, delivered every Saturday." |
| **4. Solution** | Python pipeline on a weekly schedule: fetch data → validate → run 5 screens → AI-written summary (numbers only from code) → HTML email + dashboard → archive for the feedback loop. |
| **5. Channels** | Email to my inbox; Streamlit dashboard link; GitHub repo, README and LinkedIn post for the portfolio audience. |
| **6. Revenue streams** | None — personal tool. Value is time saved, better decisions and career leverage. A paid tier is out of scope for v1.0. |
| **7. Cost structure** | Target under $5/month: free data (yfinance, FRED, FMP free tier), free GitHub Actions and Streamlit Community Cloud, ~$1–3/month AI API. Main cost: my time, ~8–10 hrs/week for 12 weeks. |
| **8. Key metrics** | Research time under 45 min/week · 100% on-time delivery by Sat 8:00 AM CT · pipeline under 15 min · 4-week return of flagged stocks vs S&P 500 · test coverage 80%+. |
| **9. Unfair advantage** | Rules tuned to my own trading style, plus my own pick-performance history that no generic screener has. |

---

## Scope boundaries

**In scope (v1.0):** 5 modules, regime banner, sector rotation, earnings flags, archive, past-picks tracker, AI summary, email, dashboard.

**Out of scope:** placing trades, broker integration, intraday alerts, personalized buy/sell advice, multi-user subscriptions.

---

## Top risks and assumptions

| Assumption / risk | How I'll test or reduce it |
| --- | --- |
| Free data is reliable enough for weekly screening | Data validation checks on every run; contract tests on APIs |
| The five screens produce useful, non-overlapping lists | Track overlap and 4-week performance from week 7 onward |
| I can keep 8–10 hrs/week for 12 weeks | 2-week sprints with a retro; MVP cut at week 6 |
| AI summary may state wrong numbers | Grounding check: every number must exist in the computed data |

---

_Disclaimer: personal research project, not investment advice._
