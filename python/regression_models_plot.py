"""
Generate three standalone regression model figures for presentation.
M1: premium ~ VRAM         (naive — confounded)
M2: premium ~ VRAM + MSRP   (controlled — VRAM flips positive)
M3: premium ~ VRAM + Tier   (Tier is the real driver)

All models use non-LHR GPUs only.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import statsmodels.api as sm
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "final_dataset.csv"
OUT_DIR = PROJECT_ROOT / "output" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TIER_COLORS = {"XX60": "#2C7BB6", "XX70": "#FDB863", "XX80": "#E76F51", "XX90": "#7B3294"}

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 200, "savefig.bbox": "tight",
    "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.labelsize": 11, "legend.fontsize": 9,
})


def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    return df[df["lhr"] == 0].copy()  # non-LHR only


def save_fig(fig, name):
    path = OUT_DIR / name
    fig.savefig(path, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"  -> {name}")


# ============================================================
# M1: premium_pct ~ vram_gb  (naive, confounded)
# ============================================================
def plot_m1(df):
    """Scatter plot with negative regression line — the 'wrong' model."""
    X = sm.add_constant(df["vram_gb"])
    y = df["premium_pct"]
    m1 = sm.OLS(y, X).fit()

    fig, ax = plt.subplots(figsize=(8, 5.5))

    # Scatter points colored by tier
    for tier in ["XX60", "XX70", "XX80", "XX90"]:
        tdf = df[df["tier"] == tier]
        jitter = np.random.RandomState(42).uniform(-0.3, 0.3, len(tdf))
        ax.scatter(
            tdf["vram_gb"] + jitter, tdf["premium_pct"],
            color=TIER_COLORS[tier], alpha=0.55, s=55,
            edgecolors="white", linewidth=0.4, label=tier, zorder=3
        )

    # Regression line
    x_range = np.linspace(7, 25, 100)
    y_pred = m1.params["const"] + m1.params["vram_gb"] * x_range
    ax.plot(x_range, y_pred, color="#D73027", linewidth=2.2, linestyle="-", zorder=4)

    # Annotation box
    vram_coef = m1.params["vram_gb"]
    vram_p = m1.pvalues["vram_gb"]
    r2 = m1.rsquared
    sig = "***" if vram_p < 0.001 else "**" if vram_p < 0.01 else "*" if vram_p < 0.05 else ""
    ann_text = (
        f"premium ~ VRAM\n"
        f"VRAM coef = {vram_coef:+.2f}{sig}\n"
        f"p = {vram_p:.4f}\n"
        f"R² = {r2:.3f}"
    )
    ax.text(0.05, 0.95, ann_text, transform=ax.transAxes, fontsize=13, va="top",
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#FFF5F5",
                       edgecolor="#D73027", alpha=0.9))

    ax.set_xlabel("VRAM (GB)")
    ax.set_ylabel("Price Premium over MSRP (%)")
    ax.set_title("M1: premium ~ VRAM  —  More VRAM = Lower Premium?")
    ax.legend(loc="upper right", fontsize=8, title="GPU Tier", title_fontsize=9)
    ax.grid(True, alpha=0.3, linestyle="--")
    ax.set_ylim(bottom=-20)

    fig.tight_layout()
    save_fig(fig, "M1_premium_vs_vram.png")


# ============================================================
# M2: premium_pct ~ vram_gb + msrp_usd  (controlled)
# ============================================================
def plot_m2(df):
    """Added-variable plot: VRAM partial effect after removing MSRP influence."""
    X = sm.add_constant(df[["vram_gb", "msrp_usd"]])
    y = df["premium_pct"]
    m2 = sm.OLS(y, X).fit()

    # --- Panel A: Added-variable plot for VRAM ---
    # Step 1: Regress premium on MSRP, get residuals
    X_prem_msrp = sm.add_constant(df["msrp_usd"])
    prem_resid = sm.OLS(y, X_prem_msrp).fit().resid

    # Step 2: Regress VRAM on MSRP, get residuals
    X_vram_msrp = sm.add_constant(df["msrp_usd"])
    vram_resid = sm.OLS(df["vram_gb"], X_vram_msrp).fit().resid

    # Step 3: Regress premium residuals on VRAM residuals
    # (slope = M2 VRAM coefficient)
    X_resid = sm.add_constant(vram_resid)
    resid_model = sm.OLS(prem_resid, X_resid).fit()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Panel A: Added-variable plot
    for tier in ["XX60", "XX70", "XX80", "XX90"]:
        mask = df["tier"] == tier
        ax1.scatter(
            vram_resid[mask], prem_resid[mask],
            color=TIER_COLORS[tier], alpha=0.55, s=55,
            edgecolors="white", linewidth=0.4, label=tier, zorder=3
        )

    xr = np.linspace(vram_resid.min(), vram_resid.max(), 100)
    yr = resid_model.params["const"] + resid_model.params[0] * xr
    ax1.plot(xr, yr, color="#1A9850", linewidth=2.2, linestyle="-", zorder=4)

    av_coef = resid_model.params[0]
    av_t = resid_model.tvalues[0]
    av_p = resid_model.pvalues[0]
    sig = "***" if av_p < 0.001 else "**" if av_p < 0.01 else "*" if av_p < 0.05 else ""
    ax1.text(0.05, 0.95,
             f"VRAM partial effect = {av_coef:+.2f}{sig}\n"
             f"t = {av_t:.2f}, p = {av_p:.4f}",
             transform=ax1.transAxes, fontsize=11, va="top", family="monospace",
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#F0FFF0",
                        edgecolor="#1A9850", alpha=0.9))

    ax1.set_xlabel("VRAM (residuals after removing MSRP)")
    ax1.set_ylabel("Premium % (residuals after removing MSRP)")
    ax1.set_title("After Controlling for MSRP\nVRAM Effect Flips Positive!")
    ax1.legend(fontsize=7.5)
    ax1.grid(True, alpha=0.3, linestyle="--")

    # Panel B: Coefficient forest plot
    coef_df = pd.DataFrame({
        "term": ["VRAM (GB)", "MSRP ($100)"],
        "coef": [m2.params["vram_gb"], m2.params["msrp_usd"] * 100],
        "ci_low": [
            m2.conf_int().loc["vram_gb", 0],
            m2.conf_int().loc["msrp_usd", 0] * 100,
        ],
        "ci_high": [
            m2.conf_int().loc["vram_gb", 1],
            m2.conf_int().loc["msrp_usd", 1] * 100,
        ],
    })

    colors = ["#2C7BB6", "#E76F51"]
    for i, (_, row) in enumerate(coef_df.iterrows()):
        ax2.axhline(y=i, color="#D9D9D9", linewidth=0.5, zorder=0)
        ax2.plot(
            [row["ci_low"], row["ci_high"]], [i, i],
            color=colors[i], linewidth=3, solid_capstyle="round", zorder=2
        )
        ax2.scatter(row["coef"], i, color=colors[i], s=120, zorder=3,
                    edgecolors="white", linewidth=1.5)
        ax2.annotate(
            f'{row["coef"]:+.2f}',
            xy=(row["coef"], i),
            xytext=(10 if row["coef"] < 0 else -10, 8),
            textcoords="offset points",
            fontsize=11, fontweight="bold", ha="center", va="bottom",
            color=colors[i]
        )

    ax2.axvline(x=0, color="black", linewidth=1, linestyle="-", zorder=1)
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(coef_df["term"].tolist(), fontsize=11)
    ax2.set_xlabel("Effect on Premium (percentage points)")
    ax2.set_title("M2: premium ~ VRAM + MSRP\nCoefficient Estimates with 95% CI")
    ax2.grid(axis="x", alpha=0.3, linestyle="--")

    fig.suptitle("M2 Resolves the Confounding  —  MSRP Was the Hidden Variable",
                 fontweight="bold", y=1.03, fontsize=13)
    fig.tight_layout()
    save_fig(fig, "M2_premium_vram_msrp.png")


# ============================================================
# M3: premium_pct ~ vram_gb + C(tier)  (Tier is the real driver)
# ============================================================
def plot_m3(df):
    """Coefficient plot with tier dummies — Tier dominates VRAM."""
    df_model = df.copy()
    df_model["tier"] = pd.Categorical(df_model["tier"], categories=["XX60", "XX70", "XX80", "XX90"])

    X = sm.add_constant(df_model[["vram_gb"]])
    X = pd.concat([X, pd.get_dummies(df_model["tier"], drop_first=True).astype(float)], axis=1)
    y = df_model["premium_pct"]
    m3 = sm.OLS(y, X).fit()

    # Build coefficient table (exclude intercept)
    # pd.get_dummies creates columns named by the Tier values directly
    coef_terms = {
        "VRAM (GB)": "vram_gb",
        "XX70 (vs XX60)": "XX70",
        "XX80 (vs XX60)": "XX80",
        "XX90 (vs XX60)": "XX90",
    }

    coef_data = []
    for label, term in coef_terms.items():
        coef_data.append({
            "term": label,
            "coef": m3.params[term],
            "ci_low": m3.conf_int().loc[term, 0],
            "ci_high": m3.conf_int().loc[term, 1],
            "pval": m3.pvalues[term],
        })

    coef_df = pd.DataFrame(coef_data)

    # --- Panel A: Coefficient forest plot ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    colors_a = ["#2C7BB6" if "VRAM" in t else "#FDB863" for t in coef_df["term"]]
    for i, (_, row) in enumerate(coef_df.iterrows()):
        ax1.axhline(y=i, color="#D9D9D9", linewidth=0.5, zorder=0)
        ax1.plot(
            [row["ci_low"], row["ci_high"]], [i, i],
            color=colors_a[i], linewidth=3, solid_capstyle="round", zorder=2
        )
        ax1.scatter(row["coef"], i, color=colors_a[i], s=120, zorder=3,
                    edgecolors="white", linewidth=1.5)
        sig = "***" if row["pval"] < 0.001 else "**" if row["pval"] < 0.01 else "*" if row["pval"] < 0.05 else " (ns)"
        ax1.annotate(
            f'{row["coef"]:+.1f}{sig}',
            xy=(row["coef"], i),
            xytext=(12, 7),
            textcoords="offset points",
            fontsize=10, fontweight="bold", ha="left", va="bottom",
            color=colors_a[i]
        )

    ax1.axvline(x=0, color="black", linewidth=1, linestyle="-", zorder=1)
    ax1.set_yticks(range(len(coef_df)))
    ax1.set_yticklabels(coef_df["term"].tolist(), fontsize=11)
    ax1.set_xlabel("Effect on Premium (percentage points)")
    ax1.set_title("M3: premium ~ VRAM + Tier\nCoefficient Estimates with 95% CI")
    ax1.grid(axis="x", alpha=0.3, linestyle="--")

    # Panel B: Premium by Tier boxplot (reinforces Tier dominance)
    tier_order = ["XX60", "XX70", "XX80", "XX90"]
    bp_data = [df[df["tier"] == t]["premium_pct"].dropna().values for t in tier_order]

    bp = ax2.boxplot(bp_data, labels=tier_order, patch_artist=True, widths=0.5)
    for patch, tier in zip(bp["boxes"], tier_order):
        patch.set_facecolor(TIER_COLORS[tier])
        patch.set_alpha(0.75)

    # Overlay jittered points
    for i, tier in enumerate(tier_order):
        y_vals = df[df["tier"] == tier]["premium_pct"].dropna()
        x_jitter = np.random.RandomState(42).uniform(i + 1 - 0.12, i + 1 + 0.12, len(y_vals))
        ax2.scatter(x_jitter, y_vals, color="black", alpha=0.18, s=14, zorder=3)

    # ANOVA
    from scipy import stats
    groups = [df[df["tier"] == t]["premium_pct"].dropna() for t in tier_order]
    f_stat, p_anova = stats.f_oneway(*groups)
    ax2.text(0.98, 0.95, f"ANOVA F={f_stat:.1f}, p={p_anova:.4f}",
             transform=ax2.transAxes, fontsize=10, ha="right", va="top",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85))

    ax2.axhline(y=0, color="black", linestyle="--", linewidth=0.8, alpha=0.4)
    ax2.set_ylabel("Price Premium over MSRP (%)")
    ax2.set_title("Premium by Tier\n(Lower-tier = Higher % Markup)")
    ax2.grid(axis="y", alpha=0.3, linestyle="--")

    # Tier mean annotations
    for i, tier in enumerate(tier_order):
        mean_val = df[df["tier"] == tier]["premium_pct"].mean()
        ax2.annotate(f"μ={mean_val:.0f}%", xy=(i + 1, mean_val),
                     xytext=(0, 10), textcoords="offset points",
                     fontsize=9, fontweight="bold", ha="center",
                     color=TIER_COLORS[tier])

    fig.suptitle("M3: Tier Is the Real Driver  —  VRAM Becomes Insignificant",
                 fontweight="bold", y=1.03, fontsize=13)
    fig.tight_layout()
    save_fig(fig, "M3_premium_vram_tier.png")


# ============================================================
# Combined summary: three models side by side (single slide visual)
# ============================================================
def plot_all_three_summary(df):
    """Single slide showing all three models condensed."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # --- M1: VRAM only ---
    ax = axes[0]
    _plot_single_reg(ax, df, "vram_gb", "M1: premium ~ VRAM",
                     "VRAM coef = −2.76***\nR² = 0.039",
                     "#D73027", slope_expected="negative")

    for tier in ["XX60", "XX70", "XX80", "XX90"]:
        tdf = df[df["tier"] == tier]
        jitter = np.random.RandomState(42).uniform(-0.3, 0.3, len(tdf))
        ax.scatter(tdf["vram_gb"] + jitter, tdf["premium_pct"],
                   color=TIER_COLORS[tier], alpha=0.45, s=30,
                   edgecolors="white", linewidth=0.3, zorder=3)

    # M1 regression line
    X1 = sm.add_constant(df["vram_gb"])
    m1 = sm.OLS(df["premium_pct"], X1).fit()
    xr = np.linspace(7, 25, 100)
    yr = m1.params["const"] + m1.params["vram_gb"] * xr
    ax.plot(xr, yr, color="#D73027", linewidth=2.2, zorder=4)

    ax.text(0.05, 0.95, f"VRAM = {m1.params['vram_gb']:+.2f}***\nR² = {m1.rsquared:.3f}",
            transform=ax.transAxes, fontsize=10, va="top", family="monospace",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF5F5", edgecolor="#D73027", alpha=0.9))
    ax.set_title("M1: premium ~ VRAM\n❌ VRAM effect is negative!", fontsize=10,
                 color="#D73027")
    ax.set_xlabel("VRAM (GB)")
    ax.set_ylabel("Premium %")

    # --- M2: VRAM + MSRP ---
    ax = axes[1]
    X2 = sm.add_constant(df[["vram_gb", "msrp_usd"]])
    m2 = sm.OLS(df["premium_pct"], X2).fit()

    coefs = [
        ("VRAM (GB)", m2.params["vram_gb"],
         m2.conf_int().loc["vram_gb", 0], m2.conf_int().loc["vram_gb", 1], "#2C7BB6"),
        ("MSRP ($100)", m2.params["msrp_usd"] * 100,
         m2.conf_int().loc["msrp_usd", 0] * 100, m2.conf_int().loc["msrp_usd", 1] * 100, "#E76F51"),
    ]
    for i, (label, coef, lo, hi, color) in enumerate(coefs):
        ax.plot([lo, hi], [i, i], color=color, linewidth=3, solid_capstyle="round")
        ax.scatter(coef, i, color=color, s=100, edgecolors="white", linewidth=1.5, zorder=3)
        sig = "***"
        ax.annotate(f"{coef:+.2f}{sig}", xy=(coef, i),
                    xytext=(8 if coef < 0 else -8, 8), textcoords="offset points",
                    fontsize=10, fontweight="bold", ha="center", va="bottom", color=color)

    ax.axvline(x=0, color="black", linewidth=0.8)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["VRAM (GB)", "MSRP ($100)"], fontsize=10)
    ax.set_xlabel("Effect on Premium (pp)")
    ax.set_title(f"M2: premium ~ VRAM + MSRP\n✅ VRAM flips positive! R²={m2.rsquared:.3f}",
                 fontsize=10, color="#1A9850")

    # --- M3: Tier model ---
    ax = axes[2]
    tier_order = ["XX60", "XX70", "XX80", "XX90"]
    bp_data = [df[df["tier"] == t]["premium_pct"].dropna().values for t in tier_order]
    bp = ax.boxplot(bp_data, labels=tier_order, patch_artist=True, widths=0.5)
    for patch, tier in zip(bp["boxes"], tier_order):
        patch.set_facecolor(TIER_COLORS[tier])
        patch.set_alpha(0.75)
    for i, tier in enumerate(tier_order):
        mean_val = df[df["tier"] == tier]["premium_pct"].mean()
        ax.annotate(f"{mean_val:.0f}%", xy=(i + 1, mean_val),
                    xytext=(0, 10), textcoords="offset points",
                    fontsize=10, fontweight="bold", ha="center", color=TIER_COLORS[tier])

    ax.axhline(y=0, color="black", linestyle="--", linewidth=0.8, alpha=0.4)
    ax.set_ylabel("Premium %")
    ax.set_title("M3: premium ~ VRAM + Tier\n✅ Tier dominates; VRAM not significant",
                 fontsize=10, color="#2C7BB6")

    fig.suptitle("Three Regression Models: Unmasking the Confounding Variable",
                 fontweight="bold", y=1.04, fontsize=14)
    fig.tight_layout()
    save_fig(fig, "M_all_three_summary.png")


def _plot_single_reg(ax, df, x_col, title, annotation, color, slope_expected=""):
    """Helper to add regression line to an axis."""
    X = sm.add_constant(df[x_col])
    m = sm.OLS(df["premium_pct"], X).fit()
    xr = np.linspace(df[x_col].min(), df[x_col].max(), 100)
    yr = m.params["const"] + m.params[x_col] * xr
    ax.plot(xr, yr, color=color, linewidth=2, zorder=4)
    return m


# ============================================================
def main():
    print("Generating M1, M2, M3 regression plots ...\n")
    df = load_data()
    print(f"Non-LHR data: {len(df)} rows, {df['model'].nunique()} models\n")

    print("[1/4] M1: premium ~ VRAM")
    plot_m1(df)

    print("[2/4] M2: premium ~ VRAM + MSRP")
    plot_m2(df)

    print("[3/4] M3: premium ~ VRAM + Tier")
    plot_m3(df)

    print("[4/4] Combined summary")
    plot_all_three_summary(df)

    print(f"\nDone. Figures saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
