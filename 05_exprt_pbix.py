import os
import sqlite3
import pandas as pd

# ── Path Configuration ───────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH     = os.path.join(BASE_DIR, "db", "GS_Analysis.db")
EXPORT_DIR  = os.path.join(BASE_DIR, "powerbi_exports")

os.makedirs(EXPORT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

# ── Export Queries ────────────────────────────────────────────────────────────
exports = {
    "PowerBI_DailyPrices.csv": "SELECT * FROM daily_prices",

    "PowerBI_AnnualSummary.csv": "SELECT * FROM annual_summary",

    "PowerBI_Events.csv": "SELECT * FROM geopolitical_events",

    "PowerBI_MonthlyAvg.csv": """
        SELECT
            month,
            ROUND(AVG(gold_price),              2) AS avg_gold_price,
            ROUND(AVG(silver_price),            2) AS avg_silver_price,
            ROUND(AVG(gprd),                    2) AS avg_gprd,
            ROUND(AVG(gold_change_percent), 4) AS avg_gold_change_percent
        FROM daily_prices
        GROUP BY month
        ORDER BY month
    """,

    "PowerBI_DecadeSummary.csv": """
        SELECT
            decade,
            ROUND(AVG(gold_price),   2) AS avg_gold,
            ROUND(AVG(silver_price), 2) AS avg_silver,
            ROUND(AVG(gprd),         2) AS avg_gprd,
            COUNT(*) AS trading_days
        FROM daily_prices
        GROUP BY decade
        ORDER BY decade
    """
}

for filename, query in exports.items():
    df = pd.read_sql_query(query, conn)
    out_path = os.path.join(EXPORT_DIR, filename)
    df.to_csv(out_path, index=False)
    print(f"Exported {filename} ({len(df)} rows)")

conn.close()
print("\nAll Power BI export files saved to powerbi_exports/")
