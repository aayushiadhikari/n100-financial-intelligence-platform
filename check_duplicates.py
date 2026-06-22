import pandas as pd

df = pd.read_excel("data/raw/balancesheet.xlsx", header=1)

df.columns = [str(col).strip() for col in df.columns]

print("Columns:")
print(df.columns.tolist())

dups = df[df.duplicated(
    subset=["company_id", "year"],
    keep=False
)]

print("\nDuplicate rows:", len(dups))
print(dups[["company_id", "year"]].head(30))