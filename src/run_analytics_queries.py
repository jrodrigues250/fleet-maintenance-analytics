import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_FILE = BASE_DIR / "database" / "fleet_maintenance_dw.db"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB_FILE)

queries = {
    "kpis_gerais": """
        SELECT
            COUNT(*) AS total_work_orders,
            COUNT(DISTINCT asset_id) AS total_assets,
            ROUND(SUM(total_cost), 2) AS total_cost,
            ROUND(SUM(labor_hours), 2) AS total_labor_hours,
            ROUND(SUM(downtime_hrs_user + downtime_hrs_shop), 2) AS total_downtime_hours
        FROM fact_work_orders
    """,

    "pareto_custos_ativos": """
        WITH asset_cost AS (
            SELECT
                asset_id,
                ROUND(SUM(total_cost), 2) AS total_cost
            FROM fact_work_orders
            GROUP BY asset_id
        ),
        ranked AS (
            SELECT
                asset_id,
                total_cost,
                SUM(total_cost) OVER (ORDER BY total_cost DESC) AS cumulative_cost,
                SUM(total_cost) OVER () AS grand_total_cost
            FROM asset_cost
        )
        SELECT
            asset_id,
            total_cost,
            ROUND(cumulative_cost, 2) AS cumulative_cost,
            ROUND((cumulative_cost / grand_total_cost) * 100, 2) AS cumulative_percentage
        FROM ranked
        ORDER BY total_cost DESC
    """,

    "custos_por_ano": """
        SELECT
            d.year,
            COUNT(*) AS work_orders,
            ROUND(SUM(f.total_cost), 2) AS total_cost
        FROM fact_work_orders f
        JOIN dim_date d ON f.date_id = d.date_id
        GROUP BY d.year
        ORDER BY d.year
    """,

    "custos_por_motivo_reparo": """
        SELECT
            j.repair_reason_desc,
            COUNT(*) AS work_orders,
            ROUND(SUM(f.total_cost), 2) AS total_cost
        FROM fact_work_orders f
        LEFT JOIN dim_job_type j ON f.job_type_id = j.job_type_id
        GROUP BY j.repair_reason_desc
        ORDER BY total_cost DESC
    """
}

for name, query in queries.items():
    df = pd.read_sql(query, conn)
    output_file = OUTPUT_DIR / f"{name}.csv"
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"Gerado: {output_file}")

conn.close()

print("Consultas analíticas executadas com sucesso.")