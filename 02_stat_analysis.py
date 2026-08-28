import os
import pandas as pd
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

# ── Path Configuration ───────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

# ── Load Cleaned Data ────────────────────────────────────────────────────────
df = pd.read_csv(os.path.join(DATA_DIR, "Gold_Silver_cleaned.csv"), parse_dates=["DATE"])

# ── 1. Pearson Correlation: GPRD vs Gold Price ────────────────────────────────
r, p = stats.pearsonr(df["GPRD"].dropna(), df.loc[df["GPRD"].notna(), "GOLD_PRICE"])
print(f"GPRD <-> Gold Pearson r = {r:.4f}, p-value = {p:.4e}")

# ── 2. T-Test: High vs Low Risk Daily Gold Returns ───────────────────────────
median_gprd = df["GPRD"].median()
high_risk = df[df["GPRD"] > median_gprd]["GOLD_CHANGE_%"].dropna()
low_risk  = df[df["GPRD"] <= median_gprd]["GOLD_CHANGE_%"].dropna()

t_stat, p_value = stats.ttest_ind(high_risk, low_risk)
print(f"\nHigh-risk average daily gold change : {high_risk.mean():.4f}%")
print(f"Low-risk  average daily gold change : {low_risk.mean():.4f}%")
print(f"T-test: t={t_stat:.3f}, p-value={p_value:.4e}")

# ── 3. Event Window Analysis: 30-Day Gold Change After Each Event ─────────────
event_dates = df[df["HAS_EVENT"] == 1]["DATE"]
windows = []

for ed in event_dates:
    window = df[(df["DATE"] >= ed) & (df["DATE"] <= ed + pd.Timedelta(days=30))]["GOLD_PRICE"]
    if len(window) > 2:
        pct_change = (window.iloc[-1] - window.iloc[0]) / window.iloc[0] * 100
        windows.append({"EVENT_DATE": ed, "30D_GOLD_CHANGE_%": pct_change})

event_impact = pd.DataFrame(windows)
print(f"\nAverage gold change in 30 days after a geopolitical event: "
      f"{event_impact['30D_GOLD_CHANGE_%'].mean():.2f}%")
print(event_impact.sort_values("30D_GOLD_CHANGE_%", ascending=False))

# ── 4. Annual Return Calculation ─────────────────────────────────────────────
annual = df.groupby("YEAR").agg(
    GOLD_START   = ("GOLD_PRICE",   "first"),
    GOLD_END     = ("GOLD_PRICE",   "last"),
    SILVER_START = ("SILVER_PRICE", "first"),
    SILVER_END   = ("SILVER_PRICE", "last"),
    AVG_GPRD     = ("GPRD",         "mean"),
    avg_gold_price   = ("GOLD_PRICE",   "mean"),
    avg_silver_price = ("SILVER_PRICE", "mean"),
).reset_index()

annual["GOLD_ANNUAL_RETURN_%"]   = (annual["GOLD_END"]   - annual["GOLD_START"])   / annual["GOLD_START"]   * 100
annual["SILVER_ANNUAL_RETURN_%"] = (annual["SILVER_END"] - annual["SILVER_START"]) / annual["SILVER_START"] * 100

print("\nAnnual returns — last 10 years:")
print(annual.tail(10)[["YEAR", "GOLD_ANNUAL_RETURN_%", "SILVER_ANNUAL_RETURN_%", "AVG_GPRD"]].to_string(index=False))

# ── Save Outputs ─────────────────────────────────────────────────────────────
annual.to_csv(os.path.join(DATA_DIR, "Annual_Analysis.csv"), index=False)
event_impact.to_csv(os.path.join(DATA_DIR, "Event_Analysis.csv"), index=False)
print("\nStatistical outputs saved.")
