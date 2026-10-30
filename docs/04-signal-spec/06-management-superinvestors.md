# Spec 6 · Management Score and Super Investors

**Module:** `management_superinvestors` (supporting module) · **Spec version:** 0.1 · **Status:** Draft
**Owner:** _Your name_ · **Last updated:** 2026-10-30
**Source:** owner requirement of 2026-10-29: show a Management score and the number of Super investors invested for every stock. The formula and investor list were reviewed and accepted by the owner on 2026-10-30.

## 1. Purpose

Add two context columns to **every stock table** (Momentum Screen A and B, PE Re-rating, Value – Long Term, confluence list):

- **Management score (0–100):** how well management allocates capital and how aligned it is with shareholders, from free SEC data.
- **Super investors:** how many well-known investors from a fixed list hold the stock, from their quarterly SEC 13F filings.

**Question answered:** *Is this company run well, and do investors I respect own it?*

These columns are **display only**. They never decide which stocks a screen selects (PRD DASH-FR-04). Like the earnings flag, this is a separate module: one module failing doesn't stop the others (PRD PLAT-FR-02).

## 2. Management score

### 2.1 Components

The score adds up five components, worth 100 points in total.

| # | Component | Weight | What it shows |
| --- | --- | --- | --- |
| 1 | ROIC level | 25 | How much profit management earns on the capital it uses |
| 2 | ROIC trend | 15 | Whether that return is improving or decaying |
| 3 | Insider ownership | 20 | How much of the company management and directors own |
| 4 | Net insider buying (12 months) | 20 | Whether insiders are buying or selling with their own money |
| 5 | Share count change (3 years) | 20 | Buybacks (fewer shares) vs dilution (more shares) |

### 2.2 Formulas

| Metric | Formula | Notes |
| --- | --- | --- |
| ROIC | NOPAT ÷ invested capital | Latest fiscal year (FY0) |
| NOPAT | EBIT × (1 − effective tax rate) | Tax rate = income tax ÷ pre-tax income, clamped to 0–35%; 21% if not computable |
| Invested capital | Total debt + total equity − cash and equivalents | Year-end balance sheet |
| ROIC trend | ROIC FY0 − average ROIC of FY−1 to FY−4 | In percentage points (pp) |
| Insider ownership | Shares held by officers and directors ÷ shares outstanding | yfinance `heldPercentInsiders`, latest available |
| Net insider buying | Σ value of open-market buys − Σ value of open-market sells, last 12 months | SEC Form 4, transaction codes **P** (buy) and **S** (sell) only. Option exercises, grants and gifts are ignored |
| Net insider buying % | Net insider buying ÷ market cap × 100 | |
| Share count change | (Diluted shares FY0 ÷ diluted shares FY−3)^(1/3) − 1 | Compound annual rate. Negative = buybacks |

### 2.3 Points

| Component | Points |
| --- | --- |
| ROIC level | ≥ 20%: **25** · 15% to < 20%: **20** · 10% to < 15%: **15** · 5% to < 10%: **8** · < 5% or negative: **0** |
| ROIC trend | ≥ +2 pp: **15** · −2 pp to < +2 pp: **10** · −5 pp to < −2 pp: **5** · < −5 pp: **0** |
| Insider ownership | ≥ 10%: **20** · 5% to < 10%: **15** · 1% to < 5%: **10** · 0.1% to < 1%: **5** · < 0.1%: **0** |
| Net insider buying | Net buying (> 0): **20** · no open-market trades: **10** · net selling < 0.1% of market cap: **5** · net selling ≥ 0.1% of market cap: **0** |
| Share count change | ≤ −2% a year: **20** · −2% to < 0%: **15** · 0% to < +2%: **8** · ≥ +2% a year: **0** |

**Score** = sum of points. **Grade:** 80–100 Strong · 60–79 Good · 40–59 Mixed · 0–39 Weak.

**Missing data:** if 3 or 4 components are available, the score is rescaled: (points earned ÷ points possible) × 100, rounded, and marked "partial". With fewer than 3 components the score is `null` and shows "—".

**Financials** (banks, insurers): debt is their raw material, so ROIC is not meaningful. For stocks in the Financials sector, **ROE** (net income ÷ average equity) replaces ROIC in components 1 and 2, with the same point bands.

## 3. Super investors

### 3.1 Investor list

A configurable list in `config/superinvestors.yaml`. Each entry has a display name and its SEC CIK number (the CIK is looked up once and recorded in the data dictionary). Starter list for the owner to edit:

| # | Investor | Firm (13F filer) |
| --- | --- | --- |
| 1 | Warren Buffett | Berkshire Hathaway |
| 2 | Seth Klarman | Baupost Group |
| 3 | Bill Ackman | Pershing Square Capital Management |
| 4 | David Tepper | Appaloosa Management |
| 5 | Stanley Druckenmiller | Duquesne Family Office |
| 6 | Li Lu | Himalaya Capital Management |
| 7 | David Einhorn | Greenlight Capital |
| 8 | Dan Loeb | Third Point |
| 9 | Chuck Akre | Akre Capital Management |
| 10 | Tom Gayner | Markel Group |
| 11 | Prem Watsa | Fairfax Financial Holdings |
| 12 | Howard Marks | Oaktree Capital Management |
| 13 | Mohnish Pabrai | Dalal Street LLC |
| 14 | Terry Smith | Fundsmith |
| 15 | Chris Hohn | TCI Fund Management |

### 3.2 Count rule

| Item | Definition |
| --- | --- |
| Holding | The stock appears in the investor's latest 13F-HR filing as a common-share position (share class `SH`) with value > 0. Option rows (`PUT`, `CALL`) don't count |
| Latest filing | The most recent quarter the investor has filed. If an amendment restates the holdings, the amendment is used |
| Super investor count | Number of investors on the list holding the stock |
| Change | Count this quarter − count last quarter, for example +2 |
| Report quarter | The quarter-end date of the filings used, for example "Q3 2026" |
| Matching | 13F filings list securities by CUSIP. CUSIPs are mapped to tickers with a CUSIP–ticker table (source decided in the data dictionary) |

**Timing:** investors must file within 45 days after each quarter ends. Until an investor files for the new quarter, their previous filing is used, and the row notes it ("2 of 15 filed for Q3 2026").

## 4. Display

| Column | Shows | Hover |
| --- | --- | --- |
| Mgmt score | Score and grade, for example **72 · Good**; "partial" tag when rescaled | Points for each component with its value, for example "ROIC 18.4% → 20/25" |
| Super investors | Count, quarter and change, for example **4 · Q3 2026 · +1** | Names of the investors holding it |

These columns are never used as filters (decision Q8). They are not used for sorting either.

## 5. Output fields

One row per ticker in the universe:

| # | Field name | Format |
| --- | --- | --- |
| 1 | `symbol` | |
| 2 | `mgmt_score` | Integer 0–100, or `null` |
| 3 | `mgmt_grade` | `strong` / `good` / `mixed` / `weak`, or `null` |
| 4 | `mgmt_partial` | true if rescaled |
| 5 | `mgmt_components` | Object: value and points for each of the five components |
| 6 | `superinvestor_count` | Integer |
| 7 | `superinvestor_names` | List of display names |
| 8 | `superinvestor_change` | Integer vs previous quarter |
| 9 | `report_quarter` | For example `2026-09-30` |
| 10 | `filers_current` | Number of listed investors who have filed for `report_quarter` |

Plus the standard fields from the shared output contract: `module`, `spec_version`, `as_of`, `generated_at`, `status`, `warnings`.

## 6. Edge cases

| Case | Handling |
| --- | --- |
| Invested capital ≤ 0 | ROIC not meaningful; component 1 and 2 missing |
| Fewer than 5 years of ROIC history | Component 2 missing |
| Fewer than 4 years of share counts (FY0 and FY−3) | Component 5 missing |
| No insider ownership figure | Component 3 missing |
| No Form 4 filings in 12 months | "No open-market trades": 10 points (not missing) |
| Recent IPO or spin-off | Usually under 3 components → score `null` |
| Several share classes (for example class A and C) | Share counts and 13F positions are combined across classes of the same company |
| CUSIP with no ticker match | Holding ignored; listed in warnings |
| SEC EDGAR unavailable | Module status `unavailable`; both columns show "—" and every module table still loads |

## 7. Parameters (to become `config/management_superinvestors.yaml`)

`mgmt_weights: {roic: 25, roic_trend: 15, insider_ownership: 20, insider_buying: 20, share_change: 20}`, `roic_trend_years: 5`, `share_change_years: 3`, `insider_window_months: 12`, `insider_codes: [P, S]`, `min_components: 3`, `financials_use_roe: true`, `superinvestor_list: config/superinvestors.yaml`, `refresh: weekly (scores), daily check for new 13F and Form 4 filings`.

## 8. Test cases (acceptance)

1. EBIT 500, tax rate 21%, debt 800, equity 1,500, cash 300 → NOPAT 395, invested capital 2,000, ROIC **19.75%** → **20** points.
2. Diluted shares 1,000 three years ago and 940 now → share change **−2.04% a year** → **20** points.
3. ROIC 20 + trend 10 + insider ownership 3% (10) + no insider trades (10) + share change 20 → score **70 · Good**.
4. Four components available earning 60 of 80 possible points → score **75**, marked partial.
5. Only 2 components available → score `null`, shown as "—".
6. A bank with ROE 14% gets **15** points for component 1 from ROE, not ROIC.
7. Insiders sold $30M of stock in 12 months, market cap $20B → net selling 0.15% → **0** points for component 4.
8. An option exercise followed by a sale (codes M and S): only the S sale counts.
9. An investor holds call options on a stock but no shares → not counted.
10. 4 listed investors hold a stock this quarter and 3 held it last quarter → shows **4 · Q3 2026 · +1**.

## 9. Decisions log

| # | Question | Decision |
| --- | --- | --- |
| Q1 | Where the columns appear | Every stock table, display only (owner, 2026-10-29) |
| Q2 | Management score source | Own score from free SEC data (owner, 2026-10-29) |
| Q3 | Super investor source | Own configurable list, counted from SEC 13F (owner, 2026-10-29) |
| Q4 | Component weights and point bands | **Accepted as proposed** in section 2 (owner, 2026-10-30) |
| Q5 | Investor list | **Start with the 15 names** in section 3.1. Each firm's CIK and current 13F filing are confirmed when the list is set up; a firm that no longer files is removed (owner, 2026-10-30) |
| Q6 | Insider ownership source | **yfinance** `heldPercentInsiders` (owner, 2026-10-30) |
| Q7 | CUSIP–ticker mapping source | Open. Proposed: OpenFIGI (free API, results cached), because SEC's list of 13F securities has CUSIPs and issuer names but no tickers. Decide in the data dictionary |
| Q8 | Should these columns ever become filters (for example "Super investors at least 2")? | **No**, display only (owner, 2026-10-30) |

## Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-10-30 | First draft from the owner's requirement: Management score (five components from SEC data) and Super investor count (13F, configurable list). Owner review: weights and list accepted, yfinance for insider ownership, never a filter; CUSIP mapping still open |
