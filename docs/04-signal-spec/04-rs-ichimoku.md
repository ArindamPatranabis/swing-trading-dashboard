# Spec 4 · Momentum: RS + Ichimoku

**Module:** `momentum_rs_ichimoku` (Screen B) · **Spec version:** 0.2 · **Status:** Draft
**Owner:** _Your name_ · **Last updated:** 2026-10-29
**Source:** the owner's screener `rs_cross_detail_weekly.py` + `RS_Cross_Detail_Weekly.bat` (Stock Screener\RS-Cloud-Final), transcribed as v0.1, then changed by the owner in v0.2 (fresh Conversion Line cross, 2-week RS cross window, signal candle with entry, exit and a pending lifecycle, sector grouping). The script does not yet include the v0.2 changes.

## 1. Purpose

Find stocks that have **just started to beat the S&P 500 over the past year** and have **closed back above their short-term trend line**. The week of that close is the **signal candle**: its high is the entry and its low is the exit (SL). A signal stays on the list until price trades up to the entry, or until a weekly close below the trend line cancels it. Run at the weekend to plan the next week's swing trades.

**Question answered:** *Which stocks have a live breakout setup (lagging turned to leading, fresh close above the short-term trend), and where would I enter and exit?*

## 2. Stock selection parameters

### 2.1 Signal candle rules

A weekly candle is a **signal candle** when **all** rules are true for that week (week s).

| # | Parameter | Rule | Notes |
| --- | --- | --- | --- |
| 1 | RS recent cross | RS(55) in week s **> 1** AND (RS(55) in week s−1 **≤ 1** OR RS(55) in week s−2 **≤ 1**) | RS crossed above 1 in the signal week or the week before it, and is still above 1. A stock above 1 for 3 or more weeks is excluded |
| 2 | Conversion Line fresh cross | Weekly close in week s **>** Conversion Line in week s AND weekly close in week s−1 **≤** Conversion Line in week s−1 | The close must have **just** crossed above the line |
| 3 | Enough history | More than 57 completed weekly bars before and including week s | Needed for RS(55) in week s and the 2 weeks before |
| 4 | Current data | The stock's last weekly bar is the benchmark's last completed week | Otherwise the stock is skipped as stale (halted, delisted or missing data) |

### 2.2 Signal lifecycle (which stocks are listed)

Each run finds the **most recent signal candle** for each stock, within the downloaded history, up to and including the last completed week. Then it checks every completed week after it, in order:

| Status | Condition | Listed? |
| --- | --- | --- |
| **New** | The signal candle is the last completed week | Yes |
| **Pending** | The signal candle is older, no later week's High has reached the entry, and no later week has closed below the Conversion Line | Yes |
| **Triggered** | A later week's High **≥ Entry**: the buy-stop at the signal high would have filled | No: the trade is live. Result text names the trigger week |
| **Cancelled** | A later week **closed below** its Conversion Line (Close < Conversion Line) before the entry was reached. Wait for the next signal candle | No. Result text names the cancel week |

- **Trigger and cancel in the same week:** weekly bars can't show which came first. The High reached the entry, so the buy-stop filled: status = **Triggered**.
- **A newer signal candle replaces an older one.** The newest signal candle always sets the entry and exit.
- **RS while pending:** RS is checked only on the signal candle. A later dip of RS below 1 does not cancel a pending signal.

### 2.3 Universe filters

The module applies **no** market cap, price or volume filter. Those come from the shared **Stock selection parameters** panel (PRD PARAM-FR-01; for example market cap ≥ $2B). The module returns every New and Pending signal with its `market_cap` and `close`. The dashboard then hides rows outside the filters, with no module re-run (PRD DASH-FR-04). Average daily dollar volume comes from the shared universe data defined in the data dictionary.

## 3. Definitions and formulas

### 3.1 Timeframe: weekly bars

| Item | Definition |
| --- | --- |
| Raw data | Daily High, Low and Close for 2 years (about 104 weeks) |
| Week | Monday to Friday (pandas period `W-FRI`) |
| Weekly High | Highest daily high in the week |
| Weekly Low | Lowest daily low in the week |
| Weekly Close | Last daily close in the week |
| Week date | The week's last actual trading day (for example Thursday when Friday is a market holiday) |
| Last completed week | The week ending on the most recent Friday **before** today. A run on Saturday or Sunday uses the week just ended. A run Monday to Friday, including after Friday's close, uses the previous full week, so an unfinished week is never used |
| Price type | Split-adjusted but **not** dividend-adjusted (Yahoo `Close`, `auto_adjust=False`), so entry and stop match the prices on the broker's chart |

### 3.2 Indicators

| Metric | Formula | Notes |
| --- | --- | --- |
| RS(55) | (Close<sub>w</sub> ÷ Close<sub>w−55</sub>) ÷ (SPX<sub>w</sub> ÷ SPX<sub>w−55</sub>) | The stock's 55-week price change relative to the S&P 500's. Above 1 = beating the index over about a year. Benchmark is the S&P 500 index (`^GSPC`), not SPY |
| RS cross week | The most recent week in the window where RS went from ≤ 1 to > 1: week s if RS<sub>s−1</sub> ≤ 1, otherwise week s−1 | Shown, so you can see whether the RS cross came with the signal candle or a week earlier |
| Conversion Line (Tenkan-sen) | (Highest weekly High of last 9 weeks + Lowest weekly Low of last 9 weeks) ÷ 2 | Includes the week it is computed for |
| % above Conversion Line | (Close ÷ Conversion Line − 1) × 100, for the last completed week | Shown, not a rule |

**Week alignment:** the stock and S&P 500 weekly series are matched on the same week. Only weeks present in both are used, and "55 weeks back" means 55 matched weekly rows back.

### 3.3 Signal candle, entry and exit

| Item | Definition | Notes |
| --- | --- | --- |
| Signal candle | The most recent weekly bar that meets rules 1–3 | Can be the last completed week (New) or older (Pending) |
| Entry | **Exactly the high** of the signal candle, no buffer | A buy-stop level: the trade starts only when price reaches it |
| Exit (SL) | **Low** of the signal candle | Stop basis recorded as `signal_low` |
| Risk per share | Entry − Exit (SL) | The signal candle's range |
| Weeks pending | Number of completed weeks after the signal candle | 0 for New |
| Distance to entry | (Entry ÷ last weekly close − 1) × 100 | How far price must rise to trigger |
| Quantity | floor(Capital × Risk % ÷ Risk per share) | Calculated by the dashboard from the sizing inputs (PRD MOM-FR-07). The module never sees capital |
| Position value | Quantity × Entry | Flagged "exceeds capital" if larger than capital |

## 4. Ranking and display

- **Listed:** stocks with status New or Pending (section 2.2), with no top N.
- **Grouped by sector.** Stocks in the same sector sit together under a sector heading.
- **Within each sector:** sorted by RS(55) on the signal candle, highest first. Every listed stock has RS > 1 on its signal candle.
- **Sector order:** the sector with the highest-RS stock comes first. Stocks with no sector data go in an "Unknown" group at the end.
- **Status badge:** each row shows New or Pending (with weeks pending).

## 5. Output fields

The module returns these columns, in this order:

| # | Column | Field name | Format |
| --- | --- | --- | --- |
| 1 | Sector | `sector` | Yahoo sector; the grouping key |
| 2 | Symbol | `symbol` | |
| 3 | Stock Name | `name` | Yahoo long name, else short name |
| 4 | Industry | `industry` | Yahoo industry |
| 5 | Market Cap ($B) | `market_cap` | $ billions, 2 decimals |
| 6 | Status | `signal_status` | `new` or `pending` |
| 7 | Signal Week | `signal_week` | Date of the signal candle |
| 8 | Weeks Pending | `weeks_pending` | Integer, 0 for New |
| 9 | RS | `rs` | RS on the signal candle, 3 decimals |
| 10 | Prev Week RS | `rs_prev` | RS in week s−1, 3 decimals |
| 11 | RS 2 Weeks Ago | `rs_prev2` | RS in week s−2, 3 decimals |
| 12 | RS Cross Week | `rs_cross_week` | Date: the signal week or the week before |
| 13 | Last Close | `close` | Last completed week, 2 decimals |
| 14 | Conversion Line | `conversion_line` | Last completed week, 2 decimals |
| 15 | % Above Conv. Line | `pct_above_conversion` | Last completed week, 2 decimals |
| 16 | Entry | `entry` | Signal candle high, 2 decimals |
| 17 | Exit (SL) | `stop` | Signal candle low, 2 decimals |
| 18 | Risk per share | `risk_per_share` | Entry − Exit, 2 decimals |
| 19 | Distance to Entry % | `pct_to_entry` | 2 decimals |
| — | Stop basis | `stop_basis` | Always `signal_low` |

Quantity and position value are added by the dashboard, not the module (section 3.3).

For every input symbol, including those not listed, the module also returns `result`: `NEW`, `PENDING`, or the reason it isn't listed (section 6). This feeds the "why flagged / why not" view.

Plus the standard fields from the shared output contract: `module`, `spec_version`, `as_of`, `generated_at`, `status`, `warnings`.

## 6. Edge cases

| Case | Handling (`result` text) |
| --- | --- |
| Symbol not found, or 57 weekly bars or fewer | `No data - check symbol` |
| No signal candle in the downloaded history | `No signal candle` |
| Most recent signal candle already triggered | `Triggered <week date>` (trade live, not listed) |
| Most recent signal candle cancelled | `Cancelled <week date>: closed below Conversion Line` |
| RS(55) cannot be computed for the weeks tested | Those weeks can't be signal candles; `RS unknown` if no week can be tested |
| Weekly close exactly equal to the Conversion Line after the signal | Does **not** cancel (rule is "closes below") |
| Weekly close equal to the line, then a fresh close above it | A new signal candle; it replaces the old one |
| Week where High ≥ Entry and Close < Conversion Line | Triggered (section 2.2) |
| Signal candle High = Low (no range) | Still listed; risk per share = 0, so the dashboard shows Quantity "—" (PRD MOM-FR-07 guard) |
| Price gaps above the entry at the open | Still Triggered; the real fill may be above the entry. Not modelled |
| S&P 500 download fails | Whole run stops with "could not download S&P 500 data" (module status `unavailable`) |
| Stock's latest bar is older than the benchmark's (halted or delisted) | `Stale data - last bar <date>`; not listed, and added to `warnings` (rule 4) |
| RS exactly 1.000 on the candle | Not a signal candle (rule is "> 1") |
| No sector from Yahoo | Grouped under "Unknown", shown last |

## 7. Parameters (to become `config/momentum_rs_ichimoku.yaml`)

**Editable in the dashboard parameter panel (PRD PARAM-FR-02):** `rs_length_weeks` (default 55). A change re-runs the module on cached data. Every other value is fixed in the config file.

`rs_length_weeks: 55`, `rs_level: 1`, `rs_cross_window_weeks: 2`, `conversion_length_weeks: 9`, `benchmark: ^GSPC`, `exchange_suffix: ""` (`.NS` = India NSE, `.BO` = India BSE), `history_period: 2y`, `bar_interval: weekly (built from daily)`, `require_fresh_conversion_cross: true`, `entry_basis: signal_high`, `entry_buffer: 0`, `stop_basis: signal_low`, `cancel_on_close_below_conversion: true`, `group_by: sector`, `sort_by: rs`, `sort_order: descending`, `top_n: all`.

## 8. How the script runs today (for reference)

| Step | What happens |
| --- | --- |
| Launch | `RS_Cross_Detail_Weekly.bat` finds Python (`py`, then `python`), runs `pip install --upgrade yfinance pandas openpyxl`, then runs the script with an optional file path |
| Input | An Excel file of symbols. It uses the column named Symbol / Ticker / Stock / Code / Scrip (any case), otherwise the first column. Blanks and duplicates are removed and symbols are upper-cased. A file picker opens if no path is given |
| Data | One `yfinance` batch download of 2 years of daily bars for all symbols plus `^GSPC`. Name, sector, industry and market cap are looked up only for matches (8 parallel requests) |
| Output | `<input>_RS55W_CrossDetail_results.xlsx` next to the input, with sheets **Matches** and **All Stocks** (every symbol with its `result`). Also printed to the console |

**Not yet in the script (v0.2 changes):** the 2-week RS cross window (the script needs the cross last week), the fresh Conversion Line cross, the signal lifecycle (New / Pending / Triggered / Cancelled; the script only looks at last week), entry/exit/risk/distance columns (it has Cross Week High/Low, which match entry and exit for New signals), and sector grouping (it sorts by RS only).

In the dashboard, the shared universe (PRD: S&P 500 + Nasdaq 100) replaces the Excel input, and the JSON output contract replaces the Excel output.

## 9. Test cases (acceptance)

1. Stock 100 → 120 and S&P 500 4,000 → 4,400 over 55 weeks gives RS = 1.200 ÷ 1.100 = **1.091**.
2. Week s: RS 1.020, week s−1: RS 0.985. Close 46.00 vs Conversion Line 45.00 in week s; close 44.00 vs line 44.50 in week s−1. Week s is the last completed week → **New**.
3. Same as test 2, but the close in week s−1 was 44.80 vs line 44.50 → not a signal candle (no fresh Conversion Line cross).
4. RS 1.020 in week s, 1.005 in s−1, 0.990 in s−2, with the Conversion Line cross from test 2 → signal candle; RS cross week = s−1.
5. RS 1.020 in week s, 1.005 in s−1, 1.010 in s−2 → not a signal candle (no RS cross in the last 2 weeks).
6. 9-week highest High 50.00 and lowest Low 40.00 → Conversion Line **45.00**. Close 46.00 → % above = **2.22**.
7. Signal candle High 52.40 and Low 48.10 → Entry **52.40** (exactly the high), Exit (SL) **48.10**, risk per share **4.30**. With capital $50,000 and risk 1%: quantity = floor(500 ÷ 4.30) = **116**, position value **$6,078.40**.
8. Test 7's signal; the next week has High 51.90 and closes 50.20 above its Conversion Line → **Pending**, weeks pending = 1, still listed.
9. The week after that has High 52.40 → **Triggered** (High ≥ Entry), not listed.
10. Instead, a week closes 47.00 with its Conversion Line at 47.50 and High 49.00 → **Cancelled**, not listed until a new signal candle.
11. A week with High 52.60 that closes below its Conversion Line → **Triggered**, not Cancelled.
12. Listed AAA (Technology, RS 1.15), BBB (Energy, RS 1.09), CCC (Technology, RS 1.04), DDD (Energy, RS 1.02) are shown as Technology: AAA, CCC, then Energy: BBB, DDD.
13. A run on Saturday 2026-10-31 uses the week ending Fri 2026-10-30 as the last completed week. A run on Fri 2026-10-30 uses the week ending Fri 2026-10-23.
14. In a week where Friday is a market holiday, the week's date is the Thursday and the weekly close is Thursday's close.
15. A symbol with only 50 weeks of history (a recent IPO) → `No data - check symbol`, never listed.
16. A stock whose last weekly bar is two weeks before the benchmark's last completed week → `Stale data - last bar <date>`, not listed, and named in `warnings`.
17. Changing RS length from 55 to 40 weeks in the parameter panel re-runs the screen on cached data and records the parameter set as Custom.

## 10. Differences from PRD v1.1 (to resolve before v0.2 release)

The spec and PRD MOM-FR-01/03/04/06 describe different screens. Each difference needs a decision: change this spec, or change the PRD in the next PRD batch.

| # | Topic | PRD v1.1 | This spec | Status |
| --- | --- | --- | --- | --- |
| G1 | RS definition | RS rating 1–99: IBD-style weighted 3/6/9/12-month return ranked across the universe, **≥ 80** (MOM-FR-01, Q4) | Ratio vs S&P 500 over 55 weeks, **cross above 1 in the last 2 weeks** | Decided in spec: ratio cross only. The 1–99 rating stays for Screen A (Spec 3). PRD to change |
| G2 | Ichimoku rule | Close **above the cloud** AND Tenkan **above Kijun** AND cloud ahead **green**; bonus flag for a cloud breakout in the last 5 trading days | **Fresh close above Tenkan (9)** only. No cloud, no Kijun | Decided in spec: Tenkan cross only. PRD to change |
| G3 | Timeframe | Daily (implied by "5 trading days", 50-day MA, RSI(14)) | **Weekly**, completed weeks only | Decided in spec: weekly only. PRD to change |
| G4 | Exit (SL) | Kijun line (MOM-FR-06) | **Signal candle low** | Decided in spec; PRD to change |
| G5 | Entry | Last close (Q16) | **Signal candle high**, exactly, as a buy-stop | Decided in spec; PRD to change |
| G6 | Benchmark | SPY | `^GSPC` (S&P 500 index, price only). The difference is negligible for a price ratio | Decided: S&P 500 index. PRD wording to change for Screen B |
| G7 | Stale data | Not covered | Stale stocks are excluded with a warning (rule 4) | Decided in spec |
| G8 | Table layout | Ticker, market cap, sector, RS rating, RSI, week % change, distance from 50-day MA, ATR %, earnings date; sorted by RS, top 10 (MOM-FR-04) | Section 5 columns, **grouped by sector**, RS high to low within each sector, all New and Pending signals | Decided in spec; PRD to change |
| G9 | Universe filters | Market cap ≥ $2B, price, average dollar volume (PARAM-FR-01) | No filter in the module; the shared parameter panel applies the universe filters to the returned rows (section 2.3) | Decided; matches the PRD, no PRD change |
| G10 | Parameter panel | RS minimum, breakout window, top N (PARAM-FR-02) | Only **RS length** is editable; the rest is fixed in config (section 7) | Decided; PRD to change |
| G11 | Price adjustment | Not stated | **Split-adjusted, not dividend-adjusted** | Decided for this module; the data dictionary should state it for all price-based modules |
| G12 | Refresh cadence | Daily dashboard refresh | Weekly signal. A pending signal that triggers midweek still shows as Pending until the week completes | Decided in spec: weekly only, no daily trigger check (follows G3). Screen B results change once a week. PRD to change |
| G13 | Signal persistence | Results are recomputed each run; nothing carries over | Pending signals carry across weeks until triggered or cancelled (derived from price history, no stored state). The "since your last visit" strip (DASH-FR-05) and past-picks tracker (TRACK-FR-01) should use New / Triggered / Cancelled | Decided in spec; PRD to change |

## 11. Decisions log

| # | Question | Decision |
| --- | --- | --- |
| Q1 | Source of the rules | Owner's script `rs_cross_detail_weekly.py`, transcribed as spec v0.1 |
| Q2 | Rule 2: close above, or fresh cross above, the Conversion Line? | **Fresh cross**: above in the signal week, at or below the week before |
| Q3 | Sort order | **Group by sector**; RS highest to lowest within each sector |
| Q4 | Entry and exit | Signal candle = the week that crossed the Conversion Line. **Entry = its high, Exit (SL) = its low** |
| Q5 | Sector order on the page | **Sector with the highest-RS stock first** |
| Q6 | Must the RS cross and the Conversion Line cross happen in the same week? | **No.** The RS cross can be in the signal week or the week before (last 2 weeks) |
| Q7 | How long does a signal stay valid? | **Until price reaches the entry (signal high).** If a weekly candle closes below the Conversion Line first, the signal is cancelled; wait for the next signal candle |
| Q8 | Entry exactly at the high, or with a buffer? | **Exactly the high**, no buffer |
| Q9 | Trigger rule: High ≥ Entry or High > Entry? | **High ≥ Entry**: touching the entry counts as triggered (a buy-stop at the high fills when price reaches it) |
| Q10 | G1 · RS definition | **55-week ratio cross above 1** only; no RS rating filter on Screen B |
| Q11 | G2 · Ichimoku rule | **Fresh close above Tenkan (9)** only; no cloud, Kijun or green-cloud check |
| Q12 | G3 · Timeframe (and G12 · cadence) | **Weekly only**, completed weekly bars. Midweek triggers show at the next weekly run |
| Q13 | G9 · Universe filters | **From the owner's parameter-driven screen** (shared panel, PARAM-FR-01). The module returns all signals with market cap and close; the dashboard filters |
| Q14 | G6 · Benchmark | **S&P 500 index (`^GSPC`)**, not SPY |
| Q15 | G7 · Stale data | **Exclude** stocks whose last bar isn't the benchmark's last completed week, with a warning |
| Q16 | G10 · Parameter panel | Only **RS length** is editable on the dashboard |
| Q17 | G11 · Price adjustment | **Split-adjusted only**, so levels match the broker's chart |

## Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-10-28 | First draft, reverse-engineered from the owner's weekly RS cross + Conversion Line screener |
| 0.2 | 2026-10-29 | Owner's changes: fresh Conversion Line cross; RS cross in the signal week or the week before; signal candle with entry = its high (exactly) and exit (SL) = its low; signals stay Pending until triggered or cancelled by a weekly close below the Conversion Line; output grouped by sector (highest-RS sector first), RS high to low within each sector. Added risk, quantity, status and distance-to-entry fields, tests 2–5 and 7–12, gap G13. Resolved G1–G3 and G12: ratio cross only, Tenkan cross only, weekly only. G9: universe filters come from the shared parameter panel (section 2.3). G6: S&P 500 index; G7: stale stocks excluded (rule 4); G10: only RS length editable; G11: split-adjusted prices. Tests 16–17 added. All gaps resolved |
