# Spec 1 · Value – Long Term

**Module:** `value_long_term` · **Spec version:** 0.1 · **Status:** Draft
**Owner:** _Your name_ · **Last updated:** 2026-10-23

## 1. Purpose

Find **financially strong companies with a long record of growth, trading at a reasonable price for that growth**, as long-term value candidates.

**Question answered:** *Which consistently growing, low-debt companies are priced attractively relative to their growth?*

## 2. Stock selection parameters

A stock is selected only when **all** rules are true.

| # | Parameter | Rule | Notes |
| --- | --- | --- | --- |
| 1 | Market cap | ≥ $2 billion | Minimum company size |
| 2 | US options market | Stock has listed options in the US market | Yes / No |
| 3 | Interest coverage ratio | > 5 | Earnings cover interest payments more than 5 times |
| 4 | Revenue growth (10 years) | > 10% | Compound annual growth rate (CAGR) over 10 years |
| 5 | Net income growth (10 years) | > 10% | Compound annual growth rate (CAGR) over 10 years |
| 6 | PEG ratio | < 1 | Price is low relative to earnings growth |
| 7 | Debt / EBITDA | ≤ 3 | Debt can be repaid from about 3 years of earnings |

## 3. Definitions and formulas

| Metric | Formula | Notes |
| --- | --- | --- |
| Market cap | Price × shares outstanding | Latest close |
| Interest coverage ratio | EBIT ÷ interest expense (TTM) | If interest expense = 0 (no debt), the rule passes |
| Revenue growth (10 years) | (Revenue FY0 ÷ Revenue FY−10)^(1/10) − 1 | Compound annual growth rate (CAGR), annual data |
| EPS growth (10 years) | (EPS FY0 ÷ EPS FY−10)^(1/10) − 1 | Shown; also used for PEG |
| Free cash flow growth (10 years) | (FCF FY0 ÷ FCF FY−10)^(1/10) − 1 | FCF = operating cash flow − capital expenditure. Shown, not a rule |
| Net income growth (10 years) | (Net income FY0 ÷ Net income FY−10)^(1/10) − 1 | Rule 5 |
| PEG ratio | PE (TTM) ÷ (10-year EPS CAGR × 100) | Uses the EPS growth column. Example: PE 15 and EPS growth 20% → PEG 0.75 |
| Debt / EBITDA | Total debt ÷ EBITDA (TTM) | |
| Operating cash flow | Cash from operations (TTM) | Shown |
| Net income | Net income (TTM) | Shown |
| Debt to profit | Total debt ÷ net income (TTM) | Shown, not a rule |
| CFO to net profit | Operating cash flow ÷ net income (TTM) | Shown, not a rule. Above 1 = earnings backed by cash |

**CAGR rule:** growth rates can only be computed when both the start and end values are positive. If either is zero or negative, the growth is `null` and the stock fails that rule.

## 4. Ranking and display

- **Sort:** market cap, largest first.
- **Rows shown:** all stocks that pass every rule.

## 5. Output fields

The module returns these columns, in this order:

| # | Column | Field name |
| --- | --- | --- |
| 1 | Symbol | `symbol` |
| 2 | Name | `name` |
| 3 | Option | `has_options` |
| 4 | Cap | `market_cap` |
| 5 | Interest coverage ratio | `interest_coverage` |
| 6 | Revenue growth | `revenue_growth_10y` |
| 7 | EPS growth | `eps_growth_10y` |
| 8 | Free cash flow growth | `fcf_growth_10y` |
| 9 | Net income growth | `net_income_growth_10y` |
| 10 | PEG | `peg` |
| 11 | Operating cash flow | `operating_cash_flow` |
| 12 | Net income | `net_income` |
| 13 | Debt to profit | `debt_to_profit` |
| 14 | CFO to net profit | `cfo_to_net_profit` |

Plus the standard fields from the shared output contract: `module`, `spec_version`, `as_of`, `generated_at`, `status`, `warnings`.

## 6. Edge cases

| Case | Handling |
| --- | --- |
| Less than 10 years of annual history | Growth = `null` → fails rules 4–5; listed in warnings |
| Negative net income (start or end year) | Growth = `null` → fails rule 5 |
| Negative or zero EPS growth | PEG not meaningful → fails rule 6 |
| EBITDA ≤ 0 | Debt/EBITDA not meaningful → fails rule 7 |
| No interest expense | Interest coverage passes rule 3; shown as "No debt" |
| Missing data field | Stock skipped, warning added |

## 7. Parameters (`config/value_long_term.yaml`)

`min_market_cap: 2e9`, `require_options: true`, `min_interest_coverage: 5`, `min_revenue_growth_10y: 0.10`, `min_net_income_growth_10y: 0.10`, `max_peg: 1.0`, `max_debt_to_ebitda: 3.0`, `growth_years: 10`, `sort_by: market_cap`, `sort_order: descending`, `top_n: all`.

## 8. Test cases (acceptance)

1. A company with revenue growing from 100 to 300 over 10 years has revenue growth ≈ 11.6% → passes rule 4.
2. A company with interest coverage of exactly 5 fails rule 3 (rule is "greater than 5").
3. A company with Debt / EBITDA of exactly 3 passes rule 7 (rule is "3 or less").
4. A company without listed US options never appears in results.
5. A company with negative net income 10 years ago has `net_income_growth_10y = null` and fails rule 5.
6. A company with PE 15 and EPS growth 20% has PEG 0.75 and passes rule 6.
7. A company with market cap $1.9 billion never appears; one with $2.0 billion can.
8. Results are ordered by market cap, largest first.

## 9. Decisions log

| # | Question | Decision |
| --- | --- | --- |
| Q1 | Minimum market cap | ≥ $2 billion |
| Q2 | Growth rate method | CAGR over 10 years |
| Q3 | Growth rate used in PEG | 10-year EPS CAGR |
| Q4 | Data source for 10 years of financials | Open — to be decided in the data dictionary. FMP's free plan covers only 5 years of annual statements; SEC EDGAR (free) is the leading candidate |
| Q5 | Ranking and rows | Sort by market cap, largest first; show all passing stocks |

## Change log

| Version | Date | Change |
| --- | --- | --- |
| 0.1 | 2026-10-23 | First draft from owner's selection rules |
