"""Spike step 5: how much history does SEC EDGAR companyfacts give us?"""
import os
import sys
import time
from datetime import date
from pathlib import Path

import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")
UA = os.getenv("SEC_USER_AGENT")
if not UA:
    sys.exit("SEC_USER_AGENT missing from .env")
HEADERS = {"User-Agent": UA}

SYMBOLS = ["AAPL", "MSFT", "NVDA", "JPM", "BRK-B"]
REVENUE = ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"]


def get(url):
    time.sleep(0.2)  # SEC allows 10 requests/second; stay well under
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def length_days(f):
    return (date.fromisoformat(f["end"]) - date.fromisoformat(f["start"])).days


def periods(facts, concept, unit, lo, hi):
    """First-reported value for each period end, keeping periods lo..hi days long."""
    items = facts.get("us-gaap", {}).get(concept, {}).get("units", {}).get(unit, [])
    best = {}
    for f in items:
        if "start" not in f or not (lo <= length_days(f) <= hi):
            continue
        if f["end"] not in best or f["filed"] < best[f["end"]]["filed"]:
            best[f["end"]] = f
    return [best[k] for k in sorted(best)]


def summary(rows):
    if not rows:
        return "none"
    return f"{len(rows)} periods, oldest {rows[0]['end']}, newest {rows[-1]['end']}"


tickers = get("https://www.sec.gov/files/company_tickers.json")
cik_by_symbol = {v["ticker"]: v["cik_str"] for v in tickers.values()}

for sym in SYMBOLS:
    print(f"=== {sym}")
    cik = cik_by_symbol.get(sym)
    if cik is None:
        print("  not found in SEC ticker list")
        continue
    data = get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json")
    facts = data["facts"]
    print(f"  CIK {cik:010d}  {data.get('entityName')}")

    annual = periods(facts, "EarningsPerShareDiluted", "USD/shares", 350, 380)
    print(f"  annual diluted EPS: {summary(annual)}")
    for f in annual[-3:]:
        print(f"    end {f['end']}  val {f['val']}  filed {f['filed']}  form {f['form']}")

    quarterly = periods(facts, "EarningsPerShareDiluted", "USD/shares", 80, 100)
    print(f"  quarterly diluted EPS: {summary(quarterly)}")
    for f in quarterly[-6:]:
        print(f"    end {f['end']}  val {f['val']}  filed {f['filed']}  form {f['form']}")

    for concept in REVENUE:
        print(f"  annual {concept}: {summary(periods(facts, concept, 'USD', 350, 380))}")
    print(f"  annual NetIncomeLoss: {summary(periods(facts, 'NetIncomeLoss', 'USD', 350, 380))}")
    print()
