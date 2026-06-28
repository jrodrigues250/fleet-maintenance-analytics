import sqlite3
import pandas as pd
from pathlib import Path

# ============================================
# Paths
# ============================================

BASE_DIR = Path(r"C:\Temp\fleet-maintenance-analytics")

DB_PATH = BASE_DIR / "database" / "fleet_maintenance_dw.db"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "powerbi" / "pareto_assets.csv"

# ============================================
# Extract asset costs from SQLite DW
# ============================================

conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    asset_id,
    SUM(total_cost) AS total_cost
FROM fact_work_orders
WHERE asset_id IS NOT NULL
GROUP BY asset_id
"""

df = pd.read_sql_query(query, conn)

conn.close()

# ============================================
# Generate Pareto ranking
# ============================================

df = df.sort_values(
    by="total_cost",
    ascending=False
).reset_index(drop=True)

df["rank"] = df.index + 1

# Keep only columns needed by Power BI
df = df[[
    "asset_id",
    "total_cost",
    "rank"
]]

# ============================================
# Export for Power BI - pt-BR CSV format
# ============================================

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig",
    sep=";",
    decimal=","
)

print("Pareto assets file generated successfully.")
print(f"Output: {OUTPUT_PATH}")
print(f"Rows: {len(df):,}")
print("")
print(df.head(10))