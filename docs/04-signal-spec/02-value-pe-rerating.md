# Spec 2 · Value: PE Re-rating (EPS + PE)

Oct 30, 2026 · @Arindam Patranabis

## Purpose and scope

The screener returns US stocks from the owner's list whose earnings are growing and whose current PE is below their own 3-year average PE: growing companies the market now prices more cheaply than usual.

| Field | Value |
| --- | --- |
| Spec | 2 · Value: PE Re-rating (EPS + PE) |
| Version | 0.1 (draft) |
| Source | Decoded from `eps_pe_screener.py` and `EPS_PE_Screener.bat` |
| Market | United States only. No Indian or other non-US exchanges |
| Data basis | Reported (actual) EPS and daily closes; no analyst estimates |
| Related | PRD v1.2 section 8.4 (PER-FR-01 to 05), PARAM-FR-02, PLAT-FR-07 |

The rules differ sharply from PRD v1.2, which screens forward PE against its 52-week median using EPS estimates. Comparison with PRD v1.2 sets out the gaps; open question Q1 decides which definition the module follows.

## Inputs

The screener reads one Excel file (.xlsx) of US ticker symbols, handled exactly as in Spec 3.

- **How the file arrives:** as a command-line argument (a file dragged onto the .bat), or from a file-picker dialog.
- **Symbol column:** the first column headed symbol, symbols, ticker, tickers, stock, stocks, code or stock symbol (case-insensitive); otherwise the first column.
- **Cleaning:** trimmed, upper-cased, blanks and duplicates dropped, first-seen order kept.
- **Non-US symbols:** any symbol containing a dot is rejected before download with Result `Not a US symbol`. Share classes use Yahoo's dash form (`BRK-B`).
- **Removed from the original script:** the `EXCHANGE_SUFFIX` setting, the `to_ticker()` helper and the `scrip` header alias.

## Data

Everything comes from yfinance, one stock at a time, 6 stocks in parallel; no FMP or SEC EDGAR call is made.

| Item | Source and rule |
| --- | --- |
| Quarterly EPS | `Ticker.quarterly_income_stmt`, row `Diluted EPS`, else `Basic EPS`; blanks dropped, oldest to newest. Yahoo usually returns 4–5 quarters |
| Annual EPS | `Ticker.income_stmt`, same row choice. Yahoo usually returns 4 fiscal years |
| Prices | `Ticker.history`, 4 years of daily closes, `auto_adjust=False`: split-adjusted, not dividend-adjusted (PLAT-FR-07) |
| Reference data | `Ticker.info`: name, market cap and Yahoo's `trailingPE` |
| Report lag | A fiscal year's EPS counts from 60 days after its year-end date (`REPORT_LAG_DAYS`), to avoid look-ahead |
| Completed bars | Last price = the latest completed daily close; a bar dated today is dropped before the 4:00 PM ET close (new rule, as in Spec 3) |

## Metric definitions

Five metrics drive the rules; Q is the latest reported quarter and FY the latest fiscal year.

**EPS latest Q and previous Q.** The last two quarterly diluted EPS values, compared sequentially (Q vs Q−1), not year over year.

**TTM EPS.** Sum of the last 4 quarterly EPS values; blank if fewer than 4 quarters exist.

**EPS growth 3Y (%).** Compound yearly growth from the fiscal year 3 years back to the latest. Blank if fewer than 4 fiscal years exist or either value is 0 or negative.

```latex
G_{3Y} = \left( \frac{EPS_{FY}}{EPS_{FY-3}} \right)^{1/3} - 1
```

**Current PE.** Yahoo's `trailingPE`. If Yahoo returns none and TTM EPS is above 0, it is last close ÷ TTM EPS.

**Average 3Y PE.** For every trading day in the last 3 years, close ÷ the latest annual EPS already reported on that day (fiscal year-end + 60 days). Days with EPS of 0 or below are dropped. The result is the mean of the daily PEs, and needs at least 200 usable days.

```latex
\overline{PE}_{3Y} = \frac{1}{N} \sum_{d=1}^{N} \frac{P_d}{EPS^{annual}_{known\ at\ d}}
```

The current PE uses trailing-12-month EPS while the average uses annual EPS. The two are close but not like for like (see open question Q3).

## Screening rules

A stock is a MATCH only when R1, R2 and R3 are all true; every failed rule is listed in Result, joined by `; `.

| ID | Rule | Default | Fail reason shown |
| --- | --- | --- | --- |
| R1 | EPS latest Q > EPS previous Q | — | `EPS Q <= prev Q`, or `Quarterly EPS missing` if under 2 quarters |
| R2 | EPS growth 3Y > minimum | 1% | `3Y EPS growth <= 1%`, or `3Y EPS growth n/a (missing or negative EPS)` |
| R3 | Current PE < Average 3Y PE | 3 years | `PE >= 3Y avg PE`, `Current PE n/a (negative earnings?)` or `3Y PE n/a` |

- R3 has no margin: a current PE 0.1% below the average passes.
- Settings at the top of the script: `EPS_GROWTH_MIN` 1, `PE_YEARS` 3, `REPORT_LAG_DAYS` 60, `WORKERS` 6.
- A stock whose download fails gets Result `No data (<error type>)` or `No data - check symbol`; any other exception gives `Error: …`, cut to 120 characters.

## Output

The run writes `<input name>_EPS_PE_results.xlsx` next to the input file, with a frozen header row and column widths of 10 to 45 characters.

| Sheet | Rows | Columns | Sort |
| --- | --- | --- | --- |
| Matches | Stocks passing R1–R3 | `Symbol`, `Stock Name`, `Market Cap ($B)`, `Last Price`, `Current PE`, `Avg 3Y PE`, `EPS Latest Q`, `EPS Prev Q`, `EPS Growth 3Y (%)` | EPS growth 3Y, highest first |
| All Stocks | Every input symbol | The Matches columns plus `Latest Q Date` and `Result` | Input order |

- Prices and PEs to 2 decimals, EPS to 3, growth to 2, market cap in billions of US dollars to 2.
- The console shows progress per stock (`i/n`, symbol, result), the match count, the Matches table and the saved path.
- The .bat launcher works as in Spec 3: find Python, install pinned packages from `requirements.txt` instead of upgrading every run, run the script, pause.

## Edge cases, data risks and fixes

The biggest risk is that current PE and average PE are built from different sources and EPS bases, so R3 can pass or fail on a data artefact rather than on valuation.

| Case | Required behaviour | Change from original |
| --- | --- | --- |
| Current PE source | Compute last completed close ÷ TTM diluted EPS locally; do not use Yahoo `trailingPE`, which uses a live price and Yahoo's own EPS | Yes, proposed |
| Seasonal businesses | Sequential Q vs Q−1 penalises retailers and other seasonal firms (see Q2) | Open question |
| Stock split after a fiscal year | Check that statement EPS is restated for splits like the prices; if not, the historical PE is wrong by the split ratio | Yes: add a check against `Ticker.splits` |
| Stale latest quarter | Latest quarter end more than 135 days old → Result `Stale EPS - last quarter <date>`; not a match | Yes: no check before |
| Fewer than 4 fiscal years | R2 fails as n/a; Yahoo often returns exactly 4, so one missing year blocks the stock | No, documented |
| Negative EPS in any year used | R2 n/a; those days dropped from the average PE | No |
| Empty symbol list | Print "No symbols found" and stop | Yes: crashed with KeyError on `Result` |
| `.xls` input | Not supported; ask for .xlsx | Yes: failed for lack of `xlrd` |
| Yahoo rate limits | One `.info` plus three statement and price calls per stock; retry once after a pause, then `No data (rate limited)` | Yes, proposed |
| Packages | Pinned versions in `requirements.txt` | Yes: upgraded every run |

## Acceptance tests

Each test uses fixed fixture statements and prices so results do not depend on live data.

- [ ] **3Y growth:** annual EPS 2.00 then 2.66 three years later → growth 9.98%.
- [ ] **Negative base:** EPS −0.50 three years back → growth n/a, not a match.
- [ ] **Sequential EPS:** latest Q 1.10, previous 1.05 → R1 passes; 1.05 and 1.05 → fails with `EPS Q <= prev Q`.
- [ ] **Current PE:** last close 120.00, TTM EPS 6.00 → current PE 20.00.
- [ ] **Report lag:** a fiscal year ending 31 Dec is first used on 1 Mar (60 days later), never earlier.
- [ ] **Average PE minimum:** 199 usable days → `3Y PE n/a`; 200 days → computed.
- [ ] **R3 boundary:** current PE equal to average PE → `PE >= 3Y avg PE`.
- [ ] **Full match:** fixture passing R1–R3 → appears on Matches, sorted by EPS growth.
- [ ] **Stale EPS:** latest quarter ended 150 days ago → `Stale EPS`, not a match.
- [ ] **US only:** `RELIANCE.NS` → rejected before download as `Not a US symbol`.
- [ ] **Empty list:** an Excel file with a header and no symbols → message and clean exit.

## Comparison with PRD v1.2

The script and the PRD screen different ideas: the PRD looks for stocks whose multiple is rising on rising estimates, while the script finds growing companies whose multiple has fallen below its own history. The script is closest to the PRD's De-rating list, with earnings filters added.

| Topic | PRD v1.2 (8.4) | Script | Gap |
| --- | --- | --- | --- |
| Valuation measure | Forward PE (price ÷ next-12-month EPS estimate) | Trailing PE (actual EPS) | Different measure |
| Comparison base | 52-week median forward PE | 3-year mean of daily PE on annual EPS | Different window and statistic |
| Threshold | ±15% change | Any amount below the average | No size threshold |
| Earnings check | Forward EPS estimate trend (rising, flat, falling) | Actual EPS: latest Q above previous Q, 3Y growth above 1% | Actuals, not estimates |
| Lists | Three: Healthy re-rating, Stretched, De-rating (PER-FR-01 to 03) | One list of matches | Re-rating and Stretched missing |
| Direction | Mainly PE expanding | PE below average only | Opposite of PER-FR-01 |
| Table (PER-FR-04) | Ticker, market cap, sector, forward PE, 52-week median PE, % change, EPS-estimate trend, earnings date, tab counts | Market cap, last price, current PE, avg PE, EPS Q/prev Q, 3Y growth | Missing sector, % change, earnings date (EARN-FR-01), tab counts |
| Empty list (PER-FR-05) | "No stocks match the current parameters" | Empty sheet, console count 0 | Missing message |
| Parameters (PARAM-FR-02) | Forward PE change %, comparison base, EPS trend window | EPS growth minimum, PE years | Different parameter set |
| Data source | FMP free tier for estimates | yfinance only | Removes the PRD's high-risk FMP estimates dependency |
| Universe | S&P 500 + Nasdaq 100, $2B+ filter | Owner's Excel list, no filters | No universe filters |
| Delivery | Dashboard module, JSON output contract | Standalone Excel | Not on the module platform yet |

One practical upside: the script needs no analyst estimates, which the PRD's risk table rates Medium likelihood, High impact for the free FMP tier.

## Open questions

The owner decides each of these; proposed defaults apply until then.

| # | Question | Proposed default |
| --- | --- | --- |
| Q1 | Does this script's rule set replace PRD 8.4, or become a fourth list ("Below historical PE") beside the PRD's three? | Resolved 2026-10-30: replaces PRD 8.4 in PRD v1.3; module renamed Value – PE vs History |
| Q2 | Compare the latest quarter with the same quarter last year instead of the previous quarter, to remove seasonality? | Year over year |
| Q3 | Put current and average PE on the same EPS basis (both annual, or both TTM)? | Current PE on TTM; keep annual for history, since Yahoo gives only 4–5 quarters |
| Q4 | Require a minimum discount, for example current PE at least 15% below the average? | 0% for now, as a parameter |
| Q5 | Mean or median for the 3-year PE? A median resists spikes when EPS is near zero | Median |
| Q6 | Add sector, earnings date and % below average to the output, as PER-FR-04 lists? | Yes |
| Q7 | Should the 3Y growth minimum stay at 1%, which barely excludes flat earnings? | Keep 1%, as a parameter |

## Change log

| Date | Version | Change |
| --- | --- | --- |
| 2026-10-30 | 0.1 | First draft. Decoded R1–R3 from the existing script and launcher; US-only scope; proposed local current PE, split, stale-EPS and rate-limit rules; compared with PRD v1.2 section 8.4; open questions Q1–Q7 |

*Personal research project, not investment advice.*
