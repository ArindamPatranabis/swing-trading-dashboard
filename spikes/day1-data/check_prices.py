"""Day-1 spike, step 2: what does yfinance give us for daily prices?"""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yfinance as yf

SYMBOLS = ["AAPL", "NVDA", "BRK-B", "SPY", "^GSPC", "BRK.B"]  # BRK.B is meant to fail
START = "2024-01-01"
OUT = Path("output")
OUT.mkdir(exist_ok=True)

now_et = datetime.now(ZoneInfo("America/New_York"))
print(f"Now in New York: {now_et:%Y-%m-%d %H:%M} ET\n")

for sym in SYMBOLS:
    print(f"=== {sym}")
    try:
        df = yf.Ticker(sym).history(start=START, interval="1d",
                                    auto_adjust=False, actions=True)
    except Exception as e:
        print("  ERROR:", type(e).__name__, e, "\n")
        continue
    if df.empty:
        print("  No data returned\n")
        continue

    df.to_csv(OUT / f"prices_{sym.replace('^', 'IDX_')}.csv")
    last = df.index[-1]
    print("  rows:", len(df), "| first:", df.index[0].date(), "| last:", last.date())
    print("  columns:", list(df.columns))
    print("  index timezone:", df.index.tz)
    print("  missing values:", {c: int(n) for c, n in df.isna().sum().items() if n})
    if last.date() == now_et.date() and now_et.hour < 16:
        print("  WARNING: last bar is today and the market has not closed -> partial bar")
    if "Stock Splits" in df.columns:
        s = df["Stock Splits"]
        s = s[s > 0]
        print("  splits in range:", {d.date().isoformat(): v for d, v in s.items()} or "none")
    if "Adj Close" in df.columns:
        gap = (df["Close"] - df["Adj Close"]).abs()
        print(f"  Close minus Adj Close: largest gap {gap.max():.4f}, latest-row gap {gap.iloc[-1]:.4f}")
    print()

# NVDA did a 10-for-1 split effective June 10, 2024.
# If Close is split-adjusted, prices before and after June 10 are similar (no 10x drop).
print("=== NVDA around its 10-for-1 split (June 10, 2024)")
nv = yf.Ticker("NVDA").history(start="2024-06-05", end="2024-06-13", auto_adjust=False)
cols = [c for c in ["Close", "Adj Close", "Volume"] if c in nv.columns]
print(nv[cols].round(2).to_string())