import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_FILE = BASE_DIR / "data" / "raw" / "Fleet_Preventative_Maintenance_&_Repair_Work_Orders_20260624.csv"
OUTPUT_FILE = BASE_DIR / "docs" / "data_dictionary_generated.csv"

df = pd.read_csv(RAW_FILE, nrows=1000, low_memory=False)

summary = pd.DataFrame({
    "column_name": df.columns,
    "data_type": df.dtypes.astype(str).values,
    "non_null_count_sample": df.notna().sum().values,
    "null_count_sample": df.isna().sum().values,
    "sample_value": [
        df[col].dropna().iloc[0] if df[col].dropna().shape[0] > 0 else None
        for col in df.columns
    ]
})

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
summary.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print("Arquivo analisado com sucesso.")
print(f"Colunas encontradas: {len(df.columns)}")
print(f"Dicionário gerado em: {OUTPUT_FILE}")
print("")
print("Colunas:")
for col in df.columns:
    print(f"- {col}")