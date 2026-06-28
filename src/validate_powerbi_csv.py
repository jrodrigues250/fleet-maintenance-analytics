import pandas as pd
from pathlib import Path

BASE_DIR = Path(r"C:\Temp\fleet-maintenance-analytics")

FACT_FILE = BASE_DIR / "data" / "processed" / "powerbi" / "fact_work_orders.csv"

df = pd.read_csv(FACT_FILE, low_memory=False)

print("Linhas:", len(df))
print("Soma total_cost:", df["total_cost"].sum())
print("Soma labor_cost:", df["labor_cost"].sum())
print("Soma parts_cost:", df["parts_cost"].sum())
print("Soma commercial_cost:", df["commercial_cost"].sum())

print("\nTop 10 total_cost:")
print(df["total_cost"].sort_values(ascending=False).head(10))