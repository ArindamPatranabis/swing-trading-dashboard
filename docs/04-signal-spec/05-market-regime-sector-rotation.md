# Spec 5 · Market Regime & Sector Rotation

**Modules:** `market_regime` (banner) and `sector_rotation` (chart and table) · **Spec version:** 0.1 · **Status:** Draft
**Owner:** _Your name_ · **Last updated:** 2026-10-30
**Source:** PRD v1.2 (REG-FR-01, REG-FR-02, SECT-FR-01, SECT-FR-02, Q12, Q13), wireframe `dashboard.png` / `prototype.html`. There is no owner script for this module, so every formula and threshold not fixed by the PRD is a **proposed default** (marked in section 11) for the owner to confirm.

## 1. Purpose

Answer the persona's pain point P7 before any stock list is read: **does the market support buying, and where is the money going?**

- **Market regime** gives one word for the overall market (Risk-on, Caution, Risk-off) from SPY's trend and the VIX, plus six context tiles.
- **Sector rotation** shows which of the 11 sectors are beating SPY, and whether that strength is building or fading.

**Questions answered:** *Is this a market to take momentum trades in? Which sectors are leading, and which are turning up or rolling over?*

### 1.1 Two modules, one dashboard section

The banner and the rotation view are built as **two independent modules** that render in the same dashboard section (DASH-FR-02, item "regime banner and sector rotation"). Each has its own folder, cache, config, tests and version (PLAT-FR-03). A failed sector ETF download can't take down the regime banner, and the reverse is also true (NFR-03). Together they make 2 small yfinance batch calls per trading day (section 7).

## 2. Market regime rules (`market_regime`)

### 2.1 Regime states

The regime is evaluated on the **last completed trading session** (section 3.1), checked **top to bottom; the first match wins** (the worst condition wins).

| Order | Regime | Condition | Banner rule text |
| --- | --- | --- | --- |
| 1 | **Risk-off** | SPY close **<** SPY SMA(200) **OR** VIX close **> 30** | SPY below its 200-day MA, or VIX over 30 |
| 2 | **Caution** | SPY close **≤** SPY SMA(50) **OR** SPY close **=** SMA(200) **OR** VIX close **≥ 20** | SPY above its 200-day MA only, or VIX between 20 and 30 |
| 3 | **Risk-on** | SPY close **>** SMA(50) **AND** SPY close **>** SMA(200) **AND** VIX close **< 20** | SPY above its 50- and 200-day MA, and VIX under 20 |

How this resolves the overlaps in the PRD wording:

- SPY above both MAs with VIX at 25 → **Caution** (the VIX test fails Risk-on).
- SPY above its 50-day but below its 200-day (possible after a sharp bounce) → **Risk-off** (below the 200-day).
- SPY below its 200-day with VIX at 14 → **Risk-off** (the trend test alone is enough).
- VIX exactly 20.00 or exactly 30.00 → **Caution**. Risk-off needs VIX *over* 30.
- SPY exactly on its 200-day → **Caution**: not above it (so not Risk-on), not below it (so not Risk-off).

### 2.2 What the regime changes

- **Risk-off:** every Momentum section shows the warning line *"Risk-off market. Momentum setups fail more often when the market is weak."* (REG-FR-02). The lists are still shown; nothing is filtered.
- **Caution and Risk-on:** no warning. The banner is information only.
- DXY, MOVE, the 10-year yield, the S&P 500 index and the Nasdaq 100 are **context tiles only** and never change the regime (Q13).

### 2.3 Context tiles

| Tile | Symbol (yfinance) | Value shown | "This week" change |
| --- | --- | --- | --- |
| S&P 500 | `^GSPC` | Index level, 0 decimals | % change, 1 decimal |
| Nasdaq 100 | `^NDX` | Index level, 0 decimals | % change, 1 decimal |
| VIX | `^VIX` | Level, 1 decimal | Points, 1 decimal |
| US 10-year yield | `^TNX` | Yield in %, 2 decimals | Percentage points (pp), 2 decimals |
| US Dollar Index (DXY) | `DX-Y.NYB` | Level, 1 decimal | % change, 1 decimal |
| MOVE index | `^MOVE` | Level, 0 decimals | Points, 0 decimals |

**"This week" change** = last completed session's close compared with the **last close of the previous calendar week** (week-to-date). On a Saturday this is the full week. On a Monday it is Monday versus Friday.

The SPY ETF drives the regime rule (as the PRD says), and the S&P 500 index is shown as the tile (as the wireframe shows). Both are listed in the output so the dashboard never mixes them up.

## 3. Definitions and formulas · regime

### 3.1 Timeframe: daily bars

| Item | Definition |
| --- | --- |
| Raw data | Daily Close for 2 years (about 500 sessions), enough for SMA(200) plus a regime history for `regime_since` |
| Last completed session | The most recent session whose date is **before today**, or **today** if the run starts after **17:00 ET** (after the VIX settles at 16:15 ET). yfinance returns an unfinished bar for today during market hours, and that bar is always dropped |
| Market holiday | Uses the last completed session and shows its date with a note (PLAT-FR-07) |
| Price type | Split-adjusted, **not** dividend-adjusted (`Close` with `auto_adjust=False`), so the MAs match the broker's chart (PLAT-FR-07) |
| Session alignment | SPY and VIX must both have a bar for the last completed session. Otherwise the fallback rules apply (section 6) |

### 3.2 Indicators

| Metric | Formula | Notes |
| --- | --- | --- |
| SMA(50) | Mean of SPY's last 50 daily closes, including the as-of session | Simple MA, not exponential |
| SMA(200) | Mean of SPY's last 200 daily closes, including the as-of session | |
| % vs SMA(50) | (SPY close ÷ SMA(50) − 1) × 100 | Shown on hover, not a rule |
| % vs SMA(200) | (SPY close ÷ SMA(200) − 1) × 100 | Shown on hover, not a rule |
| Triggers | The list of conditions from 2.1 that are true, for example `["vix_ge_20"]` | Lets the banner say *why* it isn't Risk-on |
| Regime since | Date of the first session of the current unbroken run of this regime, computed by applying 2.1 to every session in the history | If the run covers all computable history, `regime_since_before: true` |
| Previous regime | The regime of the session before `regime_since` | |

**No smoothing or hysteresis in v0.1.** The regime can flip day to day near a threshold. Showing `regime_since` makes a fresh flip visible. See decision D6.

## 4. Sector rotation rules (`sector_rotation`)

### 4.1 Universe and benchmark

| Item | Value |
| --- | --- |
| Sectors | The 11 SPDR sector ETFs: XLB Materials, XLC Communication Services, XLE Energy, XLF Financials, XLI Industrials, XLK Technology, XLP Consumer Staples, XLRE Real Estate, XLU Utilities, XLV Health Care, XLY Consumer Discretionary |
| Benchmark | **SPY** (ETF against ETF; both sides include dividends, see 4.2) |
| Fixed list | The universe never changes with the stock selection parameters (PARAM-FR-01 doesn't apply here) |

### 4.2 Timeframe and price type

| Item | Definition |
| --- | --- |
| Raw data | Daily `Adj Close` for 2 years, built into weekly bars |
| Week, week date, last completed week | **Same rules as Spec 4 section 3.1**: Monday to Friday (`W-FRI`), dated on the week's last trading day, only completed weeks |
| Weekly value | Last daily `Adj Close` in the week |
| Price type | **Dividend-adjusted (total return).** This is the one exception to PLAT-FR-07 in this module. The rotation view sets no entry or stop levels, and sector dividend yields differ a lot (Utilities and Staples yield several times what Technology does), so price-only ratios would understate high-yield sectors every quarter |

### 4.3 Formulas (our own, resolves Q12)

For each sector ETF *e* and completed week *t*:

| Step | Metric | Formula | Notes |
| --- | --- | --- | --- |
| 1 | Relative strength line | RS<sub>t</sub> = Close<sub>e,t</sub> ÷ Close<sub>SPY,t</sub> | Rises when the sector beats SPY |
| 2 | **RS-Ratio** | RS-Ratio<sub>t</sub> = 100 × RS<sub>t</sub> ÷ SMA<sub>26</sub>(RS)<sub>t</sub> | The RS line against its own 26-week average. **Above 100** = the sector is beating SPY by more than it typically has over the past half year. Includes week *t* |
| 3 | **RS-Momentum** | RS-Momentum<sub>t</sub> = 100 × RS-Ratio<sub>t</sub> ÷ RS-Ratio<sub>t−4</sub> | The 4-week rate of change of RS-Ratio. **Above 100** = relative strength is improving |
| 4 | Quadrant | See 4.4 | |
| 5 | Tail | The (RS-Ratio, RS-Momentum) points for the 5 completed weeks before week *t*, oldest first | The chart's "5-week tail". With this week's dot, 6 points per sector |

**History needed:** the tail starts at *t*−5, its momentum needs RS-Ratio at *t*−9, and that needs 26 weeks of RS, so at least **35 completed weeks**. A 2-year download (about 104 weeks) covers this with plenty to spare. The newest ETF (XLC) has existed since 2018.

**Calculation is on unrounded values.** Display rounds to 2 decimals.

### 4.4 Quadrants

| Quadrant | RS-Ratio | RS-Momentum | Plain meaning |
| --- | --- | --- | --- |
| **Leading** | > 100 | > 100 | Beating SPY, and the lead is growing |
| **Weakening** | > 100 | ≤ 100 | Still beating SPY, but the lead is shrinking |
| **Lagging** | ≤ 100 | ≤ 100 | Trailing SPY, and still falling behind |
| **Improving** | ≤ 100 | > 100 | Trailing SPY, but catching up |

A value of exactly 100.00 counts as the **weaker** side (not above 100). Sectors usually move clockwise (Improving → Leading → Weakening → Lagging), but nothing in the rules assumes they do.

### 4.5 Ranking and table columns (resolves the "RS" ambiguity in SECT-FR-01)

| Column | Field | Definition |
| --- | --- | --- |
| Rank | `rank` | 1–11 by **RS-Ratio**, highest first. Ties go to the higher RS-Momentum, then alphabetical ETF |
| ETF | `etf` | Ticker |
| Sector | `sector` | Sector name from the fixed list in 4.1 |
| RS | `rs_ratio` | **RS-Ratio, the same number as the chart's x-axis**, 2 decimals (for example 104.20). The wireframe's 0–100 "RS" score is dropped so there is only one strength measure (gap G2) |
| RS-Momentum | `rs_momentum` | 2 decimals. New column (gap G2) |
| Prior rank | `prior_rank`, `rank_change` | Rank in the previous completed week; shown as "2 (up 1)", "6 (same)" |
| 4-week change | `return_4w_pct` | The ETF's own total return over the last 4 completed weeks: (Close<sub>t</sub> ÷ Close<sub>t−4</sub> − 1) × 100, 1 decimal. An absolute number, so the table shows whether the sector is actually rising, not only whether it beats SPY |
| Quadrant | `quadrant`, `prior_quadrant` | This week's quadrant. When it differs from last week's, the row shows "Improving → Leading" and `quadrant_changed` is true. That feeds the "since your last visit" strip (DASH-FR-05) |

## 5. Output fields

Both modules return the shared output contract (PLAT-FR-01): `module`, `module_version`, `spec_version`, `parameter_set`, `as_of`, `generated_at`, `status` (`ok` / `partial` / `unavailable`), `sources`, `rows`, `warnings`. `parameter_set` is always `Default` because neither module has dashboard-editable parameters (section 9).

### 5.1 `market_regime`

One regime row:

| Field | Format |
| --- | --- |
| `regime` | `risk_on`, `caution` or `risk_off` |
| `regime_rule_text` | The banner text from 2.1 |
| `triggers` | List, for example `["spy_le_sma50", "vix_ge_20"]` |
| `as_of_session` | Date of the last completed session |
| `spy_close`, `spy_sma50`, `spy_sma200` | 2 decimals |
| `pct_vs_sma50`, `pct_vs_sma200` | 2 decimals |
| `vix_close` | 2 decimals |
| `vix_source` | `yfinance` or `fred_vixcls` (section 6) |
| `regime_since`, `regime_since_before` | Date, boolean |
| `previous_regime` | Same values as `regime`, or null |

Plus a `tiles` list, one entry per tile in 2.3:

| Field | Format |
| --- | --- |
| `key` | `spx`, `ndx`, `vix`, `us10y`, `dxy`, `move` |
| `label`, `symbol` | Text |
| `value` | Number, decimals as in 2.3 |
| `week_change`, `week_change_unit` | Number; `pct`, `points` or `pp` |
| `as_of` | Date of the value |
| `source` | `yfinance` or `fred_dgs10` |
| `tile_status` | `ok` or `unavailable` (a missing tile never changes module status, see section 6) |

### 5.2 `sector_rotation`

Eleven rows, in rank order, with the fields from 4.5 plus:

| Field | Format |
| --- | --- |
| `as_of_week` | Date of the last completed week |
| `tail` | List of 5 `{week, rs_ratio, rs_momentum}` points, oldest first |
| `quadrant_changed` | Boolean |

The dashboard shows **two as-of labels** in the section header: "Regime as of Thu Oct 29 close" and "Rotation as of week ending Fri Oct 23" (gap G4).

### 5.3 Hover definitions (DASH-FR-07)

| Term | Plain-language definition |
| --- | --- |
| Regime | The market's overall state from SPY's trend and the VIX. It doesn't decide which stocks are listed |
| RS-Ratio | How strongly a sector is beating SPY compared with its own last 6 months. Above 100 = beating SPY |
| RS-Momentum | Whether that strength is rising or falling over the last 4 weeks. Above 100 = getting stronger |
| Quadrant | Where a sector sits on the chart: Leading, Weakening, Lagging or Improving |
| 4-week change | The sector ETF's own return over the last 4 weeks, dividends included |

## 6. Edge cases and data failures

| Case | Handling |
| --- | --- |
| SPY download fails (regime) | Regime `unavailable`: the banner shows "unavailable" with the reason and last good as-of (PLAT-FR-02). Tiles still show if they loaded. No Momentum warning is shown |
| `^VIX` fails or has no bar for the as-of session | Fall back to FRED `VIXCLS`. Accept it only if its date is the as-of session or **one session earlier**. Status `partial`, warning "VIX from FRED, as of <date>". Otherwise regime `unavailable` |
| Fewer than 200 SPY sessions | Regime `unavailable`, "not enough history" (shouldn't happen with a 2-year download) |
| `^TNX` fails | Fall back to FRED `DGS10` with its own date shown on the tile. If that fails, the tile shows "unavailable" |
| `^TNX` value above 20 | Treated as quoted ×10 (the old Yahoo convention) and divided by 10, with a warning. Below 0 or still above 20 → tile `unavailable` |
| `DX-Y.NYB` or `^MOVE` fails | Tile shows "unavailable" on its own. **No substitute**: FRED's broad dollar index is a different index from DXY, and there's no free MOVE source. Module status unchanged |
| Sanity ranges (outside → that tile or input is `unavailable`) | VIX 5–150, MOVE 30–300, DXY 70–150, prices > 0 |
| A tile's latest bar is older than the as-of session | Tile shows the value with its own date and a "stale" note |
| SPY download fails (rotation) | Rotation `unavailable` |
| 1 or more sector ETFs fail, or are stale (last weekly bar not the last completed week) | Those sectors are left out of the chart and table, named in `warnings`. Status `partial` (10 of 11 is below the 95% rule in PLAT-FR-06). The remaining sectors are ranked 1–10 |
| A sector ETF with fewer than 35 completed weeks | Left out, warning "not enough history" |
| RS-Ratio or RS-Momentum exactly 100.00 | Weaker side of the axis (4.4) |
| Prior week's data missing for a sector | `prior_rank` and `prior_quadrant` null; shown as "—" |
| Run during market hours | Today's unfinished daily bar is dropped (3.1); the week isn't complete, so rotation uses last Friday (4.2) |
| yfinance returns HTTP 429 (rate limited) | One retry after 10 s. Then use the cached last good data with status `partial` and warning "using cached data from <date>" |

## 7. Data sources and free-tier budget

The module costs **$0** and needs no new API keys. FRED is already used by Economic Data; the key is read from `.env` (NFR-10). No module code is shared (PLAT-FR-03); each module makes its own call.

| Source | Used for | Key | Calls per refresh | Free-tier limits | Notes |
| --- | --- | --- | --- | --- | --- |
| yfinance `yf.download` | Regime: SPY, `^VIX`, `^GSPC`, `^NDX`, `^TNX`, `DX-Y.NYB`, `^MOVE` | None | **1 batch** (7 symbols, 2y daily) | Unofficial; Yahoo throttles bursts with HTTP 429. No published quota | Pinned at `yfinance==1.7.0` in `requirements.txt` |
| yfinance `yf.download` | Rotation: SPY + 11 sector ETFs | None | **1 batch** (12 symbols, 2y daily) | Same | `auto_adjust=False` returns both `Close` and `Adj Close` in the same call |
| FRED API | Fallbacks only: `VIXCLS`, `DGS10` | Free key, already in `.env` | 0 normally; up to 2 when yfinance fails | 120 requests per minute | Values are end-of-day, usually 1 session behind |

**How the budget is kept:**

- **Daily cache** (PLAT-FR-04). The raw downloads and the computed output are cached per trading day. A repeat click the same day makes **no API calls** (NFR-01).
- **Minimum refresh interval** (PLAT-FR-05): 30 minutes per module. A forced refresh inside that window reuses the cache.
- **Rotation changes once a week.** After the weekly bar completes, re-runs Monday to Friday reuse the week's cached weekly series and only re-download if the daily cache has expired. The output is the same all week.
- **Call log** (PLAT-FR-08): every run logs runtime, rows, API calls (expected: 2 yfinance batches, 0 FRED) and cost ($0).
- **Expected runtime:** a few seconds for both modules, far inside NFR-02's 5-minute full refresh.
- **Raw data is never committed** to the repo (NFR-11). Test fixtures are synthetic series (section 10).

## 8. Display (for the dashboard; no logic)

The dashboard only renders these outputs (DASH-FR-04). Layout follows the wireframe, with these additions:

- **Banner:** regime word, rule text, and one extra line, for example "Since Oct 14 (was Caution). Why: VIX 23.4 ≥ 20." built from `regime_since`, `previous_regime` and `triggers`.
- **Chart:** axes centred on 100. Each axis range = the largest distance from 100 among all plotted points (dots and tails) + 0.5, with a minimum of ±2, so a quiet market doesn't look dramatic. Big dot for this week, a line through the 5 tail points, and the sector name label. Hover shows ETF, RS-Ratio, RS-Momentum and quadrant. The words "RRG" and "JdK" appear nowhere (SECT-FR-02).
- **Table:** columns in 4.5 order. A quadrant change shows as "Improving → Leading".

## 9. Parameters

Neither module has a dashboard parameter panel (PARAM-FR-02 lists stock modules only). Every value is fixed in config.

**`config/market_regime.yaml`:** `trend_symbol: SPY`, `volatility_symbol: ^VIX`, `sma_fast_days: 50`, `sma_slow_days: 200`, `vix_caution_at_or_above: 20`, `vix_risk_off_above: 30`, `rule_order: [risk_off, caution, risk_on]`, `price_type: close_split_adjusted`, `history_period: 2y`, `session_cutoff_et: "17:00"`, `tiles: [^GSPC, ^NDX, ^VIX, ^TNX, DX-Y.NYB, ^MOVE]`, `tile_change_basis: prior_week_last_close`, `fallbacks: {vix: FRED:VIXCLS, us10y: FRED:DGS10}`, `fred_max_lag_sessions: 1`, `min_refresh_minutes: 30`, `retry_on_429: {count: 1, wait_seconds: 10}`.

**`config/sector_rotation.yaml`:** `benchmark: SPY`, `sectors: [XLB, XLC, XLE, XLF, XLI, XLK, XLP, XLRE, XLU, XLV, XLY]`, `price_type: adj_close_total_return`, `bar_interval: weekly (W-FRI, built from daily)`, `rs_ratio_sma_weeks: 26`, `rs_momentum_lookback_weeks: 4`, `tail_weeks: 5`, `centre: 100`, `tie_side: weaker`, `rank_by: rs_ratio`, `return_window_weeks: 4`, `min_history_weeks: 35`, `history_period: 2y`, `min_refresh_minutes: 30`, `retry_on_429: {count: 1, wait_seconds: 10}`.

## 10. Test cases (acceptance)

All tests use synthetic series; no downloaded data is committed.

**Regime**

1. SPY 680.00, SMA(50) 670.00, SMA(200) 640.00, VIX 15.80 → **Risk-on**, triggers `[]`.
2. SPY 680.00, SMA(50) 690.00, SMA(200) 640.00, VIX 18.00 → **Caution**, triggers `["spy_le_sma50"]`.
3. SPY above both MAs, VIX 20.00 → **Caution**. VIX 30.00 → **Caution**. VIX 30.01 → **Risk-off**.
4. SPY 630.00, SMA(50) 620.00, SMA(200) 640.00, VIX 14.00 → **Risk-off** (above the 50-day, below the 200-day).
5. SPY exactly equal to SMA(200), above SMA(50), VIX 15.00 → **Caution**.
6. 50 closes averaging 670.00 → SMA(50) **670.00**; SPY 680.00 → % vs SMA(50) = **1.49**.
7. Regime history Caution, Caution, Risk-on, Risk-on, Risk-on (last 5 sessions, Oct 23–29) → `regime_since` = the first Risk-on session, `previous_regime` = Caution.
8. In Risk-off, every Momentum section's output view carries the REG-FR-02 warning; in Caution, none does.
9. S&P 500 last close of the previous week 6,717.00, latest close 6,812.00 → week change **+1.4%**. 10Y 4.17% → 4.12% → **−0.05 pp**. VIX 17.0 → 15.8 → **−1.2** points.
10. `^TNX` returns 41.20 → shown as **4.12%** with a warning.
11. `^MOVE` download fails → MOVE tile "unavailable", regime status **ok**.
12. `^VIX` fails; FRED `VIXCLS` returns 18.20 dated one session before the as-of session → regime uses 18.20, status **partial**, `vix_source = fred_vixcls`. Dated two sessions before → regime **unavailable**.
13. Run on Thursday 2026-10-29 at 14:00 ET → as-of session **Wed 2026-10-28**. Run at 17:30 ET → **Thu 2026-10-29**.

**Rotation**

14. ETF 52.00, SPY 500.00 → RS **0.104**. With SMA<sub>26</sub>(RS) = 0.100 → RS-Ratio **104.00**.
15. RS-Ratio 104.00 this week and 102.00 four weeks ago → RS-Momentum **101.96** → **Leading**.
16. RS-Ratio 99.50, RS-Momentum 100.80 → **Improving**. RS-Ratio 101.40, RS-Momentum 99.20 → **Weakening**. RS-Ratio 97.20, RS-Momentum 99.00 → **Lagging**.
17. RS-Ratio exactly 100.00, RS-Momentum 101.00 → **Improving** (tie goes to the weaker side).
18. ETF total-return close 100.00 four weeks ago and 104.10 now → 4-week change **+4.1%**.
19. XLK RS-Ratio 104.20 ranked 2nd last week and 1st this week → Prior rank shown as **"2 (up 1)"**.
20. Two sectors with RS-Ratio 101.00: RS-Momentum 100.50 and 99.80 → the 100.50 sector ranks higher.
21. Last week Improving, this week Leading → row shows **"Improving → Leading"**, `quadrant_changed = true`.
22. XLRE download fails → 10 sectors ranked 1–10, XLRE named in `warnings`, status **partial**.
23. A sector ETF with only 30 completed weeks → left out with "not enough history".
24. A run on Saturday 2026-10-31 uses the week ending Fri 2026-10-30. A run on Fri 2026-10-30 uses the week ending Fri 2026-10-23 (same rule as Spec 4 test 13).
25. Dividend check: SPY flat for 26 weeks with no dividend; a sector ETF flat except for a 1% price drop on its ex-dividend date (a 1% dividend) → on `Adj Close` its RS-Ratio stays **100.00**; on price-only `Close` it would fall **below 100** and wrongly show the sector as weakening.

**Platform**

26. A second click on the same trading day → both modules served from cache with **0 API calls** logged.
27. Regime module's source disabled → rotation chart and table still load, and the reverse (NFR-03).
28. A normal refresh logs exactly **2 yfinance calls and 0 FRED calls** (one per module).

## 11. Differences from PRD v1.2 (to resolve before v0.2 release)

| # | Topic | PRD v1.2 / wireframe | This spec | Status |
| --- | --- | --- | --- | --- |
| G1 | Module split | One supporting area, REG and SECT requirements | **Two modules** (`market_regime`, `sector_rotation`) in one section | Proposed; PRD wording to clarify |
| G2 | Table "RS" column | A 0–100 "RS" score (for example 92), not defined | RS column = **RS-Ratio** (same as the chart); RS-Momentum column added | Proposed; wireframe to change |
| G3 | "4-week change" | Not defined | ETF's own **total return** over 4 completed weeks | Proposed |
| G4 | As-of label | One "As of Mon Oct 26 close" | **Two labels**: regime (daily close) and rotation (week ending) | Proposed; wireframe to change |
| G5 | Rule precedence | Three conditions that overlap | **Worst condition wins** (2.1), boundaries defined | Proposed; PRD to adopt the table |
| G6 | Benchmark | SPY | **SPY** for both modules (Spec 4 uses `^GSPC` for stocks; here it is ETF vs ETF) | Proposed; matches the PRD |
| G7 | Price adjustment | Split-adjusted only (PLAT-FR-07) | Regime: split-adjusted. Rotation: **dividend-adjusted** (4.2) | Proposed exception; allowed by PLAT-FR-07 "unless a module's signal spec says otherwise" |
| G8 | Banner content | State and rule text only | Adds **since date, previous regime and the triggering condition** | Proposed; wireframe to add |
| G9 | Tile week change | "this week", not defined | Week-to-date vs the previous week's last close | Proposed |
| G10 | Data fallbacks | yfinance only for REG; FRED listed for ECON only | FRED `VIXCLS` and `DGS10` as free fallbacks; no substitutes for DXY and MOVE | Proposed; PRD dependency table to add REG under FRED |
| G11 | Rotation formulas | Q12: ratio normalised around 100, momentum = its rate of change | RS ÷ its 26-week SMA; 4-week rate of change of that (4.3) | Proposed; closes Q12 |
| G12 | Regime cadence | Daily dashboard refresh | Regime daily; rotation **weekly** on completed weeks, like Screen B | Proposed |

## 12. Decisions log

Every row is a **proposed default** until the owner confirms it.

| # | Question | Proposed decision |
| --- | --- | --- |
| D1 | One module or two? | **Two**, so a sector download failure can't hide the regime |
| D2 | How do overlapping regime rules resolve? | **Worst wins**: Risk-off, then Caution, then Risk-on. VIX 20 and 30 are Caution |
| D3 | RS-Ratio normalisation window | **26 weeks** (half a year). Short enough to show rotation, long enough to be stable |
| D4 | RS-Momentum lookback | **4 weeks**, about one month, matching the 4-week change column |
| D5 | Smooth the RS line before normalising? | **No** in v0.1, for transparency and easy testing. Review after 8 weeks of live charts: if tails are too jumpy, add a 3-week EMA on RS (one config value) |
| D6 | Hysteresis on the regime (for example 2 closes to confirm a flip)? | **No** in v0.1; `regime_since` shows fresh flips. Revisit if the banner flips more than twice in a month |
| D7 | Should Caution also warn the Momentum sections? | **No**, per REG-FR-02 (Risk-off only) |
| D8 | Price type for rotation | **Total return** (`Adj Close`); regime stays split-adjusted |
| D9 | What does the table rank by? | **RS-Ratio**, ties by RS-Momentum, then ETF name |
| D10 | Fallback for DXY and MOVE | **None**: tile "unavailable". FRED's dollar index is a different index and would mislead |
| D11 | Data budget | 2 yfinance batches per trading day, FRED only on failure, $0 |

## Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-10-30 | First draft from PRD v1.2 and the wireframe. Regime precedence and boundaries; our own RS-Ratio and RS-Momentum formulas (closes Q12); quadrant tie rule; ranking, 4-week change and table columns; two modules; free-tier data plan with FRED fallbacks; output fields; 28 test cases; gaps G1–G12 and decisions D1–D11 proposed for the owner |
