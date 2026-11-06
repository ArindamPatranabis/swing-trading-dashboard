"""Day-1 spike, step 3: statements, company info and earnings dates from yfinance."""
import warnings
warnings.filterwarnings("ignore", message=".*inplace keyword.*")

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf

SYMBOLS = ["AAPL", "MSFT", "NVDA", "JPM", "BRK-B"]
INFO_FIELDS = ["longName", "sector", "industry", "marketCap",
               "sharesOutstanding", "heldPercentInsiders", "trailingPE"]
now_et = datetime.now(ZoneInfo("America/New_York"))


def eps_summary(stmt, label):
    if stmt is None or stmt.empty:
        print(f"  {label}: EMPTY")
        return
    periods = [c.date().isoformat() for c in stmt.columns]
    print(f"  {label}: {len(periods)} periods, newest {periods[0]}, oldest {periods[-1]}")
    for row in ["Diluted EPS", "Basic EPS"]:
        if row in stmt.index:
            vals = stmt.loc[row]
            filled = int(vals.notna().sum())
            shown = {c.date().isoformat(): (None if pd.isna(v) else round(float(v), 3))
                     for c, v in vals.items()}
            print(f"    {row}: {filled} of {len(vals)} filled -> {shown}")
        else:
            print(f"    {row}: row missing")


for sym in SYMBOLS:
    print(f"=== {sym}")
    t = yf.Ticker(sym)
    try:
        eps_summary(t.income_stmt, "annual income statement")
    except Exception as e:
        print("  annual ERROR:", type(e).__name__, e)
    try:
        eps_summary(t.quarterly_income_stmt, "quarterly income statement")
    except Exception as e:
        print("  quarterly ERROR:", type(e).__name__, e)
    try:
        info = t.info
        print("  info:", {k: info.get(k) for k in INFO_FIELDS})
    except Exception as e:
        print("  info ERROR:", type(e).__name__, e)
    try:
        print("  option expiries listed:", len(t.options))
    except Exception as e:
        print("  options ERROR:", type(e).__name__, e)
    try:
        ed = t.get_earnings_dates(limit=8)
        if ed is None or ed.empty:
            print("  earnings dates: EMPTY")
        else:
            future = ed[ed.index > now_et]
            nxt = future.index.min() if len(future) else None
            print("  earnings dates: columns", list(ed.columns), "| next:", nxt)
    except Exception as e:
        print("  earnings ERROR:", type(e).__name__, e)
    print()
