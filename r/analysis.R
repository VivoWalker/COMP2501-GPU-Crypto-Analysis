###############################################################################
#                                                                             #
#   Statistical Analysis & Visualization for                                  #
#   "Analysis of NVIDIA GPU Market Dynamics and Cryptocurrency Correlations"  #
#                                                                             #
#   Dependencies: tidyverse, scales, showtext, corrplot, broom, here          #
#                                                                             #
###############################################################################

# ---- Package management ----------------------------------------------------
required_packages <- c(
  "tidyverse", "scales", "showtext", "corrplot", "broom", "here"
)

for (pkg in required_packages) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cran.r-project.org")
  }
  library(pkg, character.only = TRUE)
}

# ---- Typography setup (Google Fonts, with offline fallback) ----------------
showtext_auto()

font_ok <- function(family) family %in% sysfonts::font_families()

tryCatch({
  font_add_google("Inter", family = "inter")
  font_add_google("Fira Code", family = "fira")
  base_font <- "inter"
}, error = function(e) {
  packageStartupMessage("Google Fonts unavailable — using system sans font")
  base_font <<- "sans"
})

# ---- Global ggplot2 theme --------------------------------------------------
theme_presentation <- theme_minimal(base_family = base_font) +
  theme(
    plot.title        = element_text(face = "bold", size = 14, margin = margin(b = 8)),
    plot.subtitle     = element_text(size = 10, colour = "grey40", margin = margin(b = 12)),
    plot.caption      = element_text(size = 8, colour = "grey60", hjust = 0),
    axis.title        = element_text(size = 10),
    axis.text         = element_text(size = 9),
    legend.position   = "bottom",
    legend.title      = element_text(size = 9),
    legend.text       = element_text(size = 8),
    panel.grid.minor  = element_blank(),
    panel.grid.major  = element_line(colour = "grey90", linewidth = 0.3),
    plot.margin       = margin(16, 16, 16, 16),
  )

# ---- Colour palette --------------------------------------------------------
pal_tier <- c(
  "XX60" = "#2C7BB6",
  "XX70" = "#FDB863",
  "XX80" = "#E76F51",
  "XX90" = "#7B3294"
)

# ---- Data I/O --------------------------------------------------------------
cat("Loading data …\n")
df <- read_csv(
  here("data", "processed", "final_dataset.csv"),
  show_col_types = FALSE
) %>%
  mutate(
    date    = as.Date(date),
    tier    = factor(tier, levels = c("XX60", "XX70", "XX80", "XX90")),
    lhr     = factor(lhr, levels = c(0, 1), labels = c("Non-LHR", "LHR"))
  )

cat(sprintf("  %d rows | %d unique models | date range: %s → %s\n",
            nrow(df), n_distinct(df$model), min(df$date), max(df$date)))

# ---- Output directory ------------------------------------------------------
out_dir <- here("output", "figures")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

# ===========================================================================
# 1. DUAL-AXIS TIME SERIES: ETH price vs GPU street prices (by tier)
# ===========================================================================
cat("\n[1/6] Dual-axis time series plot …\n")

tier_monthly <- df %>%
  group_by(date, tier) %>%
  summarise(gpu_median = median(street_price_usd, na.rm = TRUE), .groups = "drop")

eth_monthly <- df %>%
  distinct(date, eth_avg) %>%
  arrange(date)

# Dual-axis scale: map ETH price range to GPU price range
gpu_max <- max(tier_monthly$gpu_median, na.rm = TRUE)
eth_max <- max(eth_monthly$eth_avg, na.rm = TRUE)
scale_factor <- ifelse(eth_max > 0 & gpu_max > 0, gpu_max / eth_max, 1)

p1 <- ggplot() +
  geom_line(
    data = eth_monthly,
    aes(x = date, y = eth_avg / scale_factor, colour = "ETH Price"),
    linewidth = 0.6, alpha = 0.7
  ) +
  geom_line(
    data = tier_monthly,
    aes(x = date, y = gpu_median, colour = tier, group = tier),
    linewidth = 0.8
  ) +
  scale_y_continuous(
    name   = "GPU Street Price (USD)",
    labels = dollar_format(),
    sec.axis = sec_axis(~ . * scale_factor, name = "ETH Price (USD)",
                        labels = dollar_format())
  ) +
  scale_colour_manual(
    name   = "",
    values = c(pal_tier, "ETH Price" = "#333333")
  ) +
  labs(
    title    = "GPU eBay Prices vs. Ethereum Price (2020/09 – 2022/09)",
    subtitle = "Monthly median eBay sold price by tier, overlaid with ETH/USD",
    caption  = "Sources: CoinGecko (ETH); Tom's Hardware / PCMag / 3D Center (GPU eBay prices)",
    x = NULL
  ) +
  theme_presentation

ggsave(
  file.path(out_dir, "01_dual_axis_timeseries.png"),
  p1, width = 10, height = 5.5, dpi = 200
)
cat("  → 01_dual_axis_timeseries.png\n")

# ===========================================================================
# 2. CROSS-CORRELATION (CCF): ETH price vs GPU price lag
# ===========================================================================
cat("[2/6] Cross-correlation analysis …\n")

# Build aligned monthly series for RTX 3080 (flagship mining card)
ccf_data <- df %>%
  filter(model == "RTX 3080") %>%
  select(date, street_price_usd) %>%
  inner_join(eth_monthly, by = "date") %>%
  arrange(date)

if (nrow(ccf_data) < 6) {
  cat("  WARNING: < 6 months of data for CCF — skipping\n")
} else {
  gpu_3080 <- ccf_data$street_price_usd
  eth_series <- ccf_data$eth_avg

  # Save CCF plot
  png(
    file.path(out_dir, "02_ccf_eth_gpu3080.png"),
    width = 2000, height = 1400, res = 200
  )
  par(family = "sans")
  ccf(eth_series, gpu_3080, lag.max = min(12, floor(length(gpu_3080) / 3)),
      main = "Cross-Correlation: ETH Price vs RTX 3080 eBay Price",
      xlab = "Lag (months) — negative = ETH leads GPU",
      ylab = "Cross-correlation",
      ci.col = "#E76F51", lwd = 2)
  abline(v = 0, lty = 2, col = "grey60")
  dev.off()
  cat("  → 02_ccf_eth_gpu3080.png\n")

  # Multi-model CCF summary
  ccf_summary <- map_dfr(unique(df$model), function(m) {
    ccf_m <- df %>%
      filter(model == m) %>%
      select(date, street_price_usd) %>%
      inner_join(eth_monthly, by = "date") %>%
      arrange(date)
    if (nrow(ccf_m) < 6) return(tibble(model = m, best_lag_months = NA_real_, ccf_value = NA_real_))
    n <- nrow(ccf_m)
    cc <- ccf(ccf_m$eth_avg, ccf_m$street_price_usd,
              lag.max = min(12, floor(n / 3)),
              plot = FALSE, na.action = na.omit)
    peak_lag <- cc$lag[which.max(cc$acf)]
    peak_val <- max(cc$acf, na.rm = TRUE)
    tibble(model = m, best_lag_months = peak_lag, ccf_value = round(peak_val, 3))
  })

  cat("  CCF peak lags by model (negative = crypto leads GPU):\n")
  print(ccf_summary, n = Inf)
}

# ===========================================================================
# 3. REGRESSION: price premium ~ VRAM + LHR + hashrate
# ===========================================================================
cat("\n[3/6] Regression analysis …\n")

model_lm <- lm(premium_pct ~ vram_gb + lhr + eth_hashrate_mh, data = df)
cat("  Model: premium_pct ~ vram_gb + lhr + eth_hashrate_mh\n\n")
print(summary(model_lm))

# Export regression table (with error-safe sink)
reg_path <- file.path(out_dir, "03_regression_summary.txt")
sink(reg_path)
cat("OLS Regression: GPU Price Premium vs. Specifications\n")
cat("====================================================\n")
cat("Period: 2020/09 – 2022/09\n")
cat("Data: Tom's Hardware / PCMag / 3D Center eBay prices\n\n")
print(summary(model_lm))
cat("\nNote: 'lhrLHR' is a dummy = 1 for LHR variants, 0 for non-LHR.\n")
sink()
cat("  → 03_regression_summary.txt\n")

# ---- Coefficient plot -----------------------------------------------------
coef_df <- broom::tidy(model_lm, conf.int = TRUE) %>%
  filter(term != "(Intercept)") %>%
  mutate(
    term = recode(term,
      vram_gb         = "VRAM (GB)",
      lhrLHR          = "LHR Status",
      eth_hashrate_mh = "ETH Hashrate (MH/s)"
    )
  )

p3 <- ggplot(coef_df, aes(x = estimate, y = reorder(term, estimate))) +
  geom_vline(xintercept = 0, linetype = "dashed", colour = "grey60") +
  geom_pointrange(
    aes(xmin = conf.low, xmax = conf.high),
    size = 1, colour = "#2C7BB6"
  ) +
  labs(
    title    = "Drivers of GPU Price Premium over MSRP",
    subtitle = "OLS coefficient estimates with 95% confidence intervals",
    x        = "Effect on premium (percentage points)",
    y        = NULL,
    caption  = "LHR = Lite Hash Rate variant indicator"
  ) +
  theme_presentation

ggsave(
  file.path(out_dir, "03_regression_coefficients.png"),
  p3, width = 8, height = 3.5, dpi = 200
)
cat("  → 03_regression_coefficients.png\n")

# ===========================================================================
# 4. BOXPLOT: Price volatility by GPU tier
# ===========================================================================
cat("[4/6] Volatility boxplots by tier …\n")

volatility_df <- df %>%
  group_by(model, tier) %>%
  arrange(date, .by_group = TRUE) %>%
  mutate(
    pct_change = (street_price_usd / lag(street_price_usd) - 1) * 100
  ) %>%
  filter(!is.na(pct_change)) %>%
  ungroup()

p4 <- ggplot(volatility_df, aes(x = tier, y = pct_change, fill = tier)) +
  geom_boxplot(outlier.size = 0.6, outlier.alpha = 0.4, width = 0.6) +
  geom_hline(yintercept = 0, linetype = "dotted", colour = "grey50") +
  scale_fill_manual(values = pal_tier, guide = "none") +
  scale_y_continuous(labels = scales::percent_format(scale = 1)) +
  labs(
    title    = "Monthly Price Volatility by GPU Tier",
    subtitle = "Distribution of month-over-month % eBay price changes (2020/09 – 2022/09)",
    x        = NULL,
    y        = "Month-over-month price change (%)",
    caption  = "Source: Tom's Hardware / PCMag / 3D Center eBay GPU Price Index"
  ) +
  theme_presentation

ggsave(
  file.path(out_dir, "04_volatility_boxplot.png"),
  p4, width = 8, height = 5.5, dpi = 200
)
cat("  → 04_volatility_boxplot.png\n")

# ===========================================================================
# 5. CORRELATION HEATMAP
# ===========================================================================
cat("[5/6] Correlation heatmap …\n")

cor_data <- df %>%
  select(
    street_price_usd, premium_pct, eth_avg, btc_avg,
    vram_gb, lhr, eth_hashrate_mh, price_per_mh,
    eth_std, btc_std
  ) %>%
  mutate(lhr = if_else(lhr == "LHR", 1, 0)) %>%
  cor(use = "complete.obs")

png(
  file.path(out_dir, "05_correlation_heatmap.png"),
  width = 2000, height = 1800, res = 200
)
corrplot(
  cor_data,
  method      = "color",
  type        = "lower",
  addCoef.col = "grey30",
  number.cex  = 0.65,
  tl.col      = "grey20",
  tl.cex      = 0.8,
  col         = colorRampPalette(c("#D73027", "#FFFFBF", "#1A9850"))(100),
  mar         = c(0, 0, 3, 0),
  title       = "Correlation Matrix: GPU & Crypto Variables",
  diag        = FALSE
)
dev.off()
cat("  → 05_correlation_heatmap.png\n")

# ===========================================================================
# 6. LHR IMPACT: Premium comparison during peak vs. trough
# ===========================================================================
cat("[6/6] LHR impact analysis …\n")

peak_month   <- eth_monthly$date[which.max(eth_monthly$eth_avg)]
trough_month <- eth_monthly$date[which.min(eth_monthly$eth_avg)]

peak_label   <- format(peak_month,   "ETH Peak (%b %Y)")
trough_label <- format(trough_month, "ETH Trough (%b %Y)")

lhr_compare <- df %>%
  filter(date %in% c(peak_month, trough_month)) %>%
  mutate(period = if_else(date == peak_month, peak_label, trough_label)) %>%
  group_by(period, lhr) %>%
  summarise(
    avg_premium = mean(premium_pct, na.rm = TRUE),
    se_premium  = sd(premium_pct, na.rm = TRUE) / sqrt(n()),
    .groups     = "drop"
  )

p6 <- ggplot(lhr_compare, aes(x = lhr, y = avg_premium, fill = lhr)) +
  geom_col(width = 0.5) +
  geom_errorbar(
    aes(ymin = avg_premium - se_premium, ymax = avg_premium + se_premium),
    width = 0.1
  ) +
  facet_wrap(~ period, scales = "free_y") +
  scale_fill_manual(values = c("Non-LHR" = "#2C7BB6", "LHR" = "#FDB863"), guide = "none") +
  labs(
    title    = "LHR Impact on GPU Price Premium",
    subtitle = sprintf("Comparing crypto peak (%s) vs. trough (%s)",
                       format(peak_month, "%b %Y"), format(trough_month, "%b %Y")),
    x        = NULL,
    y        = "Average premium over MSRP (%)",
    caption  = "Source: Tom's Hardware / PCMag / 3D Center. LHR cards show a smaller premium during crypto booms."
  ) +
  theme_presentation

ggsave(
  file.path(out_dir, "06_lhr_premium_comparison.png"),
  p6, width = 8, height = 5, dpi = 200
)
cat("  → 06_lhr_premium_comparison.png\n")

# ===========================================================================
# Done
# ===========================================================================
cat(sprintf("\nAll figures saved to %s\n", out_dir))
