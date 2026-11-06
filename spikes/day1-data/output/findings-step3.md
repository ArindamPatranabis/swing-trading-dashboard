# Spike step 3 findings: Yahoo fundamentals (2026-11-04)

- Yahoo annual data: only 4 fiscal years. Not enough. Use SEC EDGAR for annual EPS.
- Yahoo quarterly data: has gaps (JPM, BRK-B) and lags (AAPL missing its latest quarter).
- BRK-B: Yahoo EPS is per Class B share. Check what EDGAR uses in step 5.
- Options: available for all 5 symbols.
- The red pandas "inplace" warning is harmless.
