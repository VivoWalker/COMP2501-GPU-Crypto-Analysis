"""
Crypto Data Acquisition
========================
Fetches historical daily price data for Bitcoin (BTC) and Ethereum (ETH)
from Yahoo Finance via the yfinance library.

Yahoo Finance provides reliable historical daily OHLCV data sourced from
major exchanges. We use the adjusted close price, which accounts for any
corporate actions (splits, dividends) — though for crypto these are
generally identical to the raw close.

Output: data/raw/crypto_prices.csv
"""

import sys
import pandas as pd
import yfinance as yf
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TICKERS = {"BTC-USD": "BTC", "ETH-USD": "ETH"}

# Time window: 2019-01-01 through 2022-09-30
# - 2019 through mid-2020: pre-mining-boom baseline
# - 2020/09 through 2022/09: the mining boom (+ crash) focus period
START_DATE = "2019-01-01"
END_DATE   = "2022-09-30"

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / "crypto_prices.csv"

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("Crypto Data Acquisition  —  Yahoo Finance\n" + "=" * 48)
    print(f"Window: {START_DATE} → {END_DATE}")
    print(f"Tickers: {', '.join(TICKERS.keys())}")
    print(f"Source: Yahoo Finance adjusted close\n")

    print("  Downloading … ", end="", flush=True)
    df = yf.download(
        list(TICKERS.keys()),
        start=START_DATE,
        end=END_DATE,
        progress=False,
    )

    if df.empty:
        raise RuntimeError(
            "Download returned no data. Check your internet connection."
        )

    # yfinance returns a MultiIndex DataFrame (Price × Ticker). Access the
    # 'Close' level to get closing prices for all tickers at once.
    close = df.xs("Close", axis=1, level=0)

    # Build clean columns: date, BTC_price_usd, ETH_price_usd
    result = close.reset_index()
    result = result.rename(columns={
        t: f"{l}_price_usd" for t, l in TICKERS.items()
    })
    result["date"] = result["Date"].dt.date
    result = result.drop(columns=["Date"])

    # Keep only the columns we need
    keep = ["date", "BTC_price_usd", "ETH_price_usd"]
    result = result[[c for c in keep if c in result.columns]]

    # Round prices
    for col in ["BTC_price_usd", "ETH_price_usd"]:
        if col in result.columns:
            result[col] = result[col].round(2)

    # Drop rows where both prices are missing
    result = result.dropna(subset=["BTC_price_usd", "ETH_price_usd"], how="all")
    result = result.sort_values("date").reset_index(drop=True)

    print(f"({len(result)} days) done")

    # Sanity checks
    for ticker, label in TICKERS.items():
        col = f"{label}_price_usd"
        if col not in result.columns:
            print(f"\n  ERROR: missing column '{col}'", file=sys.stderr)
            raise KeyError(col)

    btc_max = result["BTC_price_usd"].max()
    eth_max = result["ETH_price_usd"].max()
    print(f"  BTC max: ${btc_max:,.2f}  |  ETH max: ${eth_max:,.2f}")

    if btc_max < 50000:
        print("  WARNING: BTC max below $50k — expected $60k+ in 2021 peak.")
    if eth_max < 3000:
        print("  WARNING: ETH max below $3k — expected $4k+ in 2021 peak.")

    result.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved {len(result):,} daily rows → {OUTPUT_PATH}")
    print(f"Date range: {result['date'].min()} → {result['date'].max()}")


if __name__ == "__main__":
    main()
