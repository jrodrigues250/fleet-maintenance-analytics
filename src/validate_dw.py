import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_FILE = BASE_DIR / "database" / "fleet_maintenance_dw.db"

conn = sqlite3.connect(DB_FILE)

queries = {
    "tables": """
        SELECT name 
        FROM sqlite_master 
        WHERE type='table'
        ORDER BY name
    """,
    "fact_count": """
        SELECT COUNT(*) AS total_records
        FROM fact_work_orders
    """,
    "total_cost": """
        SELECT 
            ROUND(SUM(total_cost), 2) AS total_cost,
            ROUND(SUM(labor_cost), 2) AS labor_cost,
            ROUND(SUM(parts_cost), 2) AS parts_cost,
            ROUND(SUM(commercial_cost), 2) AS commercial_cost
        FROM fact_work_orders
    """,
    "top_assets_cost": """
        SELECT 
            asset_id,
            COUNT(*) AS work_orders,
            ROUND(SUM(total_cost), 2) AS total_cost
        FROM fact_work_orders
        GROUP BY asset_id
        ORDER BY total_cost DESC
        LIMIT 10
    """,
    "work_orders_by_year": """
        SELECT 
            work_order_year,
            COUNT(*) AS work_orders,
            ROUND(SUM(total_cost), 2) AS total_cost
        FROM fact_work_orders
        GROUP BY work_order_year
        ORDER BY work_order_year
    """
}

for name, query in queries.items():
    print(f"\n--- {name.upper()} ---")
    df = pd.read_sql(query, conn)
    print(df)

conn.close()