import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_FILE = BASE_DIR / "database" / "fleet_maintenance_dw.db"

conn = sqlite3.connect(DB_FILE)

query = """
SELECT
    asset_id,
    MAX(parent_asset_id) AS parent_asset_id,
    MAX(department_id) AS department_id,
    MAX(department_name) AS department_name
FROM dim_asset
WHERE asset_id IS NOT NULL
GROUP BY asset_id
"""

dim_asset_fixed = pd.read_sql(query, conn)

dim_asset_fixed.to_sql(
    "dim_asset",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print(f"Dim_Asset corrigida com sucesso.")
print(f"Total de ativos únicos: {len(dim_asset_fixed):,}")