import pandas as pd


def generate_cashflow_intelligence():

    df = pd.read_csv(
        "data/processed/kpi_master.csv"
    )

    cfo_col = "cash_from_operations_cr_final"
    profit_col = "net_profit_final"

    if profit_col not in df.columns:
        profit_col = None

    if cfo_col in df.columns and profit_col:

        df["cfo_quality"] = (
            df[cfo_col] /
            df[profit_col].replace(0, 1)
        )

    else:

        df["cfo_quality"] = 0

    if cfo_col in df.columns:

        df["distress_flag"] = (
            df[cfo_col] < 0
        )

    else:

        df["distress_flag"] = False

    output = df[
        [
            "company_id",
            "company_name",
            "year",
            "health_score",
            "cfo_quality",
            "distress_flag"
        ]
    ]

    output.to_csv(
        "data/processed/cashflow_intelligence.csv",
        index=False
    )

    print(
        "cashflow_intelligence.csv generated"
    )


if __name__ == "__main__":
    generate_cashflow_intelligence()