# 05 · Data Dictionary — Swing Trading Dashboard

Oct 31, 2026 · @Arindam Patranabis · Status: Draft v0.2 (D1, D2 decided)

**Related:** [03-prd.md](03-prd.md) · [04-signal-spec/](04-signal-spec/) · [07-architecture.md](07-architecture.md) · [adr/](adr/)

## Contents

1. [Conventions](#conventions)
2. [Reference data](#reference-data)
3. [Raw datasets](#raw-datasets)
4. [Derived fields by module](#derived-fields-by-module)
5. [Output contract](#output-contract)
6. [Parameters and settings](#parameters-and-settings)
7. [Archive, run log and snapshots](#archive-run-log-and-snapshots)
8. [Conflicts and open data questions](#conflicts-and-open-data-questions)

## Conventions

Every field in this dictionary follows the rules below; where a repo document disagrees, the conflict is listed in the last section with a proposed fix. Sources: PRD v1.3, signal specs 1 to 6, `07-architecture.md` and ADR-001 to ADR-012.

| Topic | Rule | Source |
| --- | --- | --- |
| Field names | `snake_case`, English, no units in the name except a period suffix (`_10y`, `_3y`, `_4w`) | Spec 1 output fields |
| Symbol format | Upper case, Yahoo dash form for share classes (`BRK-B`); any symbol containing a dot is rejected as `Not a US symbol` | Specs 2, 3 |
| Types | `string`, `int`, `float`, `bool`, `date` (ISO 8601 `YYYY-MM-DD`), `datetime` (ISO 8601 with offset), `enum` (closed list given in the field's row) | ADR-003 |
| Money | US dollars as `float`; market cap stored in dollars, shown in $B to 2 decimals | Spec 2 output |
| Percentages and growth | Stored in percent units, rounded to 2 decimals (`10.25` = 10.25%). Rules run on unrounded values; rounding happens only when the value is written | Owner decision D2, Oct 31 2026 |
| Ratios | Values that are not percentages keep their own precision: RS 3 decimals; PEG, PE, RS-Ratio and other multiples 2 decimals | Specs 2, 3, 5 |
| Prices | Split-adjusted, not dividend-adjusted, so entry and stop match the broker chart | PLAT-FR-07 |
| Completed bars | Daily: a bar dated today is dropped before the 4:00 PM ET close. Weekly: only weeks whose last trading day has closed | Specs 2, 3, 4 |
| Time zone | Market times and release times in US Eastern (ET); stored datetimes carry their offset | Vision, PRD ECON-FR-04 |
| As-of | `as_of` = date of the last completed trading session the value uses; on a market holiday, the prior session with a note | PLAT-FR-07, NFR-07 |
| Report lag | A fiscal year's annual figures count from fiscal year-end + 60 days, to avoid look-ahead | Spec 2, NFR-04 |
| Missing values | `null`, never 0, blank or `"n/a"`; the reason goes in the row's `exclusion_reason` or the module's `warnings` | Specs 1, 2 |
| CAGR | Computed only when start and end values are both positive; otherwise `null` and the rule fails | Specs 1, 2 |
| Display rounding | Prices and PE 2 decimals, EPS 3 decimals, growth % 2 decimals | Spec 2 output |

## Reference data

The stock universe is the S&P 500 + Nasdaq 100 (about 550 tickers), held in `config/universe` and loaded only by the market adapter; benchmarks, sector ETFs and market tiles are fixed lists in module config.

**Universe file** (`config/universe.csv`, replaces the Excel lists read by the Spec 2 and 3 scripts)

| Field | Type | Rule | Source |
| --- | --- | --- | --- |
| `symbol` | string | Upper case, Yahoo dash form; dot symbols rejected; duplicates dropped, first-seen order kept | Specs 2, 3 |
| `index_membership` | enum: `sp500`, `ndx100`, `both` | Universe never widens beyond these two indices | PRD non-goals, PARAM-FR-01 |
| `added_on` | date | When the ticker joined the file, for the tracker's history | Proposed |

**Benchmarks**

| Symbol | Used by | Price type | Why |
| --- | --- | --- | --- |
| `^GSPC` (S&P 500 index) | Momentum RS + RSI (Spec 3), RS + Ichimoku (Spec 4); S&P 500 tile | Split-adjusted close | Stock vs index RS |
| `SPY` (ETF) | Market regime trend rule; sector rotation benchmark; tracker returns | Regime: split-adjusted; rotation: dividend-adjusted | ETF vs ETF comparisons |

**Sector map** (Yahoo sector → SPDR sector ETF)

| `sector` (Yahoo) | `sector_etf` | Rotation label |
| --- | --- | --- |
| Technology | XLK | Technology |
| Healthcare | XLV | Health Care |
| Financial Services | XLF | Financials |
| Consumer Cyclical | XLY | Consumer Discretionary |
| Consumer Defensive | XLP | Consumer Staples |
| Communication Services | XLC | Communication Services |
| Industrials | XLI | Industrials |
| Energy | XLE | Energy |
| Utilities | XLU | Utilities |
| Real Estate | XLRE | Real Estate |
| Basic Materials | XLB | Materials |

Yahoo and SPDR use different sector names; `sector` always stores the Yahoo name and `sector_label` the rotation name, so joins go through `sector_etf`.

**Market tiles** (`market_regime` module)

| `key` | Label | Symbol | Value shown | Week change unit | Fallback |
| --- | --- | --- | --- | --- | --- |
| `spx` | S&P 500 | `^GSPC` | Level, 0 dp | `pct`, 1 dp | None |
| `ndx` | Nasdaq 100 | `^NDX` | Level, 0 dp | `pct`, 1 dp | None |
| `vix` | VIX | `^VIX` | Level, 1 dp | `points`, 1 dp | FRED `VIXCLS`, at most 1 session old |
| `us10y` | US 10-year yield | `^TNX` | %, 2 dp | `pp`, 2 dp | FRED `DGS10` |
| `dxy` | US Dollar Index | `DX-Y.NYB` | Level, 1 dp | `pct`, 1 dp | None (tile unavailable) |
| `move` | MOVE index | `^MOVE` | Level, 0 dp | `points`, 0 dp | None (tile unavailable) |

Sanity ranges: VIX 5–150, MOVE 30–300, DXY 70–150, prices above 0; a `^TNX` value above 20 is divided by 10 with a warning (Spec 5 section 6).

**COT contracts** (placeholder, COT-FR-01): crude oil, natural gas, gold and silver; no fields defined until the module is specified.

## Raw datasets

Three adapters write ten raw datasets as dated, read-only Parquet partitions (`data/raw/<dataset>/as_of=YYYY-MM-DD/`, ADR-004); modules never call a vendor API. Two source decisions the specs left to this document are settled here: 10-year fundamentals come from **SEC EDGAR company facts** (Spec 1 Q4), and every price-based module uses **split-adjusted, not dividend-adjusted** prices except sector rotation (Spec 4 G11, Spec 5 G7).

| Dataset | Adapter | Source | Refresh | Grain | Used by |
| --- | --- | --- | --- | --- | --- |
| `prices_daily` | market | yfinance `download`, `auto_adjust=False` | Daily after 17:00 ET | symbol × session | Momentum A and B, PE vs History, regime, rotation, tracker |
| `meta` | market | yfinance `Ticker.info`, `Ticker.options` | Weekly | symbol | All stock modules, universe filters |
| `statements` | market | yfinance `income_stmt`, `quarterly_income_stmt` | Weekly | symbol × period | PE vs History |
| `earnings` | market | yfinance `get_earnings_dates` | Daily | symbol | Earnings flags |
| `fundamentals` | fundamentals | SEC EDGAR `companyfacts` (XBRL); FMP free tier as fallback for gaps | Weekly | symbol × fiscal year | Value Long Term, management score |
| `insider_tx` | fundamentals | SEC EDGAR Form 4 | Daily check, weekly score | transaction | Management score |
| `holdings_13f` | fundamentals | SEC EDGAR 13F-HR / 13F-HR/A | Daily check in filing windows | filer × quarter × CUSIP | Super investors |
| `cusip_map` | fundamentals | OpenFIGI API, cached | On new CUSIP | CUSIP | Super investors |
| `macro_series` | macro | FRED API | Daily | series × observation date | Economic Data, regime fallbacks |
| `release_calendar` | macro | FRED release dates, agency calendars, Fed FOMC calendar | Weekly | indicator × release | Economic Data |

**`prices_daily`** (also holds benchmarks, sector ETFs and tile symbols)

| Field | Type | Unit | Definition |
| --- | --- | --- | --- |
| `symbol` | string | — | Symbol as sent to Yahoo |
| `session` | date | — | Trading session; today's bar dropped before the close |
| `open`, `high`, `low`, `close` | float | USD | Split-adjusted, not dividend-adjusted (`Close`) |
| `adj_close` | float | USD | Split- and dividend-adjusted; used only by sector rotation |
| `volume` | int | shares | Daily volume |

History kept: 2 years for prices (Spec 4, Spec 5), 4 years where PE vs History needs a 3-year average PE (Spec 2).

**`meta`**

| Field | Type | Unit | Definition | Yahoo field |
| --- | --- | --- | --- | --- |
| `symbol` | string | — | | |
| `name` | string | — | Long name, else short name | `longName`, `shortName` |
| `sector`, `industry` | string | — | Yahoo classification; null shows as "Unknown" | `sector`, `industry` |
| `market_cap` | float | USD | Price × shares outstanding | `marketCap` |
| `shares_outstanding` | int | shares | | `sharesOutstanding` |
| `has_options` | bool | — | True when Yahoo lists at least one US option expiry | `Ticker.options` non-empty |
| `insider_pct` | float | % | Shares held by officers and directors (Yahoo fraction × 100) | `heldPercentInsiders` |

**`statements`**

| Field | Type | Unit | Definition |
| --- | --- | --- | --- |
| `symbol`, `period_type` | string, enum `quarter` / `annual` | — | |
| `period_end` | date | — | Fiscal period end |
| `eps_diluted` | float | USD/share | `Diluted EPS`, else `Basic EPS`; blanks dropped |
| `eps_basis` | enum `diluted` / `basic` | — | Which row was used |
| `known_from` | date | — | `period_end` + 60 days for annual rows (report lag) |

Yahoo usually returns 4–5 quarters and 4 fiscal years (Spec 2).

**`earnings`**: `symbol`, `next_earnings_date` (date, null if unknown), `date_confirmed` (bool), `fetched_at` (datetime).

**`fundamentals`** (one row per symbol and fiscal year, at least 11 years for 10-year CAGRs)

| Field | Type | Unit | XBRL concept (us-gaap), first available wins |
| --- | --- | --- | --- |
| `cik`, `fiscal_year`, `fiscal_year_end` | string, int, date | — | From the filing |
| `revenue` | float | USD | `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`, `SalesRevenueNet` |
| `net_income` | float | USD | `NetIncomeLoss` |
| `eps_diluted` | float | USD/share | `EarningsPerShareDiluted` |
| `ebit` | float | USD | `OperatingIncomeLoss` |
| `interest_expense` | float | USD | `InterestExpense` |
| `depreciation_amortization` | float | USD | `DepreciationDepletionAndAmortization` |
| `income_tax`, `pretax_income` | float | USD | `IncomeTaxExpenseBenefit`, `IncomeLossFromContinuingOperationsBeforeIncomeTaxes…` |
| `operating_cash_flow` | float | USD | `NetCashProvidedByUsedInOperatingActivities` |
| `capex` | float | USD | `PaymentsToAcquirePropertyPlantAndEquipment` |
| `total_debt` | float | USD | `LongTermDebt` + `DebtCurrent` (or `ShortTermBorrowings`) |
| `cash` | float | USD | `CashAndCashEquivalentsAtCarryingValue` |
| `total_equity` | float | USD | `StockholdersEquity` |
| `diluted_shares` | float | shares | `WeightedAverageNumberOfDilutedSharesOutstanding` |
| `concept_used` | object | — | Which concept filled each field, for audit |

TTM values (EBIT, interest, EBITDA, CFO, net income) are the sum of the last four quarterly 10-Q/10-K facts. EDGAR XBRL starts around 2009, so 10-year CAGRs are computable for most of the universe; FMP covers only 5 years free.

**`insider_tx`**: `symbol`, `cik_issuer`, `filed_on` (date), `transaction_date` (date), `code` (enum; only `P` buy and `S` sell are used), `shares` (float), `price` (USD), `value` (USD = shares × price).

**`holdings_13f`**: `filer_cik`, `report_quarter` (date, quarter end), `accession` (string), `is_amendment` (bool), `cusip` (string, 9 chars), `share_class` (enum `SH` / `PRN`), `put_call` (enum `PUT` / `CALL` / null), `value_usd` (float), `shares` (float).

**`cusip_map`**: `cusip`, `symbol` (null when unmatched), `issuer_name`, `source` (`openfigi`), `mapped_on` (date). OpenFIGI is chosen because SEC's 13F securities list has CUSIPs and issuer names but no tickers (Spec 6 Q7).

**`macro_series`**: `series_id`, `observation_date`, `value` (float), `realtime_start` (date the value was published), `units` (string). Series IDs are listed per indicator in the next section.

**`release_calendar`**: `indicator_key`, `release_date` (date), `release_time_et` (time), `period` (string, for example `2026-09`), `estimate_type` (GDP only: `advance` / `second` / `third`), `confirmed` (bool; false shows "date not confirmed"), `source` (string).

## Derived fields by module

Each module computes its own fields from raw data and owns them (ADR-004); formulas below are copied from the signal specs, and thresholds are defaults that the parameters section lets the owner change.

### Shared stock fields

These appear on every stock row so the dashboard can apply universe filters without re-running a module (DASH-FR-04).

| Field | Type | Unit | Definition | Source |
| --- | --- | --- | --- | --- |
| `symbol` | string | — | Universe symbol | Universe file |
| `name`, `sector`, `industry` | string | — | From `meta` | Specs 3, 4 |
| `market_cap` | float | USD | From `meta`; filter default ≥ $2B | PARAM-FR-01 |
| `close` | float | USD | Last completed daily close; price filter default ≥ $10 | PRD Q18 |
| `avg_dollar_volume_20d` | float | USD | Mean of close × volume over the last 20 completed sessions; filter default ≥ $20M | **Proposed here** (Spec 4 section 2.3 defers it) |
| `earnings_date` | date | — | Joined from the earnings flags output by the dashboard, not the module | EARN-FR-01 |
| `result` | string | — | `MATCH`, `NEW`, `PENDING`, or every failed-rule reason joined by `; ` | Specs 2, 3, 4 |

### Economic Data (`econ`)

Eleven indicators; each becomes one `IndicatorRow`. FRED series IDs are the standard public IDs and are confirmed in the week-2 data spike.

| `indicator_key` | Indicator | Source series | Value shown | Release time (ET) |
| --- | --- | --- | --- | --- |
| `cpi` | CPI headline, core | FRED `CPIAUCSL`, `CPILFESL` | MoM % and YoY % | Mid-month, 8:30 |
| `pce` | PCE headline, core | FRED `PCEPI`, `PCEPILFE` | MoM % and YoY % | End of month, 8:30 |
| `ism_mfg` | ISM Manufacturing PMI | Manual entry from ISM press release (`is_manual = true`) | Index; above or below 50 | 1st business day, 10:00 |
| `ism_svc` | ISM Services PMI | Manual entry, as above | Index; above or below 50 | 3rd business day, 10:00 |
| `gdp` | Real GDP | FRED `A191RL1Q225SBEA` | Annualised % with `estimate_type` | Advance, second, third estimates, 8:30 |
| `fed_funds` | Fed funds target range, FOMC decision | FRED `DFEDTARL`, `DFEDTARU`; Fed FOMC calendar | Range; last decision `hike` / `hold` / `cut`; next meeting | Statement 14:00, press conference 14:30 |
| `retail_sales` | Retail sales headline, ex-autos | FRED `RSAFS`, `RSFSXMV` | MoM % | Mid-month, 8:30 |
| `vehicle_sales` | Light vehicle sales | FRED `ALTSALES` | Millions, SAAR, vs prior month | Start of month |
| `nfp` | Payrolls, unemployment rate | FRED `PAYEMS` (monthly change, thousands), `UNRATE` | Change and rate vs prior | First Friday, 8:30 |
| `jobless_claims` | Initial, 4-week average, continuing | FRED `ICSA`, `IC4WSA`, `CCSA` | Thousands | Thursday, 8:30 |
| `yield_curve` | 10Y–2Y spread | FRED `T10Y2Y` | pp; `inverted` when < 0; 1-month change | Each trading day |

| `IndicatorRow` field | Type | Definition |
| --- | --- | --- |
| `indicator_key`, `label` | string | Key from the table above, display name |
| `latest_value`, `prior_value`, `change` | float | Latest and prior published values; change = latest − prior, in the indicator's unit |
| `unit`, `period_basis` | enum | `pct`, `index`, `thousands`, `millions_saar`, `pp`; `mom`, `yoy`, `annualized`, `level` |
| `period` | string | Reference period, for example `2026-09` |
| `release_date`, `next_release_date` | date | Last and next release; next is null with `date_confirmed = false` when unknown |
| `days_to_next` | int | Calendar days from the as-of date to the next release |
| `due_within_7d` | bool | Highlighted row (ECON-FR-04) |
| `top_flag` | bool | True for FOMC or jobs report due within 7 days (ECON-FR-05) |
| `is_manual` | bool | PMI values entered by hand (ECON-FR-08) |
| `curve_state`, `trend_1m` | enum, float | Yield curve only: `inverted` / `normal`; spread now − spread 21 sessions ago |

### Momentum A · RS + RSI, daily (`momentum_rs_rsi`, Spec 3)

An event screen: a stock is listed on the day its 55-day RS crosses above 1 while RSI(14) is above 60. Bar t is the last completed session.

| Field | Type | Unit | Formula or rule |
| --- | --- | --- | --- |
| `rsi_14` | float | 0–100 | Wilder RSI, alpha 1/14; 100 when average loss is 0. Rule: > 60 |
| `rs_55d` | float | ratio | (C<sub>t</sub> ÷ C<sub>t−55</sub>) ÷ (SPX<sub>t</sub> ÷ SPX<sub>t−55</sub>), benchmark `^GSPC`, dates inner-joined. Rule: > 1 |
| `rs_55d_prev` | float | ratio | Same on bar t−1. Rule: ≤ 1 (fresh cross) |
| `sector_etf` | string | — | From the sector map; reason text (`sector unknown`, `no ETF data`) when blank |
| `sector_rs_55d` | float | ratio | (C<sub>t</sub> ÷ C<sub>t−55</sub>) ÷ (ETF<sub>t</sub> ÷ ETF<sub>t−55</sub>) |
| `beats_sector` | enum `Y` / `N` / null | — | `Y` when `sector_rs_55d` > 1; informational, never filters (R5) |
| `atr_14` | float | USD | Wilder average of true range, alpha 1/14 |
| `atr_pct` | float | % | `atr_14` ÷ close × 100 |
| `entry` | float | USD | Close on bar t (R6, proposed) |
| `stop` | float | USD | `entry` − 2 × `atr_14`; fixed at entry, not trailing |
| `stop_basis` | enum | — | `entry_minus_2atr` |
| `bars_available` | int | bars | Rule: at least 57 |

Display: RS to 3 decimals, RSI and prices to 2. Sorted by `rs_55d`, highest first; all matches returned.

### Momentum B · RS + Ichimoku, weekly (`momentum_rs_ichimoku`, Spec 4)

A signal-candle screen on completed weekly bars (Monday–Friday, `W-FRI`, dated on the week's last trading day). Only New and Pending signals are listed.

| Field | Type | Unit | Formula or rule |
| --- | --- | --- | --- |
| `rs` | float | ratio | RS(55 weeks) on the signal candle: (C<sub>w</sub> ÷ C<sub>w−55</sub>) ÷ (SPX<sub>w</sub> ÷ SPX<sub>w−55</sub>). Rule: > 1 |
| `rs_prev`, `rs_prev2` | float | ratio | RS in weeks s−1 and s−2; at least one must be ≤ 1 |
| `rs_cross_week` | date | — | Week s if `rs_prev` ≤ 1, else week s−1 |
| `conversion_line` | float | USD | (Highest weekly high + lowest weekly low over 9 weeks) ÷ 2, last completed week |
| `pct_above_conversion` | float | % | (close ÷ `conversion_line` − 1) × 100 |
| `signal_week` | date | — | Most recent week meeting rules 1–3 |
| `signal_status` | enum | — | `new`, `pending` (listed); `triggered`, `cancelled` (in `result` only) |
| `weeks_pending` | int | weeks | Completed weeks after `signal_week`; 0 for new |
| `entry` | float | USD | Signal candle high, no buffer (buy-stop) |
| `stop` | float | USD | Signal candle low |
| `stop_basis` | enum | — | `signal_low` |
| `risk_per_share` | float | USD | `entry` − `stop` |
| `pct_to_entry` | float | % | (`entry` ÷ last weekly close − 1) × 100 |
| `close` | float | USD | Last completed weekly close |

Lifecycle: triggered when a later weekly high ≥ `entry` (wins a tie with cancel); cancelled when a later weekly close < its conversion line. Grouped by sector (sector with the highest-RS stock first), then `rs` descending.

### Value – Long Term (`value_long_term`, Spec 1)

All seven rules must pass; FY0 is the latest fiscal year and FY−10 the year ten years earlier, both from `fundamentals`.

| Field | Type | Unit | Formula or rule |
| --- | --- | --- | --- |
| `has_options` | bool | — | From `meta`. Rule: true |
| `interest_coverage` | float | × | EBIT ÷ interest expense, TTM. Rule: > 5; no interest expense passes and shows "No debt" |
| `revenue_growth_10y` | float | % | ((Revenue FY0 ÷ Revenue FY−10)<sup>1/10</sup> − 1) × 100. Rule: > 10.00 |
| `net_income_growth_10y` | float | % | Same CAGR on net income. Rule: > 10.00 |
| `eps_growth_10y` | float | % | Same CAGR on diluted EPS; feeds PEG |
| `fcf_growth_10y` | float | % | Same CAGR on FCF = operating cash flow − capex; shown, not a rule |
| `pe_ttm` | float | × | Close ÷ TTM diluted EPS |
| `peg` | float | × | `pe_ttm` ÷ `eps_growth_10y` (growth already in %). Rule: < 1; growth ≤ 0 fails |
| `ebitda_ttm` | float | USD | EBIT + depreciation and amortisation, TTM |
| `debt_to_ebitda` | float | × | Total debt ÷ `ebitda_ttm`. Rule: ≤ 3; EBITDA ≤ 0 fails |
| `operating_cash_flow`, `net_income` | float | USD | TTM, shown |
| `debt_to_profit` | float | × | Total debt ÷ net income TTM; shown |
| `cfo_to_net_profit` | float | × | Operating cash flow ÷ net income, TTM; above 1 means earnings backed by cash |

Sorted by `market_cap`, largest first; every passing stock shown. Fewer than 11 fiscal years of history gives null growth and a warning.

### Value – PE vs History (`value_pe_history`, Spec 2)

Growing companies priced below their own 3-year average PE, on reported EPS only (no analyst estimates).

| Field | Type | Unit | Formula or rule |
| --- | --- | --- | --- |
| `eps_latest_q`, `eps_prev_q` | float | USD/share | Last two quarterly diluted EPS. Rule R1: latest > previous |
| `latest_q_date` | date | — | Latest quarter end; older than 135 days → `Stale EPS`, excluded |
| `eps_ttm` | float | USD/share | Sum of last 4 quarters; null if fewer than 4 |
| `eps_growth_3y` | float | % | ((EPS FY ÷ EPS FY−3)<sup>1/3</sup> − 1) × 100. Rule R2: > 1.00 |
| `pe_current` | float | × | Last completed close ÷ `eps_ttm`, computed locally (Yahoo `trailingPE` is not used) |
| `pe_avg_3y` | float | × | Mean over the last 3 years of daily close ÷ latest annual EPS known that day (FY end + 60 days); EPS ≤ 0 days dropped; needs ≥ 200 usable days |
| `pct_below_avg` | float | % | (1 − `pe_current` ÷ `pe_avg_3y`) × 100. Rule R3: `pe_current` < `pe_avg_3y` (minimum discount default 0.00%) |
| `split_check` | enum | — | `ok` / `mismatch`; statement EPS checked against `Ticker.splits`, mismatch excluded with a warning |

Display: PE and price 2 decimals, EPS 3 decimals. Sorted by `eps_growth_3y`, highest first; every passing stock shown.

### Market regime and sector rotation (`market_regime`, `sector_rotation`, Spec 5)

Two modules in one dashboard section: the regime is daily on split-adjusted SPY; rotation is weekly on dividend-adjusted ETF prices.

| Field | Module | Type | Unit | Formula or rule |
| --- | --- | --- | --- | --- |
| `regime` | regime | enum | — | `risk_off` (SPY < SMA200 or VIX > 30), else `caution` (SPY ≤ SMA50, SPY = SMA200 or VIX ≥ 20), else `risk_on`; worst wins |
| `triggers` | regime | list | — | True conditions, for example `spy_le_sma50`, `vix_ge_20` |
| `spy_close`, `spy_sma50`, `spy_sma200` | regime | float | USD | Simple MAs including the as-of session |
| `pct_vs_sma50`, `pct_vs_sma200` | regime | float | % | (SPY ÷ SMA − 1) × 100 |
| `vix_close`, `vix_source` | regime | float, enum | points | `yfinance` or `fred_vixcls` |
| `regime_since`, `previous_regime` | regime | date, enum | — | Start of the current unbroken run; regime before it |
| `rs_ratio` | rotation | float | index, 100 = par | 100 × (ETF ÷ SPY) ÷ SMA<sub>26w</sub>(ETF ÷ SPY) |
| `rs_momentum` | rotation | float | index | 100 × RS-Ratio<sub>t</sub> ÷ RS-Ratio<sub>t−4</sub> |
| `quadrant` | rotation | enum | — | `leading` (>100, >100), `weakening` (>100, ≤100), `lagging` (≤100, ≤100), `improving` (≤100, >100); exactly 100 is the weaker side |
| `rank`, `prior_rank`, `rank_change` | rotation | int | — | 1–11 by RS-Ratio; ties by RS-Momentum, then ETF name |
| `return_4w_pct` | rotation | float | % | (Close<sub>t</sub> ÷ Close<sub>t−4</sub> − 1) × 100, total return |
| `prior_quadrant`, `quadrant_changed` | rotation | enum, bool | — | Feeds the "since your last visit" strip |
| `tail` | rotation | list | — | 5 `{week, rs_ratio, rs_momentum}` points, oldest first |

### Earnings flags (`earnings_flags`, EARN-FR-01)

| Field | Type | Unit | Formula or rule |
| --- | --- | --- | --- |
| `next_earnings_date` | date | — | From `earnings`; null shows "—" |
| `trading_days_to_earnings` | int | sessions | Exchange-calendar sessions from the as-of date |
| `earnings_within_10d` | bool | — | True when `trading_days_to_earnings` ≤ 10 |

### Management score and super investors (`management_superinvestors`, Spec 6)

Display-only columns on every stock table; never a filter or sort key. Financials use ROE in place of ROIC.

| Field | Type | Unit | Formula or rule |
| --- | --- | --- | --- |
| `roic` | float | % | NOPAT ÷ invested capital × 100, FY0; NOPAT = EBIT × (1 − tax rate), tax rate = income tax ÷ pretax income clamped 0–35%, else 21%; invested capital = debt + equity − cash |
| `roic_trend_pp` | float | pp | ROIC FY0 − mean ROIC FY−1 to FY−4 |
| `roe` | float | % | Net income ÷ average equity × 100; Financials only |
| `insider_pct` | float | % | From `meta` |
| `net_insider_buying_usd`, `net_insider_buying_pct` | float | USD, % | Σ code P − Σ code S over 12 months; ÷ market cap × 100 |
| `share_change_3y` | float | % / year | ((Diluted shares FY0 ÷ FY−3)<sup>1/3</sup> − 1) × 100; negative = buybacks |
| `mgmt_score` | int | 0–100 | Sum of component points (weights 25/15/20/20/20); rescaled when 3–4 components exist; null below 3 |
| `mgmt_grade` | enum | — | `strong` 80–100, `good` 60–79, `mixed` 40–59, `weak` 0–39 |
| `mgmt_partial`, `mgmt_components` | bool, object | — | Rescaled flag; value and points per component |
| `superinvestor_count`, `superinvestor_change` | int | — | Listed filers holding `SH` shares with value > 0 in their latest 13F-HR; change vs previous quarter |
| `superinvestor_names` | list | — | Display names |
| `report_quarter`, `filers_current` | date, int | — | Quarter end used; how many listed filers have filed for it |

**Super investor CIKs** (`config/superinvestors.yaml`; Spec 6 asks for them to be recorded here). Confirm each firm's latest 13F-HR when the list is set up and remove any firm that has stopped filing.

| # | Investor | 13F filer | CIK | Checked |
| --- | --- | --- | --- | --- |
| 1 | Warren Buffett | Berkshire Hathaway | 0001067983 | [arkolith](https://arkolith.com/funds), [pagecrawl](https://pagecrawl.io/blog/13f-institutional-holdings-change-monitoring) |
| 2 | Seth Klarman | Baupost Group | 0001061768 | [arkolith](https://arkolith.com/funds) |
| 3 | Bill Ackman | Pershing Square Capital Management | 0001336528 | [SEC filing](https://www.sec.gov/Archives/edgar/data/0001336528/000117266111000410/pers1q11.txt) |
| 4 | David Tepper | Appaloosa LP | 0001656456 | [arkolith](https://arkolith.com/funds) |
| 5 | Stanley Druckenmiller | Duquesne Family Office | 0001536411 | [arkolith](https://arkolith.com/funds) |
| 6 | Li Lu | Himalaya Capital Management | 0001709323 | [arkolith](https://arkolith.com/funds) |
| 7 | David Einhorn | Greenlight Capital | 0001079114 | [arkolith](https://arkolith.com/funds) |
| 8 | Dan Loeb | Third Point | 0001040273 | [arkolith](https://arkolith.com/funds) |
| 9 | Chuck Akre | Akre Capital Management | 0001112520 | [SEC filing](https://www.sec.gov/Archives/edgar/data/0001112520/000111252012000007/akre13fhrnon.txt) |
| 10 | Tom Gayner | Markel Group | 0001096343 | [arkolith](https://arkolith.com/funds) |
| 11 | Prem Watsa | Fairfax Financial Holdings | 0000915191 | Not verified; confirm on EDGAR |
| 12 | Howard Marks | Oaktree Capital Management | 0000949509 | [arkolith](https://arkolith.com/funds) |
| 13 | Mohnish Pabrai | Dalal Street LLC | 0001549575 | [arkolith](https://arkolith.com/funds) |
| 14 | Terry Smith | Fundsmith | 0001569205 | Not verified; confirm on EDGAR |
| 15 | Chris Hohn | TCI Fund Management | 0001647251 | Not verified; confirm on EDGAR |

## Output contract

Every module writes one JSON file with the envelope below (contract v1.0.0, ADR-003); the module-specific fields from the previous section sit inside `rows`. The envelope merges PLAT-FR-01's field list with the `generated_at` and `spec_version` names the signal specs use.

**Envelope**

| Field | Type | Required | Definition |
| --- | --- | --- | --- |
| `contract_version` | string | yes | Semantic version, `1.0.0` |
| `module`, `module_version` | string | yes | Package name and its own version |
| `spec_version` | string | yes | Signal spec and version, for example `spec-3@0.1` |
| `parameter_set` | object | yes | `{name, values, hash}`; `name` is `default`, `custom` or a preset name |
| `as_of` | date | yes | Last completed session used |
| `as_of_week` | date | weekly modules | Last completed week used (Momentum B, rotation) |
| `generated_at` | datetime | yes | When the run finished |
| `status` | enum | yes | `ok`, `partial` (under 95% coverage or a fallback used), `unavailable` |
| `status_reason` | string | when not ok | Plain-language reason shown on the card |
| `coverage` | float | stock modules | % of the universe with usable data |
| `sources` | list | yes | `{name, dataset, as_of, fallback}` per source used |
| `rows` | list | yes | Every passing row (Q17); empty list when none pass |
| `excluded` | list | stock modules | `{symbol, reason}` for every stock not listed, for "why not" |
| `warnings` | list | yes | `{code, symbol, message}` |
| `metrics` | object | yes | `{runtime_s, rows, api_calls, cost_usd}` (PLAT-FR-08) |

The orchestrator, not the module, adds `last_good_as_of` when a run fails, and the dashboard derives two display states that are not module statuses: `stale` (last good result shown) and `fewer_than_3` (MOM-FR-05).

**Row types**

| Row type | Used by | Fields beyond the shared stock fields |
| --- | --- | --- |
| `StockRow` | Value Long Term, PE vs History | Module fields + `rules_passed` (list of rule IDs, feeds "why flagged") |
| `MomentumRow` | Momentum A | `StockRow` + `entry`, `stop`, `stop_basis`, `atr_pct` |
| `SignalRow` | Momentum B | `MomentumRow` + `signal_status`, `signal_week`, `weeks_pending`, `risk_per_share`, `pct_to_entry` |
| `IndicatorRow` | Economic Data | Fields listed under Economic Data |
| `RegimeRow` + `TileRow` | Market regime | One regime row plus 6 tiles: `key`, `label`, `symbol`, `value`, `week_change`, `week_change_unit`, `as_of`, `source`, `tile_status` |
| `SectorRow` | Sector rotation | Fields listed under rotation |
| `ContextRow` | Earnings flags, management and super investors | Keyed by `symbol`; joined onto stock tables by the dashboard |

**Combined views** (read module outputs only)

| View | Row fields |
| --- | --- |
| `confluence` | `symbol`, `modules` (list of module names passed), `module_count` (≥ 2), `excluded_partial` (modules left out because their status was partial, PRD Q10) |
| `whats_new` | `symbol` or `indicator_key`, `change` (`new`, `dropped`, `triggered`, `cancelled`, `released`), `source_module`, `since` (previous visit timestamp) |
| `tracker` | `pick_date`, `symbol`, `module`, `parameter_set_hash`, `ref_price` (close on pick date; Screen B: entry when triggered, PRD Q19), `return_1w`, `return_2w`, `return_4w`, `spy_return_1w/2w/4w`, `excess_4w` (all %), `outcome` (`open`, `triggered`, `cancelled`) |
| `summary` | `lines` (list of template sentences), `numbers_used` (every number with its source field, for the grounding check) |

**Computed by the dashboard, never stored in the contract**: `quantity` = floor(capital × risk % ÷ (`entry` − `stop`)), `position_value` = quantity × entry, `exceeds_capital` (bool), and `hidden_by_filter` (bool). Capital and risk % never reach a module (PLAT-FR-01).

## Parameters and settings

Only the parameters marked "panel" can be changed on the dashboard (PARAM-FR-01, 02); everything else is fixed in `config/<module>.yaml`, and every run records the full set in `parameter_set`.

| Parameter | Module | Default | Unit | Where | Source |
| --- | --- | --- | --- | --- | --- |
| `min_market_cap` | Universe filter | 2,000,000,000 | USD | Panel | PARAM-FR-01, Spec 1 |
| `min_price` | Universe filter | 10 | USD | Panel | PRD Q18 |
| `min_avg_dollar_volume` | Universe filter | 20,000,000 | USD | Panel | PRD Q18 |
| `rsi_length`, `rsi_min` | Momentum A | 14, 60 | bars, index | Config; `rsi_min` panel | Spec 3 |
| `rs_length_days`, `rs_level` | Momentum A | 55, 1 | sessions, ratio | Config | Spec 3 |
| `atr_length`, `atr_stop_multiple` | Momentum A | 14, 2 | bars, × | Config | Spec 3 R6 |
| `rs_length_weeks` | Momentum B | 55 | weeks | Panel | Spec 4 |
| `rs_cross_window_weeks`, `conversion_length_weeks` | Momentum B | 2, 9 | weeks | Config | Spec 4 |
| `require_options` | Value Long Term | true | — | Panel | Spec 1 |
| `min_interest_coverage` | Value Long Term | 5 | × | Panel | Spec 1 |
| `min_revenue_growth_10y`, `min_net_income_growth_10y` | Value Long Term | 10.00, 10.00 | % | Panel | Spec 1 |
| `max_peg`, `max_debt_to_ebitda` | Value Long Term | 1.0, 3.0 | × | Panel | Spec 1 |
| `min_eps_growth_3y` | PE vs History | 1.00 | % | Panel | Spec 2 |
| `pe_history_years` | PE vs History | 3 | years | Panel | Spec 2 |
| `min_discount_to_avg_pe` | PE vs History | 0.00 | % | Panel | Spec 2 Q4 |
| `report_lag_days`, `max_quarter_age_days` | PE vs History | 60, 135 | days | Config | Spec 2 |
| `sma_fast_days`, `sma_slow_days` | Regime | 50, 200 | sessions | Config | Spec 5 |
| `vix_caution_at_or_above`, `vix_risk_off_above` | Regime | 20, 30 | points | Config | Spec 5 |
| `rs_ratio_sma_weeks`, `rs_momentum_lookback_weeks`, `tail_weeks` | Rotation | 26, 4, 5 | weeks | Config | Spec 5 |
| `earnings_flag_sessions` | Earnings flags | 10 | sessions | Config | EARN-FR-01 |
| `mgmt_weights` | Management score | 25/15/20/20/20 | points | Config | Spec 6 |
| `min_refresh_minutes` | Every module | 30 | minutes | Config | Spec 5, PLAT-FR-05 |

**Owner settings** (`~/.stdash/settings.json`, outside the repo, never in a snapshot that leaves the PC; NFR-15)

| Setting | Type | Default | Valid range | Behaviour outside range |
| --- | --- | --- | --- | --- |
| `capital` | float, USD | 50,000 (sample) | > 0 | Quantity "—" with a warning |
| `risk_pct` | float, % | 1.0 | 0.25–3.0 | Quantity "—" with a warning |
| `presets` | list | empty | — | Named parameter sets (PARAM-FR-05) |
| `last_visit` | datetime | — | — | Baseline for the "since your last visit" strip |

The badge reads `Default` when every panel value equals its default, otherwise `Custom (unsaved)` or the preset name (PARAM-FR-04).

## Archive, run log and snapshots

Each refresh writes one snapshot folder plus one index row, and every adapter, module and view run appends one run-log row, all in one SQLite file (ADR-005, ADR-011).

**Snapshot folder** (`archive/<YYYY-MM-DD>T<HHMM>/`): `dashboard.html`, `manifest.json`, and one contract JSON per module and view (ARCH-FR-01).

| `manifest.json` field | Type | Definition |
| --- | --- | --- |
| `snapshot_id` | string | Folder name |
| `created_at` | datetime | When the refresh finished |
| `as_of`, `as_of_week` | date | Session and week the snapshot reflects |
| `modules` | list | `{module, module_version, spec_version, contract_version, status, parameter_set_hash}` per module (NFR-14) |
| `parameter_set` | object | Full parameter set used |
| `sizing_inputs_hash` | string | Hash of capital and risk %, so a snapshot proves which inputs were used without revealing them (NFR-14 and NFR-15 together) |
| `disclaimer` | string | "Personal research project, not investment advice" (ARCH-FR-04) |

**`snapshots` table** (opens a past snapshot by date, ARCH-FR-02): `snapshot_id` (key), `created_at`, `as_of`, `path`, `modules_ok`, `modules_partial`, `modules_unavailable`.

**`runs` table** (PLAT-FR-08)

| Field | Type | Definition |
| --- | --- | --- |
| `run_id` | string | Unique per run |
| `snapshot_id` | string | Null for runs outside a refresh |
| `unit`, `unit_kind` | string, enum | Name; `adapter`, `module`, `view` |
| `started_at`, `runtime_s` | datetime, float | |
| `status`, `error` | enum, string | Contract status; error text when unavailable |
| `rows`, `api_calls` | int | |
| `cost_usd` | float | 0 for every free source; LLM cost only for the optional narrator |
| `cache_hit` | bool | True when served without re-running |

**`cache` table** (ADR-006): `cache_key` = hash of (module, module version, spec version, parameter hash, input partitions), `output_path`, `created_at`.

**Public sample snapshot** (`samples/`, hosted link): built from synthetic fixture data only; no vendor data, no `sizing_inputs_hash`, no settings (NFR-11, NFR-15, PRD Q11).

## Conflicts and open data questions

Reading all the documents side by side turned up 14 places where they disagree or leave a data question open. D1 and D2 were decided on Oct 31, 2026; for the rest, the dictionary follows the proposed resolution until the owner decides.

| # | Topic | Where it conflicts | Resolution |
| --- | --- | --- | --- |
| D1 | Symbol field name | Specs 1, 4 and 6 used `symbol`; PRD and ADR-003 used `ticker` | **Decided Oct 31, 2026:** `symbol` everywhere; ADR-003 and the PRD's field lists follow |
| D2 | Percent storage | Spec 1 config used fractions (`0.10`); Spec 2 script used `EPS_GROWTH_MIN 1` (percent) | **Decided Oct 31, 2026:** percent units, rounded to 2 decimals after the rules run; Spec 1 config changes to `10.00` |
| D3 | Market-cap rule in Value Long Term | Spec 1 rule 1 is in the module; PRD VLT-FR-01 and Spec 4 put it in the universe filter | Proposed: universe filter only; drop rule 1 from Spec 1 |
| D4 | Annual EPS history for PE vs History | Spec 2 reads Yahoo statements, which usually give exactly 4 fiscal years, so one missing year blocks R2 | Proposed: use EDGAR `fundamentals` for annual EPS, keep Yahoo for quarterly EPS |
| D5 | TTM figures in Value Long Term | Spec 1 needs TTM EBIT, interest and EBITDA; EDGAR reports Q4 only inside the 10-K | Proposed: derive Q4 = annual − (Q1 + Q2 + Q3); flag the stock if any quarter is missing |
| D6 | Momentum A fields | PRD MOM-FR-04 lists RS rating 1–99, week % change and distance from 50-day MA; Spec 3 defines none of them | Follows Spec 3 until Spec 3 Q1 (replace or run beside Screen A) is decided |
| D7 | Data calls in Spec 5 | Spec 5 section 7 has each module making its own yfinance call; ADR-004 (accepted) has adapters fetch once into shared raw data | Update Spec 5 section 7 to read `prices_daily`; call counts move to the adapter |
| D8 | Spec 6 module placement | Spec 6 is owner-accepted but has no PRD requirement and no row in the architecture service catalogue | Proposed: add a PRD requirement (for example MGMT-FR-01) and a catalogue row |
| D9 | Non-US suffix setting | Spec 4 config keeps `exchange_suffix` (`.NS`, `.BO`); Specs 2 and 3 make the product US-only | Proposed: remove `exchange_suffix` from Spec 4 |
| D10 | 3-year PE statistic | PRD PER-FR-02 says mean; Spec 2 Q5 proposes median | Mean until Q5 is decided; `pe_avg_3y` renamed `pe_median_3y` if it changes |
| D11 | Sequential EPS | Spec 2 Q2 proposes year-over-year to remove seasonality | Sequential (current rule) until decided |
| D12 | Wireframe path | Folder is now `docs/06-wireframes/`; ADR-008, the architecture doc and the wireframe README still say `docs/wireframes/`; a stray 1-byte file `docs/07-Architecture` exists | Proposed: fix the links and delete the stray file |
| D13 | Unverified identifiers | FRED series IDs and 3 of 15 CIKs (Fairfax, Fundsmith, TCI) are not yet confirmed | Confirm in the week-2 data spike |
| D14 | ISM PMIs | No free ISM data feed found (Vision risk, PRD Q9) | Manual entry with `is_manual = true` until a source is confirmed |

**Documents read**: README, `01-vision.md` v1.1, `02-persona.md`, `03-prd.md` v1.3, signal specs 1–6, `06-wireframes/README.md` and `prototype.html`, `07-architecture.md`, ADR-001 to ADR-012, `requirements.txt` and `.env.example`, as of commit `e017645` (Oct 31, 2026).

_Disclaimer: personal research project, not investment advice._
