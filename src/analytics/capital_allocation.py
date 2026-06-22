import pandas as pd
from pathlib import Path

PROCESSED = Path("data/processed")


def generate_capital_matrix():

    df = pd.read_csv(PROCESSED / "kpi_master.csv")

    latest = (
        df.sort_values("year")
        .groupby("company_id")
        .tail(1)
        .copy()
    )

    latest["allocation_band"] = "Balanced"

    latest.loc[
        (
            latest["free_cash_flow_cr_final"] > 0
        )
        &
        (
            latest["health_score"] >= 60
        ),
        "allocation_band"
    ] = "Cash Generator"

    latest.loc[
        (
            latest["free_cash_flow_cr_final"] > 0
        )
        &
        (
            latest["capex_to_sales_pct"] > 5
        ),
        "allocation_band"
    ] = "Aggressive Growth"

    latest.loc[
        latest["free_cash_flow_cr_final"] < 0,
        "allocation_band"
    ] = "Capital Stressed"

    output = latest[
        [
            "company_id",
            "company_name",
            "health_score",
            "free_cash_flow_cr_final",
            "capex_to_sales_pct",
            "allocation_band"
        ]
    ]

    output.to_csv(
        PROCESSED / "capital_allocation_matrix.csv",
        index=False
    )

    print("capital_allocation_matrix.csv generated")
    print("Rows:", len(output))


if __name__ == "__main__":
    generate_capital_matrix()