"""
GPU Specifications Data
========================
Defines a canonical table of NVIDIA GeForce GPU specifications relevant
to mining economics: VRAM size, LHR status, release date, and estimated
hashrate (MH/s for ETH/ETC).

Data sources:
  - NVIDIA official specs (VRAM, MSRP)
  - TechPowerUp GPU database (hashrate benchmarks)
  - NVIDIA blog (LHR announcement May 2021)

Output: data/raw/gpu_specs.csv
"""

import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / "gpu_specs.csv"

# ---------------------------------------------------------------------------
# GPU spec table
# ---------------------------------------------------------------------------
# Key GPUs active during the 2020/09 – 2022/09 mining boom.
#
# LHR (Lite Hash Rate) variants were introduced starting May 2021.
# They halved ETH hashrate but were otherwise identical to non-LHR.
# ---------------------------------------------------------------------------
GPU_SPECS = [
    # RTX 30-series (Ampere) — the mining-boom generation
    ("RTX 3060",       "XX60", 12, 0, "2021-02-25",  48,  329, "Ampere"),
    ("RTX 3060 LHR",   "XX60", 12, 1, "2021-05-19",  26,  329, "Ampere"),
    ("RTX 3060 Ti",    "XX60",  8, 0, "2020-12-02",  60,  399, "Ampere"),
    ("RTX 3070",       "XX70",  8, 0, "2020-10-29",  62,  499, "Ampere"),
    ("RTX 3070 LHR",   "XX70",  8, 1, "2021-05-19",  34,  499, "Ampere"),
    ("RTX 3070 Ti",    "XX70",  8, 0, "2021-06-10",  55,  599, "Ampere"),
    ("RTX 3080",       "XX80", 10, 0, "2020-09-17",  98,  699, "Ampere"),
    ("RTX 3080 LHR",   "XX80", 10, 1, "2021-05-19",  55,  699, "Ampere"),
    ("RTX 3080 Ti",    "XX80", 12, 0, "2021-06-03",  80, 1199, "Ampere"),
    ("RTX 3090",       "XX90", 24, 0, "2020-09-24", 120, 1499, "Ampere"),
]

COLS = [
    "model", "tier", "vram_gb", "lhr", "release_date",
    "eth_hashrate_mh", "msrp_usd", "architecture",
]

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("GPU Specifications Data\n" + "=" * 40)
    df = pd.DataFrame(GPU_SPECS, columns=COLS)
    df["release_date"] = pd.to_datetime(df["release_date"])
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df)} GPU entries → {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
