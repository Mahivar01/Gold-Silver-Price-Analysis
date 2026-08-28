import os
import pandas as pd

# ── Path Configuration ───────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT_DIR = os.path.join(BASE_DIR, "powerbi_exports")

os.makedirs(EXPORT_DIR, exist_ok=True)

# ── Load the Power BI Annual Summary (produced by script 05) ─────────────────
# This script must run AFTER 05_exprt_pbix.py, since it adds columns to that
# file rather than rebuilding it from a different source. Keeping a single
# source of truth avoids column-naming drift between the DB export and this
# script's output.
export_path = os.path.join(EXPORT_DIR, "PowerBI_AnnualSummary.csv")

if not os.path.exists(export_path):
    raise FileNotFoundError(
        f"{export_path} not found. Run scripts/05_exprt_pbix.py before this script."
    )

annual = pd.read_csv(export_path)
annual = annual.sort_values("year").reset_index(drop=True)

# ── Calculate YoY Returns ─────────────────────────────────────────────────────
annual["gold_yoy_return_percent"] = (
    (annual["avg_gold_price"] - annual["avg_gold_price"].shift(1))
    / annual["avg_gold_price"].shift(1)
) * 100

annual["silver_yoy_return_percent"] = (
    (annual["avg_silver_price"] - annual["avg_silver_price"].shift(1))
    / annual["avg_silver_price"].shift(1)
) * 100

annual["gold_yoy_return_percent"]   = annual["gold_yoy_return_percent"].round(2)
annual["silver_yoy_return_percent"] = annual["silver_yoy_return_percent"].round(2)

# ── Save back to the same Power BI export ─────────────────────────────────────
annual.to_csv(export_path, index=False)

print("PowerBI_AnnualSummary.csv updated with YoY return columns.")
print(annual[["year", "gold_yoy_return_percent", "silver_yoy_return_percent"]].to_string(index=False))
