import pandas as pd
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_FILE = BASE_DIR / "data" / "raw" / "Fleet_Preventative_Maintenance_&_Repair_Work_Orders_20260624.csv"
DB_FILE = BASE_DIR / "database" / "fleet_maintenance_dw.db"

conn = sqlite3.connect(DB_FILE)

cols = [
    "UNIQUE_WORK_ORDER_NO",
    "CREATE_DATE",
    "LOC_WORK_ORDER_LOC",
    "LOC_WORK_ORDER_LOC_NAME",
    "WORK_ORDER_YR",
    "JOB_TYPE",
    "EQ_EQUIP_NO",
    "WORK_ORDER_STATUS",
    "REAS_REAS_FOR_REPAIR",
    "REAS_FOR_REPAIR_DESC",
    "PRI_PRIORITY_CODE",
    "DEPT_EQUIP_DEPT",
    "DEPT_EQUIP_DEPT_NAME",
    "EQ_PARENT_EQUIP_NO",
    "DOWNTIME_HRS_USER",
    "DOWNTIME_HRS_SHOP",
    "DELAY_HOURS",
    "LABOR_HOURS",
    "LABOR_COST",
    "PARTS_COST",
    "COMML_COST",
    "TOTAL_COST"
]

print("Lendo CSV...")
df = pd.read_csv(RAW_FILE, usecols=cols, low_memory=False)

print("Tratando datas...")
df["CREATE_DATE"] = pd.to_datetime(df["CREATE_DATE"], errors="coerce")
df = df.dropna(subset=["CREATE_DATE"])

print("Tratando valores numéricos...")
numeric_cols = [
    "DOWNTIME_HRS_USER",
    "DOWNTIME_HRS_SHOP",
    "DELAY_HOURS",
    "LABOR_HOURS",
    "LABOR_COST",
    "PARTS_COST",
    "COMML_COST",
    "TOTAL_COST"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

print("Criando Dim_Date...")
dim_date = df[["CREATE_DATE"]].drop_duplicates().copy()
dim_date["date_id"] = dim_date["CREATE_DATE"].dt.strftime("%Y%m%d").astype(int)
dim_date["date"] = dim_date["CREATE_DATE"].dt.date.astype(str)
dim_date["year"] = dim_date["CREATE_DATE"].dt.year
dim_date["month"] = dim_date["CREATE_DATE"].dt.month
dim_date["month_name"] = dim_date["CREATE_DATE"].dt.month_name()
dim_date["quarter"] = dim_date["CREATE_DATE"].dt.quarter
dim_date = dim_date[["date_id", "date", "year", "month", "month_name", "quarter"]]

print("Criando Dim_Asset...")
dim_asset = df[[
    "EQ_EQUIP_NO",
    "EQ_PARENT_EQUIP_NO",
    "DEPT_EQUIP_DEPT",
    "DEPT_EQUIP_DEPT_NAME"
]].drop_duplicates().copy()

dim_asset = dim_asset.rename(columns={
    "EQ_EQUIP_NO": "asset_id",
    "EQ_PARENT_EQUIP_NO": "parent_asset_id",
    "DEPT_EQUIP_DEPT": "department_id",
    "DEPT_EQUIP_DEPT_NAME": "department_name"
})

print("Criando Dim_JobType...")
dim_job = df[[
    "JOB_TYPE",
    "REAS_REAS_FOR_REPAIR",
    "REAS_FOR_REPAIR_DESC",
    "PRI_PRIORITY_CODE"
]].drop_duplicates().copy()

dim_job.insert(0, "job_type_id", range(1, len(dim_job) + 1))

dim_job = dim_job.rename(columns={
    "JOB_TYPE": "job_type",
    "REAS_REAS_FOR_REPAIR": "repair_reason_id",
    "REAS_FOR_REPAIR_DESC": "repair_reason_desc",
    "PRI_PRIORITY_CODE": "priority_code"
})

print("Criando Dim_Location...")
dim_location = df[[
    "LOC_WORK_ORDER_LOC",
    "LOC_WORK_ORDER_LOC_NAME"
]].drop_duplicates().copy()

dim_location = dim_location.rename(columns={
    "LOC_WORK_ORDER_LOC": "location_id",
    "LOC_WORK_ORDER_LOC_NAME": "location_name"
})

print("Criando Fact_WorkOrders...")
fact = df.copy()
fact["date_id"] = fact["CREATE_DATE"].dt.strftime("%Y%m%d").astype(int)

fact = fact.merge(
    dim_job,
    left_on=["JOB_TYPE", "REAS_REAS_FOR_REPAIR", "REAS_FOR_REPAIR_DESC", "PRI_PRIORITY_CODE"],
    right_on=["job_type", "repair_reason_id", "repair_reason_desc", "priority_code"],
    how="left"
)

fact = fact.rename(columns={
    "UNIQUE_WORK_ORDER_NO": "work_order_id",
    "EQ_EQUIP_NO": "asset_id",
    "LOC_WORK_ORDER_LOC": "location_id",
    "WORK_ORDER_STATUS": "work_order_status",
    "WORK_ORDER_YR": "work_order_year",
    "DOWNTIME_HRS_USER": "downtime_hrs_user",
    "DOWNTIME_HRS_SHOP": "downtime_hrs_shop",
    "DELAY_HOURS": "delay_hours",
    "LABOR_HOURS": "labor_hours",
    "LABOR_COST": "labor_cost",
    "PARTS_COST": "parts_cost",
    "COMML_COST": "commercial_cost",
    "TOTAL_COST": "total_cost"
})

fact = fact[[
    "work_order_id",
    "date_id",
    "asset_id",
    "location_id",
    "job_type_id",
    "work_order_year",
    "work_order_status",
    "downtime_hrs_user",
    "downtime_hrs_shop",
    "delay_hours",
    "labor_hours",
    "labor_cost",
    "parts_cost",
    "commercial_cost",
    "total_cost"
]]

print("Gravando SQLite...")
dim_date.to_sql("dim_date", conn, if_exists="replace", index=False)
dim_asset.to_sql("dim_asset", conn, if_exists="replace", index=False)
dim_job.to_sql("dim_job_type", conn, if_exists="replace", index=False)
dim_location.to_sql("dim_location", conn, if_exists="replace", index=False)
fact.to_sql("fact_work_orders", conn, if_exists="replace", index=False)

conn.close()

print("Data Warehouse criado com sucesso!")
print(f"Banco gerado em: {DB_FILE}")
print(f"Registros na fato: {len(fact):,}")