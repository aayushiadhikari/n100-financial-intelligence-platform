import pandas as pd

files = [
    "profitandloss.xlsx",
    "market_cap.xlsx",
    "balancesheet.xlsx"
]

for file in files:
    print("\n")
    print("=" * 80)
    print(file)

    df = pd.read_excel(
        f"data/raw/{file}",
        header=0
    )

    print(df.columns.tolist())