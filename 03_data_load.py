import os
import pandas as pd
import sqlite3

# ── Path Configuration ───────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR   = os.path.join(BASE_DIR, "db")

os.makedirs(DB_DIR, exist_ok=True)

# ── Connect and Create Schema ────────────────────────────────────────────────
conn = sqlite3.connect(os.path.join(DB_DIR, "GS_Analysis.db"))
cur  = conn.cursor()

cur.executescript("""
DROP TABLE IF EXISTS daily_prices;
DROP TABLE IF EXISTS geopolitical_events;
DROP TABLE IF EXISTS annual_summary;

CREATE TABLE daily_prices (
    date                    TEXT PRIMARY KEY,
    gold_price              REAL,
    gold_open               REAL,
    gold_high               REAL,
    gold_low                REAL,
    gold_change_percent     REAL,
    silver_price            REAL,
    silver_open             REAL,
    silver_high             REAL,
    silver_low              REAL,
    silver_change_percent   REAL,
    gprd                    REAL,
    gprd_act                REAL,
    gprd_threat             REAL,
    has_event               INTEGER,
    gold_silver_ratio       REAL,
    gold_volatility_30      REAL,
    gold_sma_50             REAL,
    gold_sma_200            REAL,
    year                    INTEGER,
    month                   INTEGER,
    decade                  INTEGER
);

CREATE TABLE geopolitical_events (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    date         TEXT,
    event_name   TEXT,
    gprd         REAL,
    gprd_act     REAL,
    gprd_threat  REAL,
    gold_price   REAL,
    silver_price REAL
);

CREATE TABLE annual_summary (
    year                        INTEGER PRIMARY KEY,
    gold_annual_return_percent  REAL,
    silver_annual_return_percent REAL,
    avg_gprd                    REAL,
    avg_gold_price              REAL,
    avg_silver_price            REAL
);
""")

# ── Load daily_prices ────────────────────────────────────────────────────────
df = pd.read_csv(os.path.join(DATA_DIR, "Gold_Silver_cleaned.csv"), parse_dates=["DATE"])

df_db = df[[
    "DATE", "GOLD_PRICE", "GOLD_OPEN", "GOLD_HIGH", "GOLD_LOW", "GOLD_CHANGE_%",
    "SILVER_PRICE", "SILVER_OPEN", "SILVER_HIGH", "SILVER_LOW", "SILVER_CHANGE_%",
    "GPRD", "GPRD_ACT", "GPRD_THREAT", "HAS_EVENT", "GOLD_SILVER_RATIO",
    "GOLD_VOLATILITY_30", "GOLD_SMA_50", "GOLD_SMA_200", "YEAR", "MONTH", "DECADE"
]].copy()

df_db.columns = [c.lower().replace("%", "percent").replace("-", "_") for c in df_db.columns]
df_db["date"] = df_db["date"].astype(str)
df_db.to_sql("daily_prices", conn, if_exists="append", index=False)
print(f"Loaded {len(df_db)} rows -> daily_prices")

# ── Load geopolitical_events ─────────────────────────────────────────────────
events = df[df["HAS_EVENT"] == 1][
    ["DATE", "EVENT", "GPRD", "GPRD_ACT", "GPRD_THREAT", "GOLD_PRICE", "SILVER_PRICE"]
].copy()
events.columns = ["date", "event_name", "gprd", "gprd_act", "gprd_threat", "gold_price", "silver_price"]
events["date"] = events["date"].astype(str)
events.to_sql("geopolitical_events", conn, if_exists="append", index=False)
print(f"Loaded {len(events)} rows -> geopolitical_events")

# ── Load annual_summary ──────────────────────────────────────────────────────
ann = pd.read_csv(os.path.join(DATA_DIR, "Annual_Analysis.csv"))
ann_db = ann[["YEAR", "GOLD_ANNUAL_RETURN_%", "SILVER_ANNUAL_RETURN_%", "AVG_GPRD",
              "avg_gold_price", "avg_silver_price"]].copy()
ann_db.columns = ["year", "gold_annual_return_percent", "silver_annual_return_percent",
                  "avg_gprd", "avg_gold_price", "avg_silver_price"]
ann_db.to_sql("annual_summary", conn, if_exists="append", index=False)
print(f"Loaded {len(ann_db)} rows -> annual_summary")

conn.commit()
conn.close()
print("\nDatabase loaded into SQLite successfully.")
