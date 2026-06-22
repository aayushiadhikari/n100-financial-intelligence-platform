import pandas as pd

df = pd.read_excel("data/raw/financial_ratios.xlsx", header=0)

print(df.columns.tolist())
print(df.head())