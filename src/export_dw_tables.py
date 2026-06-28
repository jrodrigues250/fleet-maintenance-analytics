import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

DB_FILE = BASE_DIR / "database" / "fleet_maintenance_dw.db"
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "powerbi"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

tables = [
    "dim_date",
    "dim_asset",
    "dim_job_type",
    "dim_location",
    "fact_work_orders"
]

conn = sqlite3.connect(DB_FILE)

for table in tables:
    print(f"Exportando {table}...")
    df = pd.read_sql(f"SELECT * FROM {table}", conn)

    output_file = OUTPUT_DIR / f"{table}.csv"

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig",
        sep=";",
        decimal=","
    )

    print(f"Gerado: {output_file} | Linhas: {len(df):,}")

conn.close()

print("Exportação concluída em padrão pt-BR.")