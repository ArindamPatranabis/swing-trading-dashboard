"""Spike step 5b: which per-share concepts does Berkshire report?"""
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
UA = os.getenv("SEC_USER_AGENT")
if not UA:
    sys.exit("SEC_USER_AGENT missing from .env")

url = "https://data.sec.gov/api/xbrl/companyfacts/CIK0001067983.json"
data = requests.get(url, headers={"User-Agent": UA}, timeout=30).json()

for taxonomy, concepts in data["facts"].items():
    for name, body in concepts.items():
        if "PerShare" not in name:
            continue
        for unit, items in body["units"].items():
            latest = max(items, key=lambda f: (f["end"], f["filed"]))
            print(f"{taxonomy}:{name}  unit {unit}  facts {len(items)}  "
                  f"latest end {latest['end']}  val {latest['val']}  form {latest['form']}")
