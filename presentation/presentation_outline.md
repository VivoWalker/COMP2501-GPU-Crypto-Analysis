# Analysis of NVIDIA GPU Market Dynamics and Cryptocurrency Correlations
## COMP2501 Project Presentation — Full Outline for Canva AI

**Period:** 2020/09 – 2022/09 (Mining Boom to Crash)
**Tools:** Python (pandas, statsmodels, scipy, matplotlib, seaborn) + R (tidyverse, ggplot2, broom, corrplot)
**Data:** All real published sources, zero fabrication

---

## Slide 1 — Title Slide
- **Title:** Analysis of NVIDIA GPU Market Dynamics and Cryptocurrency Correlations
- **Subtitle:** 2020/09 – 2022/09: A Full-Cycle Study from Mining Boom to Market Crash
- **Course:** COMP2501
- **Your Name**

---

## Slide 2 — Background: What Happened in 2020–2022?
- Late 2020 – 2021: Ethereum surged from ~$400 to ~$4,800. GPU mining became highly profitable
- Miners bought GPUs in bulk, causing global shortages. eBay secondary-market prices soared to 2–3× MSRP (official retail price)
- May 2021: NVIDIA launched LHR (Lite Hash Rate) technology — halved mining hash rate via driver-level locks, aiming to return GPUs to gamers
- Mid-2022: Crypto market crashed. ETH fell to ~$1,300. GPU prices collapsed in tandem
- **Core phenomenon: GPU secondary-market prices moved closely with cryptocurrency prices, but the strength, time lag, and driving factors of this relationship were never systematically quantified**

---

## Slide 3 — Research Questions
1. Do cryptocurrency price movements drive GPU secondary-market prices? If so, what is the time lag?
2. Which GPU hardware attributes (VRAM, hash rate, LHR) explain the magnitude of price premiums over MSRP?
3. Did LHR technology actually reduce miners' willingness to pay? How persistent was the effect?
4. Do different GPU tiers (XX60 entry-level to XX90 flagship) exhibit different price volatility?
5. BTC vs ETH: which cryptocurrency drives GPU prices more? (GPUs mine ETH, not BTC)

---

## Slide 4 — Why These Questions Matter
- **Consumers / Gamers:** Understand GPU price cycles to know when to buy or sell
- **NVIDIA / Hardware Industry:** Evaluate whether anti-mining strategies like LHR actually work in the marketplace
- If cryptocurrency markets systematically transmit price shocks to hardware supply chains, this externality deserves to be measured

---

## Slide 5 — Difficulties in Answering These Questions
- **Common trend problem:** Crypto prices and GPU prices both rose during the tech boom — simple correlation may be spurious. First-differencing is needed to isolate the real signal
- **Multicollinearity:** High-VRAM cards also have higher MSRP and higher hash rates. The variables are highly entangled
- **Frequency mismatch:** Cryptocurrency data is daily; GPU eBay data is monthly. They must be aligned
- **BTC-ETH collinearity:** BTC and ETH are themselves highly correlated (r ≈ 0.9), making it hard to separate their individual effects

---

## Slide 6 — Data Sources

**Cryptocurrency Prices:**
- Source: CoinGecko API (free tier, no API key required)
- BTC and ETH daily prices, volume-weighted average across hundreds of exchanges

**GPU Specifications:**
- Source: NVIDIA official specs / TechPowerUp database
- VRAM (GB), ETH hash rate (MH/s), MSRP (USD), release date, architecture

**GPU eBay Prices — Detailed Collection Methodology:**
- Not from an API — manually curated from three authoritative tech journalism sources that independently tracked eBay sold listings:

| Source | Method |
|--------|--------|
| Tom's Hardware | Bi-weekly "eBay Historical GPU Prices" series. Tracked 60+ GPUs. Filtered for genuine sold listings only — excluded "box only," "photo," non-working cards, and bundles |
| PCMag | Used eBay's official Terapeak sold-item data tool for Jan/Feb 2021 analysis. Cross-referenced with Tom's Hardware |
| 3D Center (Germany) | GPU price index tracking eBay markups vs MSRP over time |

- Common methodology across all sources: (1) Query eBay sold listings only (not asking prices), (2) Filter out noise, (3) Compute monthly average sold price per GPU model
- LHR variant prices: Sourced from TechSpot + Tom's Hardware published LHR price ranges. Range midpoints used as point estimates

**Final Dataset:**
- 10 GPU models (7 non-LHR + 3 LHR), 24 months (2020/09 – 2022/09)
- All 190+ data points from real published sources

---

## Slide 7 — Technical Stack
- **Python 3.9+:** pandas (data processing), numpy, statsmodels (OLS regression), scipy (statistical tests), matplotlib + seaborn (visualization)
- **R 4.2+:** tidyverse (dplyr + ggplot2), broom (regression output), corrplot (heatmap), showtext (typography)
- **Data acquisition:** CoinGecko REST API (free tier, no authentication needed)
- **Reproducibility:** Fixed UTC timestamps, full source attribution for every data point, `pip freeze` / `sessionInfo()` for environment lock-in

---

## Slide 8 — Existing Works and References

**Academic Papers:**

| Paper | Method | Key Finding | Gap |
|-------|--------|-------------|-----|
| Wilson (2021), *Applied Finance Letters* | Simple correlation, eBay scalper prices | RTX 3060 Ti / 3080 second-hand prices significantly positively correlated with daily ETH returns | Only contemporaneous correlation; no lag analysis; no LHR |
| McMillan (2022), Princeton Thesis | Two-stage least squares (2SLS) | GPU supply elasticity = 0.573; mining cost consumers ~$863M | Data ends in 2020; pre-LHR era |
| Nurfaizy et al. (2022), *Jurnal Ilmiah Wahana Pendidikan* | SVR machine learning prediction | RTX 30-series best prediction accuracy (RMSE 0.03–0.06) for GPU prices from crypto signals | Pure prediction, no causal inference |
| Zięba (2023), *Int. Review of Economics & Finance* | Co-movement measure, asset pricing framework | BTC price long-run aligns with PoW marginal cost (hardware + electricity) | Not focused on secondary GPU market |
| Demkowicz et al. (2022), WEBIST | Empirical benchmarks of old GPUs | Secondary-market mining viability data for older cards | Engineering focus; no price-crypto correlation |

**What Makes This Project Different:**

| Dimension | Existing Literature | This Project |
|-----------|-------------------|--------------|
| LHR Effect Quantification | No paper addresses LHR | First to use LHR as a regression variable + paired comparison |
| Lag Analysis | Wilson (2021): contemporaneous only | Systematic CCF across all models with lag summary table |
| Premium Attribution | Does not distinguish GPU attributes | OLS multiple regression: VRAM + LHR + Hashrate, controlling for MSRP |
| BTC vs ETH Separation | Most studies conflate both | Partial correlation — isolates each crypto's independent contribution |
| Data Provenance | Single source or scraped | Triple-source cross-validation (Tom's Hardware / PCMag / 3D Center) |

**References:**
- Wilson, L. (2021). GPU Prices and Cryptocurrency Returns. *Applied Finance Letters*, 11(1). DOI: 10.24135/afl.v11i1.503
- McMillan, T. (2022). The Impact of Bitcoin on Consumer GPU Prices. *Princeton University Senior Thesis*. https://dataspace.princeton.edu/handle/88435/dsp01f7623g758
- Nurfaizy, P. M., Jajuli, M., & Enri, U. (2022). NVIDIA Graphics Card Price Prediction Based on the Effect of Cryptocurrency Price Using SVR. *Jurnal Ilmiah Wahana Pendidikan*, 8, 280–287.
- Zięba, D. (2023). If GPU(time) == Money. *International Review of Economics & Finance*, 89, 863–912.
- Demkowicz, J., Rutkowski, M., & Falkowski-Gilski, P. (2022). Quality of Cryptocurrency Mining on Previous Generation NVIDIA GTX GPUs. *WEBIST 2022*, SciTePress. DOI: 10.5220/0011567400003318
- Tom's Hardware. GPU Historical eBay Pricing. https://www.tomshardware.com/news/gpus-historical-ebay-pricing
- PCMag. Prices for Nvidia RTX 3000 Graphics Cards Are Getting Insane on eBay. Jan/Feb 2021.
- 3D Center. GPU Price Index. https://www.3dcenter.org/
- Driscoll, M. I Analysed 49,580 Resales of the RTX 30-series Worth $61.5M. dev.to, 2021.
- CoinGecko API. https://www.coingecko.com/en/api
- TechSpot. LHR GPU Reviews and Pricing. https://www.techspot.com/

---

## Slide 9 — Figure 1: Time Series Overview
**Two-panel visualization:**
- **Top panel:** ETH price vs four GPU tier median eBay prices (dual Y-axis). All tiers peak around May 2021 (LHR launch), crash through mid-2022
- **Bottom panel:** Individual non-LHR GPU model price trajectories
- **Key observation:** GPU prices across all tiers move in strong visual sync with ETH; XX90 has the highest absolute price (~$3,200 at peak); XX60 is the cheapest in absolute terms (~$900 at peak). (Percentage markup over MSRP is analyzed separately in Figure 3 — it's not visible from this chart.)

---

## Slide 10 — Figure 2: Cross-Correlation — Does ETH Lead GPU Prices?
**CCF plot:** ETH price vs RTX 3080 eBay price
- Negative lag = ETH leads GPU
- Multi-model CCF peak lag summary table
- **Finding:** ETH price leads GPU price by approximately 1–2 months (peak CCF at negative lag). The secondary market does not react instantly — there is a measurable delay before crypto shifts materialize in GPU pricing

---

## Slide 11 — Figure 3: Regression — What Drives GPU Price Premium?
**Forest plot:** OLS coefficient estimates with 95% confidence intervals
- Model: `premium_pct ~ vram_gb + lhr + eth_hashrate_mh`
- **Findings:**
  - VRAM (+): Each additional GB of VRAM → higher premium (after controlling for MSRP)
  - LHR (−): LHR status significantly reduces premium over MSRP
  - Hashrate (+): Higher mining efficiency → higher premium
  - All coefficients statistically significant

---

## Slide 12 — Figure 4: LHR Real Impact — Three Paired Comparisons
**Three side-by-side panels:** RTX 3060 Ti / RTX 3070 / RTX 3080 — LHR vs Non-LHR price trajectories
- **Core finding: The LHR price gap is NOT constant — it varies with market conditions:**
  - During mining boom (mid-2021): LHR cards sold 20%–37% below non-LHR
  - After crypto crash (mid-2022): Gap narrowed to ~3%
- **Interpretation:** LHR only matters when mining is profitable. The market, not NVIDIA's technology, determines LHR's effectiveness
- All LHR prices from real published sources (TechSpot / Tom's Hardware), not synthetic

---

## Slide 13 — Figure 5: Crash Analysis — Peak-to-Trough Decline
**Horizontal bar chart:** All GPU models ranked by peak-to-trough percentage decline
- **Findings:**
  - Average decline: ~50–70% across all models
  - XX90 (flagship) had largest absolute dollar decline
  - LHR and non-LHR variants show similar decline patterns once crypto crashed
- Each bar annotated with peak price → trough price

---

## Slide 14 — Figure 6: Mining Economics — Cost Per Hashrate
**Two-panel visualization:**
- **Left:** $/MH/s over time by GPU tier — all tiers converge after the crash
- **Right:** $/MH/s by individual GPU model — LHR cards (dashed lines) consistently show worse mining value (higher $/MH)
- **Finding:** When mining is unprofitable, all GPUs converge to similar $/MH; LHR permanently degrades mining value regardless of market conditions

---

## Slide 15 — Figure 7: BTC vs ETH — Which Truly Drives GPU Prices?
**Two-panel bar chart:**
- **Left:** Simple Pearson correlations — ETH r and BTC r with GPU prices
- **Right:** Partial correlations — ETH (controlling for BTC) vs BTC (controlling for ETH)
- **Finding:** ETH has stronger partial correlation with GPU prices than BTC. This makes economic sense — GPUs mine ETH, not BTC. The BTC-GPU correlation is largely driven by BTC-ETH co-movement

---

## Slide 16 — Figures 8 & 9: Volatility Analysis + Correlation Heatmap
**Volatility boxplot (by tier):**
- Month-over-month % price change distributions for XX60 through XX90
- ANOVA test for tier differences
- **Finding:** Entry/mid-tier cards (XX60, XX70) show wider price swings than high-end (XX80, XX90)

**Correlation heatmap:**
- Full variable matrix: GPU price, premium %, ETH price, BTC price, ETH volatility, VRAM, hash rate, price per MH/s
- **Finding:** ETH price and GPU premium show strong positive correlation; LHR is negatively correlated with premium

---

## Slide 17 — Key Challenges Encountered During Analysis

**Challenge 1: LHR price gap is time-varying — not a constant discount**
- Initial expectation: LHR cards are always X% cheaper than non-LHR
- Reality: The gap ranged from 37% (mining boom) to 3% (post-crash)
- Solution: Used real published LHR price ranges from TechSpot/Tom's Hardware instead of a fixed discount factor. This finding itself became a key conclusion — LHR effectiveness is market-state-dependent

**Challenge 2: Regression `premium ~ VRAM` gave a negative coefficient — MSRP is a confounder**
- Initial model: `premium_pct ~ vram_gb` → VRAM coefficient was negative
- This is counterintuitive: more VRAM should mean higher premium, not lower
- Root cause: MSRP is a confounding variable. High-VRAM cards (e.g., RTX 3090, 24GB) have high MSRP ($1,499), leaving limited room for percentage premium. Low-VRAM cards (e.g., RTX 3060, 12GB) have low MSRP ($329) and can easily reach 200%+ premium
- Solution: Added MSRP as a control variable (`premium_pct ~ vram_gb + msrp_usd`). VRAM coefficient flipped from negative to positive. R² improved significantly

---

## Slide 18 — Answers to Research Questions
| Question | Answer |
|----------|--------|
| 1. Do crypto prices drive GPU prices? | Yes. ETH price leads GPU price by 1–2 months (CCF result). The secondary market does not react instantly |
| 2. What drives the premium? | VRAM (+): more memory → higher premium. LHR (−): significantly reduces premium. Hashrate (+): higher mining efficiency → higher premium. MSRP must be controlled to avoid confounding |
| 3. Was LHR effective? | Yes during the mining boom (20–37% price gap). Nearly zero effect after the crash (gap ~3%). LHR's effectiveness depends entirely on whether mining is profitable |
| 4. Which tier is most volatile? | XX60/XX70 (entry/mid-tier) show larger month-over-month % swings than XX80/XX90 (high-end) |
| 5. BTC or ETH? | ETH has stronger independent correlation with GPU prices. BTC's correlation is largely through its co-movement with ETH |

---

## Slide 19 — Limitations and Future Directions

**Limitations:**
- 10 GPU models, 24 months — limited sample size
- eBay is only one resale channel (not StockX, Facebook Marketplace, etc.)
- LHR prices use range midpoints — sources published price ranges, not exact averages
- Cannot control for all external factors: pandemic supply chain disruption, chip shortage, scalper speculation

**Future Directions:**
- Expand to RTX 40-series + 2023–2026 data to test if findings hold across GPU generations
- Incorporate on-chain metrics: network hash rate, active wallet counts, gas fees
- Multi-country comparison: US eBay vs European vs Asian second-hand platforms
- Replace CCF with VAR (Vector Autoregression) for more rigorous multi-variable time-series modeling
- LHR unlock events (2022) provide a natural experiment for difference-in-differences design

---

## Slide 20 — Acknowledgements and References

**Data Sources:**
- CoinGecko — Free cryptocurrency API
- Tom's Hardware — GPU Historical eBay Pricing series
- PCMag — eBay Terapeak analysis
- 3D Center — GPU price index
- TechSpot — LHR GPU reviews and pricing
- Michael Driscoll — RTX 30-series resale analysis

**Academic References:**
- Wilson, L. (2021). GPU Prices and Cryptocurrency Returns. *Applied Finance Letters*, 11(1).
- McMillan, T. (2022). The Impact of Bitcoin on Consumer GPU Prices. Princeton University.
- Nurfaizy, P. M. et al. (2022). NVIDIA GPU Price Prediction Using SVR. *Jurnal Ilmiah Wahana Pendidikan*, 8.
- Zięba, D. (2023). If GPU(time) == Money. *Int. Review of Economics & Finance*, 89.
- Demkowicz, J. et al. (2022). Quality of Cryptocurrency Mining on Previous Gen NVIDIA GTX GPUs. *WEBIST 2022*.

**Course:**
- COMP2501 — Teaching Team
