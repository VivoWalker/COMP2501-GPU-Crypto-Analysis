"""
Data Alignment & Final Dataset Assembly
=========================================
Addresses the frequency mismatch:
  - Crypto prices: daily (high frequency)
  - GPU eBay prices: monthly (low frequency)

Strategy:
  1. Resample crypto daily → monthly (mean, max, min, std).
  2. Merge GPU eBay prices on (date, model).
  3. Join GPU specs (VRAM, hashrate, MSRP) on model.
  4. Derive analysis features: premium_pct, price_per_mh.
  5. Output long-format and wide-format CSVs for R.

Output: data/processed/final_dataset.csv
          data/processed/final_dataset_monthly.csv
"""

import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW  = PROJECT_ROOT / "data" / "raw"
DATA_PROC = PROJECT_ROOT / "data" / "processed"
DATA_PROC.mkdir(parents=True, exist_ok=True)

CRYPTO_PATH   = DATA_RAW / "crypto_prices.csv"
GPU_SPECS_PATH = DATA_RAW / "gpu_specs.csv"
GPU_PRICE_PATH = DATA_RAW / "ebay_gpu_prices.csv"

OUTPUT_MARKET   = DATA_PROC / "final_dataset.csv"
OUTPUT_MONTHLY  = DATA_PROC / "final_dataset_monthly.csv"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def build_monthly_crypto(path):
    """Down-sample daily crypto to monthly OHLC + volatility."""
    df = pd.read_csv(path, parse_dates=["date"])
    df["month"] = df["date"].dt.to_period("M")

    monthly = df.groupby("month").agg(
        btc_avg  = ("BTC_price_usd", "mean"),
        btc_high = ("BTC_price_usd", "max"),
        btc_low  = ("BTC_price_usd", "min"),
        btc_std  = ("BTC_price_usd", "std"),
        eth_avg  = ("ETH_price_usd", "mean"),
        eth_high = ("ETH_price_usd", "max"),
        eth_low  = ("ETH_price_usd", "min"),
        eth_std  = ("ETH_price_usd", "std"),
    ).reset_index()

    monthly["month"] = monthly["month"].dt.to_timestamp()
    return monthly


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("Data Alignment & Merge  —  2020/09 → 2022/09\n" + "=" * 48)

    # 1. Load crypto (monthly)
    print("1. Resampling crypto daily → monthly …")
    crypto_m = build_monthly_crypto(CRYPTO_PATH)
    print(f"   {len(crypto_m)} monthly rows")

    # 2. Load GPU eBay prices
    print("2. Loading GPU eBay prices …")
    gpu_prices = pd.read_csv(GPU_PRICE_PATH, parse_dates=["date"])
    print(f"   {len(gpu_prices)} rows, {gpu_prices['model'].nunique()} models")
    print(f"   Source: {gpu_prices['data_source'].iloc[0]}")

    # 3. Load GPU specs
    print("3. Loading GPU specs …")
    specs = pd.read_csv(GPU_SPECS_PATH)
    print(f"   {len(specs)} GPU models")

    # 4. Merge GPU prices ↔ specs on model (lhr comes from gpu_prices)
    combined = gpu_prices.merge(
        specs[["model", "vram_gb", "msrp_usd", "eth_hashrate_mh",
                "architecture"]],
        on="model", how="left"
    )

    # 5. Merge with crypto (on date)
    combined = combined.merge(
        crypto_m, left_on="date", right_on="month", how="left"
    ).drop(columns=["month"])

    # 6. Derived features
    combined["premium_pct"] = (
        (combined["ebay_avg_price_usd"] - combined["msrp_usd"])
        / combined["msrp_usd"] * 100
    ).round(2)

    combined["price_per_mh"] = (
        combined["ebay_avg_price_usd"] / combined["eth_hashrate_mh"]
    ).round(2)

    # 7. Sort, clean column order
    combined = combined.sort_values(["model", "date"]).reset_index(drop=True)

    # Rename for consistency with analysis.R
    combined = combined.rename(columns={
        "ebay_avg_price_usd": "street_price_usd"
    })

    col_order = [
        "date", "model", "tier", "architecture", "vram_gb", "lhr",
        "msrp_usd", "street_price_usd", "premium_pct",
        "eth_hashrate_mh", "price_per_mh",
        "eth_avg", "eth_high", "eth_low", "eth_std",
        "btc_avg", "btc_high", "btc_low", "btc_std",
        "data_source",
    ]
    combined = combined[[c for c in col_order if c in combined.columns]]

    combined.to_csv(OUTPUT_MARKET, index=False)
    print(f"\n   Final dataset: {len(combined)} rows → {OUTPUT_MARKET}")
    print(f"   Models: {combined['model'].nunique()}  |  "
          f"Tiers: {sorted(combined['tier'].dropna().unique())}")
    print(f"   Date range: {combined['date'].min().date()} → "
          f"{combined['date'].max().date()}")

    # 8. Wide-format export (for R plotting convenience)
    print("\n4. Exporting wide-format variant …")
    wide = combined.pivot_table(
        index="date",
        columns="model",
        values=["street_price_usd", "premium_pct", "price_per_mh"],
    )
    wide.columns = ["_".join(str(c).strip().replace(" ", "_")
                             for c in col) for col in wide.columns]
    wide = wide.reset_index()
    wide = wide.merge(
        crypto_m, left_on="date", right_on="month", how="left"
    ).drop(columns=["month"])
    wide.to_csv(OUTPUT_MONTHLY, index=False)
    print(f"   Wide-format {len(wide)} rows → {OUTPUT_MONTHLY}")

    print("\nData alignment complete.")

if __name__ == "__main__":
    main()
