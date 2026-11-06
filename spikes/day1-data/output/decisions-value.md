# Value modules: data decisions after spike steps 2, 3, 5 (2026-11-04)

## Decided
- D1: field name is `symbol` everywhere.
- D2: percentages stored in percent units, 2 dp; rules use unrounded values.
- D3: no market-cap rule inside value_long_term. Market cap is a dashboard universe
  filter, default minimum $2B, changeable by the user at any time; applies to all screens.
- D4: annual figures from SEC EDGAR companyfacts (Yahoo gives only ~4 years).
- D10: pe_avg_3y uses the mean.
- D11: R1 compares the latest quarter with the previous quarter (sequential).
- Symbols without EDGAR EarningsPerShareDiluted are excluded,
  reason "EPS not reported in EDGAR" (BRK-B excluded by this rule).
- Banks: interest_coverage rule not applied. Bank = Yahoo industry starting with "Banks".
  interest_coverage = null with note "Not applicable: bank"; the other 6 rules must pass.
- P1: quarterly figures from EDGAR; Yahoo quarterly only as fallback, flagged in sources[].fallback.
- P2: known-from date = EDGAR "filed" date. FY end + 60 days only for Yahoo fallback data.
- P3 (D5): Q4 = annual - (Q1 + Q2 + Q3); EDGAR never reports Q4 alone.
- P4: EDGAR per-share values split-adjusted with Yahoo Ticker.splits, to match split-adjusted Close.
- P5: revenue = one value per fiscal year, merged in this order:
  RevenueFromContractWithCustomerExcludingAssessedTax > Revenues > SalesRevenueNet.
  Warning if two concepts disagree by more than 1% for the same year.
- P6: no silent fallback from diluted EPS to basic EPS.

## Still open
- None for the Value modules.
