import pandas as pd

df = pd.read_csv("data/processed/kpi_master.csv")
summary = pd.read_csv("data/processed/kpi_summary.csv")

print("\nKPI MASTER VERIFICATION\n")

print("Rows:", len(df))
print("Companies:", df["company_id"].nunique())
print("Columns:", len(df.columns))
print("Missing health scores:", df["health_score"].isna().sum())
print("Missing health bands:", df["health_band"].isna().sum())

print("\nHealth Band Distribution:")
print(df["health_band"].value_counts())

print("\nTop 10 Companies by Health Score:")
print(
    df.sort_values("health_score", ascending=False)[
        ["company_id", "company_name", "year", "health_score", "health_band"]
    ].head(10)
)

print("\nKPI Summary:")
print(summary)