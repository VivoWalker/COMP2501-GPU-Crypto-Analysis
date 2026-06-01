# Analysis of NVIDIA GPU Market Dynamics and Cryptocurrency Correlations

A data-driven investigation into how cryptocurrency price movements
(Ethereum and Bitcoin) influence the secondary-market (eBay) pricing of
NVIDIA GeForce GPUs, with a focus on VRAM capacity and Lite Hash Rate (LHR)
technology.

**Focus period:** 2020/09 – 2022/09 (mining boom through crash)

## Project Structure

```
.
├── README.md
├── data/
│   ├── raw/
│   │   ├── crypto_prices.csv          # ← 01_fetch_crypto.py
│   │   ├── gpu_specs.csv              # ← 02_fetch_gpu_specs.py
│   │   └── ebay_gpu_prices.csv        # ← 03_fetch_gpu_prices.py
│   └── processed/
│       ├── final_dataset.csv          # ← 04_merge_and_align.py (long format)
│       └── final_dataset_monthly.csv  # Wide-format variant
├── python/
│   ├── 01_fetch_crypto.py             # BTC & ETH from CoinGecko API
│   ├── 02_fetch_gpu_specs.py          # GPU specs (VRAM, LHR, hashrate, MSRP)
│   ├── 03_fetch_gpu_prices.py         # Real eBay prices from published sources
│   └── 04_merge_and_align.py          # Merge, align, derive features
├── r/
│   └── analysis.R                     # 6 statistical visualizations
├── output/
│   └── figures/                       # Generated PNG plots (6 figures)
└── presentation/
    ├── 01_Problem_Definition/
    ├── 02_Methodology/
    ├── 03_Results_and_Findings/
    └── 04_Conclusion/
```

## Quick Start

### 1. Environment Setup

**Python** (3.9+):
```bash
pip install pandas numpy requests scipy
```

**R** (4.2+):
```r
install.packages(c(
  "tidyverse", "scales", "showtext", "corrplot", "broom", "here"
))
```

### 2. Run the Pipeline (in order, from project root)

```bash
# Step 1 — Fetch cryptocurrency data from CoinGecko (no API key needed)
python python/01_fetch_crypto.py

# Step 2 — Generate GPU specifications table
python python/02_fetch_gpu_specs.py

# Step 3 — Compile real eBay GPU price data from published sources
python python/03_fetch_gpu_prices.py

# Step 4 — Align frequencies, merge, derive features
python python/04_merge_and_align.py

# Step 5 — Run R statistical analysis and generate figures
Rscript r/analysis.R
```

## Data Sources

| Component | Source | Description |
|-----------|--------|-------------|
| **Crypto prices** | [CoinGecko API](https://www.coingecko.com/en/api) | Free tier, daily BTC & ETH (volume-weighted avg across exchanges) |
| **GPU specifications** | NVIDIA / TechPowerUp | VRAM, LHR status, release dates, ETH hashrate benchmarks |
| **GPU eBay prices** | Curated from published journalism | See below |

### GPU Price Data Provenance

GPU prices are compiled from three trusted, publicly published sources that
independently tracked eBay sold listings during the 2020–2022 mining boom:

1. **Tom's Hardware** — "eBay Historical GPU Prices" bi-weekly series.
   Tracked 60+ GPUs, filtered for genuine sold listings only (excluded
   "box only", "photo", bundles, and non-working cards).

2. **PCMag** — Jan/Feb 2021 analysis using eBay's Terapeak sold-item data.
   Cross-referenced with Tom's Hardware for consistency.

3. **3D Center** (Germany) — GPU price index tracking eBay markups vs MSRP.

4. **Michael Driscoll** (data engineer) — Published analysis of 49,580 RTX
   30-series resales worth $61.5M on eBay + StockX.

All three sources used the same methodology: query eBay **sold** listings,
filter noise, compute monthly average sold price per GPU model.

> **Note on LHR variants:** LHR (Lite Hash Rate) cards launched May 2021.
> Published sources track prices by model name without always distinguishing
> LHR vs non-LHR. LHR-variant prices are estimated using a time-varying
> discount factor (10–20% below non-LHR during the boom, narrowing to ~3%
> after the crash), consistent with Tom's Hardware commentary.

## Methodology Summary

### Time Lag Analysis
Cross-Correlation Function (CCF) between ETH price and GPU street
price identifies the typical lag (in months) before cryptocurrency
market shifts materialize in GPU pricing.

### Magnitude Analysis
OLS regression: `premium_pct ~ vram_gb + lhr + eth_hashrate_mh`
quantifies how much each hardware attribute contributes to the size
of price swings during crypto rallies.

### Volatility by Tier
Boxplots of month-over-month % price change, grouped by GPU tier
(XX60 through XX90), reveal which segment of the market is most
sensitive to crypto-driven demand shocks.

## Presentation Mapping

| Section | Key Visual | Description |
|---------|-----------|-------------|
| **01 Problem Definition** | — | Context: 2021 mining boom, scalping, LHR introduction |
| **02 Methodology** | — | Python (CoinGecko API, pandas) & R (ggplot2, CCF) pipeline |
| **03 Results & Findings** | `01_dual_axis_timeseries.png` | ETH price vs GPU tier pricing over time |
| | `02_ccf_eth_gpu3080.png` | Cross-correlation lag analysis |
| | `03_regression_coefficients.png` | VRAM, LHR, hashrate effect sizes |
| | `04_volatility_boxplot.png` | Price volatility by tier |
| | `05_correlation_heatmap.png` | Full variable correlation matrix |
| | `06_lhr_premium_comparison.png` | LHR premium at peak vs trough |
| **04 Conclusion** | — | LHR effectiveness, VRAM's role, market efficiency |

## Why CoinGecko Prices May Differ from Google

CoinGecko uses a **volume-weighted average** across hundreds of
exchanges (Binance, Coinbase, Kraken, etc.). Google Finance may show
a single exchange (e.g., Coinbase spot price) or use a different
aggregation method. The differences are typically 1–3% and do not
affect the time-series correlation structure used in this analysis.

## Reproducibility

- CoinGecko data uses fixed UTC timestamps for deterministic pull windows.
- GPU price reference points are documented in `03_fetch_gpu_prices.py`.
- R figures include data source captions.
- Package versions can be obtained via `pip freeze` / `sessionInfo()`.

## License

This project is created for academic purposes (COMP2501 coursework).
All GPU price data is attributed to the original published sources
(Tom's Hardware, PCMag, 3D Center, Michael Driscoll).
