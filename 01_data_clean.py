import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ── Path Configuration ───
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(BASE_DIR, "data")
CHART_DIR = os.path.join(BASE_DIR, "charts")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)

# ── Data Loading and Inspection ───
df = pd.read_csv(os.path.join(DATA_DIR, "Gold-Silver-GeopoliticalRisk_HistoricalData.csv"))
print(df.shape)
print(df.dtypes)
print(df.isnull().sum())

# ── Cleaning ───
df["DATE"] = pd.to_datetime(df["DATE"])
df.sort_values("DATE", inplace=True)
df.reset_index(drop=True, inplace=True)

# Forward-fill 7 missing silver rows (market holiday carry)
silver_cols = ["SILVER_PRICE", "SILVER_OPEN", "SILVER_HIGH", "SILVER_LOW", "SILVER_CHANGE_%"]
df[silver_cols] = df[silver_cols].ffill()

# Linearly interpolate 2 missing GPRD values
gprd_cols = ["GPRD", "GPRD_ACT", "GPRD_THREAT"]
df[gprd_cols] = df[gprd_cols].interpolate(method="linear")

# Event flagging
df["HAS_EVENT"] = df["EVENT"].notna().astype(int)

# ── Feature Engineering ───
df["GOLD_SILVER_RATIO"]   = df["GOLD_PRICE"] / df["SILVER_PRICE"]
df["GOLD_VOLATILITY_30"]  = df["GOLD_PRICE"].pct_change().rolling(30).std() * np.sqrt(252)
df["SILVER_VOLATILITY_30"]= df["SILVER_PRICE"].pct_change().rolling(30).std() * np.sqrt(252)
df["GOLD_SMA_50"]         = df["GOLD_PRICE"].rolling(50).mean()
df["GOLD_SMA_200"]        = df["GOLD_PRICE"].rolling(200).mean()
df["GPRD_ROLLING_30"]     = df["GPRD"].rolling(30).mean()
df["YEAR"]                = df["DATE"].dt.year
df["MONTH"]               = df["DATE"].dt.month
df["DECADE"]              = (df["YEAR"] // 10) * 10

print(df.tail())
df.to_csv(os.path.join(DATA_DIR, "Gold_Silver_cleaned.csv"), index=False)
print("Clean CSV saved.")

# ── EDA Visualisations ──
plt.style.use("seaborn-v0_8-darkgrid")

# 1. Price History
fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
axes[0].plot(df["DATE"], df["GOLD_PRICE"], color="#FFD700", lw=1)
axes[0].set_title("Gold Prices from 1985–2025", fontsize=13)
axes[0].set_ylabel("USD/oz")
axes[1].plot(df["DATE"], df["SILVER_PRICE"], color="#C0C0C0", lw=1)
axes[1].set_title("Silver Prices from 1985–2025", fontsize=13)
axes[1].set_ylabel("USD/oz")
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "Price_History.png"), dpi=150)
plt.show()

# 2. GPRD vs Gold with event markers
fig, ax1 = plt.subplots(figsize=(14, 5))
ax2 = ax1.twinx()
ax1.plot(df["DATE"], df["GOLD_PRICE"], color="#FFD700", lw=1, label="Gold Price")
ax2.plot(df["DATE"], df["GPRD"], color="#E74C3C", lw=0.7, alpha=0.6, label="GPRD")
events = df[df["HAS_EVENT"] == 1]
for _, row in events.iterrows():
    ax1.axvline(row["DATE"], color="red", alpha=0.3, lw=0.5)
ax1.set_ylabel("Gold Price (USD)", color="#B8860B")
ax2.set_ylabel("Geopolitical Risk Index", color="#E74C3C")
ax1.set_title("Gold Price vs Geopolitical Risk Index with Major World Events")
fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9))
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "GPRD_vs_Gold.png"), dpi=150)
plt.show()

# 3. Gold-Silver Ratio
plt.figure(figsize=(14, 4))
plt.plot(df["DATE"], df["GOLD_SILVER_RATIO"], color="purple", lw=1)
plt.axhline(df["GOLD_SILVER_RATIO"].mean(), color="orange", ls="--",
            label=f"Mean: {df['GOLD_SILVER_RATIO'].mean():.1f}")
plt.title("Gold-Silver Ratio from 1985–2025")
plt.ylabel("Ratio")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "GOLD_SILVER_RATIO.png"), dpi=150)
plt.show()

# 4. Correlation Heatmap
corr_cols = ["GOLD_PRICE", "SILVER_PRICE", "GPRD", "GPRD_ACT", "GPRD_THREAT",
             "GOLD_CHANGE_%", "SILVER_CHANGE_%", "GOLD_SILVER_RATIO"]
corr = df[corr_cols].corr()
plt.figure(figsize=(9, 7))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlGn", center=0,
            linewidths=0.5, annot_kws={"size": 9})
plt.title("Correlation Matrix")
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "corr_matrix.png"), dpi=150)
plt.show()

# 5. 30-Day Rolling Volatility
plt.figure(figsize=(14, 4))
plt.plot(df["DATE"], df["GOLD_VOLATILITY_30"] * 100, label="Gold Vol", color="#FFD700")
plt.plot(df["DATE"], df["SILVER_VOLATILITY_30"] * 100, label="Silver Vol", color="#C0C0C0", alpha=0.7)
plt.title("30-Day Rolling Annualised Volatility (%)")
plt.ylabel("%")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "Volatility.png"), dpi=150)
plt.show()

# 6. Average Gold Price by Decade
decade_avg = df.groupby("DECADE")["GOLD_PRICE"].mean().reset_index()
plt.figure(figsize=(9, 5))
plt.bar(decade_avg["DECADE"].astype(str), decade_avg["GOLD_PRICE"],
        color="#FFD700", edgecolor="black")
plt.title("Average Gold Price by Decade")
plt.ylabel("USD/oz")
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "Average_Gold_Price_ByDecade.png"), dpi=150)
plt.show()

print("All EDA plots saved.")
