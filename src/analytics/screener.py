import pandas as pd
from pathlib import Path

PROCESSED_PATH = Path("data/processed")


def run_screeners():

    df = pd.read_csv(PROCESSED_PATH / "kpi_master.csv")

    # Fixed reporting year
    latest_year = "2024-03"

    latest = df[df["year"] == latest_year].copy()

    # Quality Growth
    quality_growth = latest[
        (latest["return_on_equity_pct_final"] >= 15)
        & (latest["debt_to_equity_final"] <= 1)
        & (latest["free_cash_flow_cr_final"] > 0)
    ].sort_values(
        "health_score",
        ascending=False
    )

    # Debt Free
    debt_free = latest[
        latest["debt_to_equity_final"] == 0
    ].sort_values(
        "health_score",
        ascending=False
    )

    # Value
    value = latest[
        (latest["pe_ratio_final"] <= 20)
        & (latest["pb_ratio_final"] <= 3)
    ].sort_values(
        "health_score",
        ascending=False
    )

    # High ROE
    high_roe = latest[
        latest["return_on_equity_pct_final"] >= 20
    ].sort_values(
        "return_on_equity_pct_final",
        ascending=False
    )

    # Low Debt
    low_debt = latest[
        latest["debt_to_equity_final"] <= 0.5
    ].sort_values(
        "health_score",
        ascending=False
    )

    # Strong Cashflow
    strong_cashflow = latest[
        (latest["free_cash_flow_cr_final"] > 0)
        & (latest["cfo_to_net_profit"] > 1)
    ].sort_values(
        "health_score",
        ascending=False
    )

    # Output Excel
    output_file = PROCESSED_PATH / "screener_master.xlsx"

    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:

        quality_growth.to_excel(
            writer,
            sheet_name="Quality_Growth",
            index=False
        )

        debt_free.to_excel(
            writer,
            sheet_name="Debt_Free",
            index=False
        )

        value.to_excel(
            writer,
            sheet_name="Value",
            index=False
        )

        high_roe.to_excel(
            writer,
            sheet_name="High_ROE",
            index=False
        )

        low_debt.to_excel(
            writer,
            sheet_name="Low_Debt",
            index=False
        )

        strong_cashflow.to_excel(
            writer,
            sheet_name="Strong_Cashflow",
            index=False
        )

    # CSV outputs

    quality_growth.to_csv(
        PROCESSED_PATH / "quality_growth_screener.csv",
        index=False
    )

    debt_free.to_csv(
        PROCESSED_PATH / "debt_free_screener.csv",
        index=False
    )

    value.to_csv(
        PROCESSED_PATH / "value_screener.csv",
        index=False
    )

    high_roe.to_csv(
        PROCESSED_PATH / "high_roe_screener.csv",
        index=False
    )

    low_debt.to_csv(
        PROCESSED_PATH / "low_debt_screener.csv",
        index=False
    )

    strong_cashflow.to_csv(
        PROCESSED_PATH / "strong_cashflow_screener.csv",
        index=False
    )

    print("screener_master.xlsx generated successfully.")
    print("CSV screener outputs generated successfully.")
    print()

    print("Screening Year:", latest_year)
    print("Quality Growth:", len(quality_growth))
    print("Debt Free:", len(debt_free))
    print("Value:", len(value))
    print("High ROE:", len(high_roe))
    print("Low Debt:", len(low_debt))
    print("Strong Cashflow:", len(strong_cashflow))


if __name__ == "__main__":
    run_screeners()