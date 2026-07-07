import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path("data/db/nifty100.db")
OUTPUT = Path("output")


def run_ratio_validation():

    OUTPUT.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql_query(
        "SELECT * FROM financial_ratios",
        conn
    )

    conn.close()

    financials = ratios[
        ratios["broad_sector"] == "Financials"
    ]

    non_financials = ratios[
        ratios["broad_sector"] != "Financials"
    ]

    suppressed = 0

    for _, row in financials.iterrows():

        if row["high_leverage_flag"]:

            suppressed += 1

    edge_cases = []

    for _, row in ratios.iterrows():

        source_roe = row.get(
            "source_roe_percentage"
        )

        computed_roe = row.get(
            "return_on_equity_pct"
        )

        if (
            pd.notna(source_roe)
            and
            pd.notna(computed_roe)
        ):

            diff = abs(
                source_roe -
                computed_roe
            )

            if diff > 5:

                edge_cases.append([
                    row["company_id"],
                    row["year"],
                    "ROE",
                    diff,
                    "Data Source Issue"
                ])

        source_roce = row.get(
            "source_roce_percentage"
        )

        computed_roce = row.get(
            "return_on_capital_employed_pct"
        )

        if (
            pd.notna(source_roce)
            and
            pd.notna(computed_roce)
        ):

            diff = abs(
                source_roce -
                computed_roce
            )

            if diff > 5:

                edge_cases.append([
                    row["company_id"],
                    row["year"],
                    "ROCE",
                    diff,
                    "Version Difference"
                ])

    edge_df = pd.DataFrame(
        edge_cases,
        columns=[
            "company_id",
            "year",
            "metric",
            "difference",
            "category"
        ]
    )

    edge_df.to_csv(
        OUTPUT /
        "ratio_edge_cases_review.csv",
        index=False
    )

    print(
        "ratio_edge_cases_review.csv generated"
    )

    print()

    print(
        "Financial Companies:",
        len(financials)
    )

    print(
        "Non Financial Companies:",
        len(non_financials)
    )

    print(
        "Suppressed High Leverage Flags:",
        suppressed
    )

    print(
        "ROE / ROCE Edge Cases:",
        len(edge_df)
    )