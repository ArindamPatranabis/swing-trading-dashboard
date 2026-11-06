# Spike step 5 findings: SEC EDGAR companyfacts (2026-11-04)

- Depth: 19-20 annual years for AAPL, MSFT, NVDA, JPM. Spec 1 (needs 11) is feasible.
- Fresher than Yahoo: AAPL FY2026 10-K (EPS 8.98) filed 2026-11-03 is present.
- Every fact has a "filed" date. Proposal: use it as the known-from date instead of FY end + 60 days.
- No standalone Q4 quarters in EDGAR. Confirms D5: Q4 = annual - (Q1+Q2+Q3).
- First-reported EPS is NOT split-adjusted (NVDA FY2024 = 11.93 vs Yahoo 1.19). Must adjust with Ticker.splits.
- Revenue concept changes over time (AAPL: SalesRevenueNet to 2017, RevenueFromContract... after).
  Adapter must merge the 3 revenue concepts, one value per fiscal year.
- BRK-B: no EarningsPerShareDiluted. Find Berkshire's EPS concept next.
- Later: interest coverage is not meaningful for banks (JPM).
