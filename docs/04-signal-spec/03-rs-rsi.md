# Spec 3 · Momentum: RS Cross + RSI (daily)

Oct 30, 2026 · @Arindam Patranabis

## Purpose and scope

The screener returns US stocks from the owner's list whose 55-day relative strength against the S&P 500 crossed above 1 on the latest completed day while RSI(14) is above 60. It adds a Y/N flag for whether each stock is also beating its own sector.

| Field | Value |
| --- | --- |
| Spec | 3 · Momentum: RS Cross + RSI (daily) |
| Version | 0.1 (draft) |
| Source | Decoded from `rs_rsi_cross_screener.py` and `RS_RSI_Cross_Screener.bat`, plus requirement R5 and the US-only decision |
| Market | United States only. No Indian or other non-US exchanges |
| Timeframe | Daily bars, end of day |
| Related | PRD v1.2 (MOM-FR-01 to 07, PLAT-FR-07), Spec 4 RS + Ichimoku |

This rule set differs from PRD v1.2 Screen A (see Differences from PRD Screen A). Whether it replaces Screen A or runs beside it is open question Q1.

## Inputs

The screener reads one Excel file (.xlsx) of US ticker symbols chosen by the owner.

- **How the file arrives:** as a command-line argument (a file dragged onto the .bat), or from a file-picker dialog when no argument is given.
- **Symbol column:** the first column whose header, trimmed and lower-cased, is one of symbol, symbols, ticker, tickers, stock, stocks, code or stock symbol. If none match, the first column is used.
- **Cleaning:** values are trimmed and upper-cased; blanks and duplicates are dropped, keeping first-seen order.
- **Ticker format:** symbols are sent to Yahoo Finance as listed, with no exchange suffix added. Share classes use Yahoo's dash form (`BRK-B`, not `BRK.B`).
- **Non-US symbols:** any symbol containing a dot is rejected before download with Result `Not a US symbol`, because Yahoo would otherwise return data for exchanges such as `.NS` and screen them against the S&P 500.
- **Removed from the original script:** the `EXCHANGE_SUFFIX` setting, the `to_ticker()` helper and the `scrip` header alias.

## Data

All prices come from yfinance as one year of daily bars, downloaded in a single batch with the benchmark and the 11 sector ETFs.

| Item | Rule |
| --- | --- |
| Source | yfinance `download`, `period="1y"`, `interval="1d"` |
| Fields | Open, High, Low, Close. High and Low are new; the original script used Close only, and ATR needs them |
| Adjustment | `auto_adjust=False`: split-adjusted, not dividend-adjusted, so levels match the broker chart (PLAT-FR-07) |
| Benchmark | `^GSPC` (S&P 500 index). If it fails to download, the run stops with an error |
| Sector indices | XLK, XLV, XLF, XLY, XLP, XLC, XLE, XLU, XLRE, XLB, XLI |
| Completed bars only | The latest bar used is the last completed US session. A bar dated today is dropped until the 4:00 PM ET close (the original script's `SKIP_TODAY_IF_MARKET_OPEN` default of False is changed) |
| Date alignment | Ratios use only dates on which both series traded (inner join) |
| Reference data | Name, sector, industry and market cap from `yf.Ticker().info`, fetched for matching stocks only, 8 threads |

## Indicator definitions

Four indicators drive the screen, all on daily closes unless stated; t is the latest completed bar.

**RSI(14), Wilder smoothing.** Gains and losses are smoothed with an exponential average, alpha = 1/14, matching TradingView. If the average loss is 0, RSI is 100.

```latex
RSI_t = 100 - \frac{100}{1 + \dfrac{\text{avg gain}_t}{\text{avg loss}_t}}
```

**RS vs S&P 500 (55 days).** Above 1 means the stock gained more than the S&P 500 over the last 55 trading days.

```latex
RS_t = \frac{C_t / C_{t-55}}{SPX_t / SPX_{t-55}}
```

**Sector RS (55 days).** The same ratio with the stock's sector ETF in place of the S&P 500. It equals the stock's RS vs the S&P 500 divided by the sector ETF's RS vs the S&P 500.

```latex
SectorRS_t = \frac{C_t / C_{t-55}}{ETF_t / ETF_{t-55}}
```

**ATR(14), Wilder smoothing.** True Range is the largest of high minus low, high minus previous close, and previous close minus low. ATR is its Wilder average (alpha = 1/14), in dollars. ATR % = ATR ÷ close × 100.

```latex
TR_t = \max(H_t - L_t,\ |H_t - C_{t-1}|,\ |L_t - C_{t-1}|)
```

## Screening rules

A stock is a MATCH only when R1, R2 and R3 are all true on bar t and R4 holds; the result is an event (a fresh cross), not a standing state.

| ID | Rule | Default | Fail reason shown |
| --- | --- | --- | --- |
| R1 | RSI(14) > RSI minimum | 60 | `RSI <= 60` |
| R2 | RS(55) on bar t > RS level | 1 | `RS <= 1` |
| R3 | RS(55) on bar t−1 ≤ RS level (fresh cross) | 1 | `RS already above 1 the day before (no fresh cross)` |
| R4 | More than RS length + 1 bars of history (at least 57) | 57 bars | `No data - check symbol` |

- Bar t−1 is the previous date on which both the stock and the S&P 500 traded.
- If RS on bar t or t−1 cannot be computed, the reason is `RS unknown`.
- All fail reasons are listed, joined by ` ;  `. R2 and R3 are checked in order, so a stock below 1 shows only `RS <= 1`.
- Settings live at the top of the script: `RSI_LENGTH` 14, `RSI_MIN` 60, `RS_LENGTH` 55, `RS_LEVEL` 1, `BENCHMARK` `^GSPC`.

## R5 · Sector RS flag

Each matching stock gets `Beats Sector` = Y when its 55-day Sector RS on bar t is above 1, and N when it is 1 or below.

- **Type:** a state on bar t, not a fresh cross.
- **Role:** informational only. It never removes a stock from Matches.
- **Scope:** Matches sheet only, because sector lookups are made only for matching stocks.
- **Blank flag:** when Yahoo returns no sector, the sector has no mapped ETF, or the ETF has too little data. The column `Sector ETF` then shows the reason (`sector unknown` or `no ETF data`).
- **Columns added:** `Sector ETF`, `Sector RS (55d)` to 3 decimals, `Beats Sector`.

| Yahoo sector | Sector ETF |
| --- | --- |
| Technology | XLK |
| Healthcare | XLV |
| Financial Services | XLF |
| Consumer Cyclical | XLY |
| Consumer Defensive | XLP |
| Communication Services | XLC |
| Industrials | XLI |
| Energy | XLE |
| Utilities | XLU |
| Real Estate | XLRE |
| Basic Materials | XLB |

## R6 · Entry, 2×ATR stop and quantity (proposed)

Proposed, not yet confirmed: each match gets an entry at the last close, a stop at entry minus 2 × ATR(14), and a quantity that risks the same dollar amount on every trade.

```latex
\text{Stop} = \text{Entry} - 2 \times ATR_{14}
```

```latex
\text{Quantity} = \left\lfloor \frac{\text{Capital} \times \text{Risk \%}}{\text{Entry} - \text{Stop}} \right\rfloor
```

The stop scales with each stock's normal daily range, so a volatile stock gets more room and a smaller position. 1× ATR sits inside daily noise; 3× ATR gives more room but a smaller position for the same risk.

| Item | Rule |
| --- | --- |
| Entry | Close on bar t |
| Stop | Entry − 2 × ATR(14), Wilder; set once at entry, not trailing |
| Capital and Risk % | Settings `CAPITAL` and `RISK_PCT`; sample default $50,000 at 1%. Real values stay in a local file that is never committed (NFR-15) |
| Guards | Capital > 0 and risk between 0.25% and 3%, else quantity is blank with a warning; position value above capital is flagged `exceeds capital` |
| Columns added | `ATR %`, `Entry`, `Exit (SL)`, `Quantity`, `Position ($)` |

Worked example: entry $158.40 and ATR $4.595 give a stop of $149.21. Risking $500 ($50,000 × 1%) over $9.19 gives 54 shares, a $8,554 position.

A stop is a trigger, not a guaranteed price; a gap down, for example on earnings, can fill below it. Planning aid from the owner's own rules, not advice.

## Output

The run writes `<input name>_RS_RSI_Cross_results.xlsx` next to the input file, with a frozen header row and column widths of 10 to 45 characters.

| Sheet | Rows | Columns | Sort |
| --- | --- | --- | --- |
| Matches | Stocks passing R1–R4 | `Symbol`, `Stock Name`, `Sector`, `Industry`, `Market Cap ($B)`, `Date`, `Last Close`, `RSI(14)`, `RS`, `Prev Day RS`, `Sector ETF`, `Sector RS (55d)`, `Beats Sector`; plus `ATR %`, `Entry`, `Exit (SL)`, `Quantity`, `Position ($)` if R6 is confirmed | RS, highest first |
| All Stocks | Every input symbol | `Symbol`, `Date`, `Last Close`, `RSI(14)`, `RS`, `Prev Day RS`, `Result` | Input order |

- Market cap is in billions of US dollars to 2 decimals; RS values to 3 decimals; RSI and prices to 2.
- The console prints the match count, the Matches table, the count of no-data symbols and the saved path.
- When nothing matches, the Matches sheet still has its header row, and the console says 0 matches.

**Launcher (.bat).** It finds Python (`py`, then `python`, then `%USERPROFILE%\python.exe`), installs packages from a pinned `requirements.txt` instead of upgrading on every run, runs the script with any dragged file, and pauses at the end.

## Edge cases and fixes to the original script

The rebuilt screener must handle these cases; the last column says what changes from the original script.

| Case | Required behaviour | Change from original |
| --- | --- | --- |
| Run during market hours | Drop today's incomplete bar | Yes: default was to use it |
| Stale symbol (halted or delisted) | Last bar older than the benchmark's last bar → Result `Stale data - last bar <date>`; not a match | Yes: was judged on the old bar |
| Every symbol has no data | Write both sheets, Matches empty, no crash | Yes: crashed with KeyError on `RS` |
| Empty Excel file | Print "No symbols found" and stop | Yes: crashed |
| `.xls` input | Not supported; ask for .xlsx | Yes: failed for lack of `xlrd` |
| `.info` lookup fails | Name, sector, industry and cap blank; R5 flag blank with `sector unknown` | No |
| Sector ETF download fails | That sector's R5 flag blank with `no ETF data` | New |
| Average loss is 0 | RSI = 100 | No |
| Packages | Pinned versions in `requirements.txt` | Yes: upgraded on every run |
| Missed cross days | A cross on a day the screener was not run is not reported | Open question Q2 |

## Acceptance tests

Each test uses fixed fixture series so results do not depend on live data.

- [ ] **RSI accuracy:** RSI(14) on a fixed test series matches a TradingView reference within 0.1.
- [ ] **Fresh cross:** RS 0.995 on t−1 and 1.012 on t, with RSI 64 → MATCH.
- [ ] **Already above:** RS 1.020 on t−1 and 1.030 on t → not a match, reason `RS already above 1 the day before (no fresh cross)`.
- [ ] **RSI boundary:** RSI exactly 60.00 with a fresh cross → not a match, reason `RSI <= 60`.
- [ ] **RS boundary:** RS exactly 1.000 on t → not a match; exactly 1.000 on t−1 and 1.001 on t → counts as a cross.
- [ ] **Short history:** 56 bars → `No data - check symbol`.
- [ ] **Sector flag:** a Technology match with Sector RS 1.08 vs XLK → `Beats Sector` = Y; 0.97 → N; no sector → blank with `sector unknown`.
- [ ] **Sector equivalence:** Sector RS equals RS vs S&P 500 divided by the ETF's RS vs S&P 500, within 0.001.
- [ ] **Sizing (if R6 confirmed):** capital $50,000, risk 1%, entry $158.40, stop $149.21 → quantity 54.
- [ ] **Intraday run:** run before 4:00 PM ET on a trading day → Date column shows the previous session.
- [ ] **All bad symbols:** a list of invalid tickers → file saved, Matches empty, no error.
- [ ] **US only:** `RELIANCE.NS` in the list → rejected before download as `Not a US symbol`.

## Differences from PRD Screen A

This screener is closer to a daily version of Spec 4's RS-ratio cross than to PRD v1.2 Screen A, so the PRD needs updating if it replaces Screen A.

| Topic | PRD v1.2 Screen A | This spec |
| --- | --- | --- |
| RS measure | IBD-style 1–99 rank of weighted 3/6/9/12-month return, ≥ 80 | 55-day RS ratio vs S&P 500 crossing above 1 |
| RSI | 50–70 "strong" or 40–50 "pullback" in an uptrend | Above 60, no upper limit, no pullback case |
| Signal type | State: qualifies today | Event: crossed today |
| Universe | S&P 500 + Nasdaq 100, about 550 tickers, universe filters | Owner's Excel list, no filters |
| Result count | Top 10 by RS | Every match, sorted by RS |
| Sector view | None | R5 Beats Sector flag |
| Sizing | Entry, 2×ATR stop, quantity (MOM-FR-06/07) | Same rule, proposed as R6 |
| Delivery | Dashboard module with JSON output contract | Standalone Excel output |

## Open questions

The owner decides each of these; proposed defaults apply until then.

| # | Question | Proposed default |
| --- | --- | --- |
| Q1 | Does this spec replace PRD Screen A, or run as a third Momentum screen? | Decide before the PRD's v0.1 build starts |
| Q2 | Report crosses from the last N trading days, not only bar t, so a skipped day misses nothing? | N = 1 (today only), with a setting to widen it |
| Q3 | Confirm R6 (entry, 2×ATR stop, quantity)? | Include, using PRD MOM-FR-06/07 rules |
| Q4 | Should RSI have an upper limit (for example 80) to avoid overbought entries? | No upper limit |
| Q5 | Compute the R5 flag for every stock on the All Stocks sheet as well? | Matches only, to avoid slow `.info` calls |
| Q6 | Should `Beats Sector` = N ever remove a stock from Matches? | No, informational only |

## Change log

| Date | Version | Change |
| --- | --- | --- |
| 2026-10-30 | 0.1 | First draft. Decoded R1–R4 from the existing script and launcher; added R5 sector RS flag, US-only scope, proposed R6 sizing, completed-bar and stale-data rules, and fixes for the original script's crashes |

*Personal research project, not investment advice.*
