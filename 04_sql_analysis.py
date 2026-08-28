import os
import sqlite3
import pandas as pd

# ── Path Configuration ───────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "db", "GS_Analysis.db")

conn = sqlite3.connect(DB_PATH)

def run(label, query):
    df = pd.read_sql_query(query, conn)
    print(f"\n{'-'*60}")
    print(f"    {label}")
    print(f"{'-'*60}")
    print(df.to_string(index=False))
    return df

# ── Query 1: Top 10 Highest GPRD Days ────────────────────────────────────────
run("Top 10 Highest GPRD Days", """
    SELECT date, gprd, gprd_act, gprd_threat, gold_price
    FROM daily_prices
    ORDER BY gprd DESC
    LIMIT 10
""")

# ── Query 2: High vs Low Risk Periods ────────────────────────────────────────
run("High vs Low Risk Periods", """
    SELECT
        CASE WHEN gprd > (SELECT AVG(gprd) FROM daily_prices)
             THEN 'High Risk' ELSE 'Low Risk' END AS risk_level,
        ROUND(AVG(gold_price),   2) AS avg_gold,
        ROUND(AVG(silver_price), 2) AS avg_silver,
        COUNT(*) AS days
    FROM daily_prices
    GROUP BY 1
""")

# ── Query 3: Monthly Seasonality ─────────────────────────────────────────────
run("Monthly Seasonality", """
    SELECT
        month,
        ROUND(AVG(gold_change_percent), 4) AS avg_daily_change_percent,
        ROUND(AVG(gold_price),          2) AS avg_gold_price
    FROM daily_prices
    GROUP BY month
    ORDER BY month
""")

# ── Query 4: Year-over-Year Gold & Silver Returns ─────────────────────────────
run("Year-over-Year Gold Growth Rate", """
    SELECT
        year,
        ROUND(gold_annual_return_percent,   2) AS gold_return_percent,
        ROUND(silver_annual_return_percent, 2) AS silver_return_percent,
        ROUND(avg_gprd,                     2) AS avg_gprd
    FROM annual_summary
    ORDER BY year
""")

# ── Query 5: Geopolitical Events Ranked by GPRD ───────────────────────────────
run("Geopolitical Events Ranked by GPRD", """
    SELECT event_name, date,
           ROUND(gprd,       2) AS gprd,
           ROUND(gold_price, 2) AS gold_price
    FROM geopolitical_events
    ORDER BY gprd DESC
""")

# ── Query 6: Gold-Silver Ratio Extremes ───────────────────────────────────────
run("Gold-Silver Ratio Extremes", """
    SELECT date, gold_price, silver_price,
           ROUND(gold_silver_ratio, 2) AS ratio
    FROM daily_prices
    ORDER BY gold_silver_ratio DESC
    LIMIT 10
""")

# ── Query 7: Top 20 Volatility Spikes ────────────────────────────────────────
run("Top 20 Volatility Spikes", """
    SELECT date, gold_price,
           ROUND(gold_volatility_30 * 100, 2) AS volatility_percent,
           gprd
    FROM daily_prices
    WHERE gold_volatility_30 IS NOT NULL
    ORDER BY gold_volatility_30 DESC
    LIMIT 20
""")

# ── Query 8: Decade-by-Decade Comparison ──────────────────────────────────────
run("Decade-by-Decade Comparison", """
    SELECT decade,
           ROUND(AVG(gold_price),   2) AS avg_gold,
           ROUND(AVG(silver_price), 2) AS avg_silver,
           ROUND(AVG(gprd),         2) AS avg_gprd,
           COUNT(*) AS trading_days
    FROM daily_prices
    GROUP BY decade
    ORDER BY decade
""")

conn.close()
print(f"\n{'-'*60}")
print("All queries executed successfully.")
print(f"{'-'*60}")
