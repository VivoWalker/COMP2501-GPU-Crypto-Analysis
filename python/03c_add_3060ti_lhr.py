"""
Replace estimated RTX 3060 LHR with real RTX 3060 Ti LHR data.
User-provided data from TechSpot / Tom's Hardware.

Changes:
  1. gpu_specs.csv: remove RTX 3060 LHR, add RTX 3060 Ti LHR
  2. ebay_gpu_prices.csv: remove RTX 3060 LHR rows, add RTX 3060 Ti LHR rows
"""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
SPECS_PATH = DATA_RAW / "gpu_specs.csv"
PRICE_PATH = DATA_RAW / "ebay_gpu_prices.csv"

# ============================================================
# Real RTX 3060 Ti LHR price data from user's sources
# ============================================================
RTX3060TI_LHR_REAL = [
    # (date, low, high, source_note)
    ("2021-05-01",  700,  950, "TechSpot — LHR launch month"),
    ("2021-06-01",  750, 1000, "TechSpot"),
    ("2021-07-01",  800, 1050, "TechSpot"),
    ("2021-08-01",  850,  850, "TechSpot Aug — ~952 mixed, LHR ~850"),
    ("2021-09-01",  750,  950, "Tom's Hardware"),
    ("2021-10-01",  700,  900, "Tom's Hardware"),
    ("2021-11-01",  680,  880, "Tom's Hardware"),
    ("2021-12-01",  700,  850, "Tom's Hardware"),
    ("2022-01-01",  600,  800, "Tom's Hardware"),
    ("2022-02-01",  550,  750, "Tom's Hardware"),
    ("2022-03-01",  520,  720, "Tom's Hardware"),
    ("2022-04-01",  450,  650, "Tom's Hardware"),
    ("2022-05-01",  400,  580, "Tom's Hardware"),
    ("2022-06-01",  350,  550, "Tom's Hardware — ~420-470"),
    ("2022-07-01",  340,  520, "Tom's Hardware"),
    ("2022-08-01",  320,  500, "Tom's Hardware"),
    ("2022-09-01",  300,  450, "Tom's Hardware"),
]


def main():
    print("Replacing RTX 3060 LHR (estimated) with RTX 3060 Ti LHR (real data)\n")

    # ---- 1. Update GPU specs ----
    specs = pd.read_csv(SPECS_PATH)
    print(f"GPU specs before: {len(specs)} models")
    print(f"  Models: {sorted(specs['model'].unique())}")

    # Remove RTX 3060 LHR
    specs = specs[specs["model"] != "RTX 3060 LHR"].copy()

    # Add RTX 3060 Ti LHR
    # RTX 3060 Ti non-LHR = 60 MH/s; LHR reduces to ~55% = 33 MH/s
    new_row = {
        "model": "RTX 3060 Ti LHR",
        "tier": "XX60",
        "vram_gb": 8,
        "lhr": 1,
        "release_date": "2021-05-19",
        "eth_hashrate_mh": 33,
        "msrp_usd": 399,
        "architecture": "Ampere",
    }
    specs = pd.concat([specs, pd.DataFrame([new_row])], ignore_index=True)
    specs.to_csv(SPECS_PATH, index=False)
    print(f"GPU specs after: {len(specs)} models")
    print(f"  Models: {sorted(specs['model'].unique())}")

    # ---- 2. Update eBay prices ----
    prices = pd.read_csv(PRICE_PATH)
    print(f"\neBay prices before: {len(prices)} rows")

    # Remove all RTX 3060 LHR rows
    removed = len(prices[prices["model"] == "RTX 3060 LHR"])
    prices = prices[prices["model"] != "RTX 3060 LHR"].copy()

    # Add RTX 3060 Ti LHR rows
    new_rows = []
    for date_str, low, high, source_note in RTX3060TI_LHR_REAL:
        midpoint = round((low + high) / 2)
        new_rows.append({
            "date": date_str,
            "model": "RTX 3060 Ti LHR",
            "tier": "XX60",
            "ebay_avg_price_usd": midpoint,
            "data_source": f"TechSpot / Tom's Hardware — range ${low}-${high} (midpoint used)",
            "lhr": 1,
        })

    prices = pd.concat([prices, pd.DataFrame(new_rows)], ignore_index=True)
    prices = prices.sort_values(["date", "model"]).reset_index(drop=True)
    prices.to_csv(PRICE_PATH, index=False)
    print(f"eBay prices after: {len(prices)} rows")
    print(f"  Removed {removed} RTX 3060 LHR rows (estimated)")
    print(f"  Added {len(new_rows)} RTX 3060 Ti LHR rows (real data)")

    # ---- Summary ----
    print(f"\n=== Updated LHR models (all real data now) ===")
    lhr_rows = prices[prices["lhr"] == 1].sort_values(["model", "date"])
    for _, row in lhr_rows.iterrows():
        print(f"  {row['date']}  {row['model']:22s}  ${row['ebay_avg_price_usd']:5.0f}")
    print(f"\n  Total LHR rows: {len(lhr_rows)} (ALL from real published sources)")


if __name__ == "__main__":
    main()
