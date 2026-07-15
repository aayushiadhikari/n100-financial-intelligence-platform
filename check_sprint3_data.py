import sqlite3
from pathlib import Path

import pandas as pd


DB_PATH = Path("data/db/nifty100.db")


def print_metric_status(dataframe, column):
    if column not in dataframe.columns:
        print(f"{column}: COLUMN MISSING")
        return

    numeric = pd.to_numeric(
        dataframe[column],
        errors="coerce"
    )

    print(
        f"{column}: "
        f"non-null rows={numeric.notna().sum()}, "
        f"companies={dataframe.loc[numeric.notna(), 'company_id'].nunique()}"
    )


def main():
    connection = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql_query(
        "SELECT * FROM financial_ratios",
        connection
    )

    connection.close()

    print("\nFINANCIAL RATIOS DIAGNOSTIC\n")

    print("Total rows:", len(ratios))
    print("Total companies:", ratios["company_id"].nunique())
    print()

    metrics = [
        "return_on_equity_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
        "revenue_cagr_3yr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "composite_quality_score"
    ]

    for metric in metrics:
        print_metric_status(ratios, metric)

    print("\nLATEST NON-NULL CAGR PER COMPANY\n")

    for metric in [
        "revenue_cagr_3yr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr"
    ]:
        if metric not in ratios.columns:
            continue

        valid = ratios[
            pd.to_numeric(
                ratios[metric],
                errors="coerce"
            ).notna()
        ]

        latest_valid = (
            valid.sort_values(["company_id", "year"])
            .groupby("company_id")
            .tail(1)
        )

        print(
            f"{metric}: latest valid companies = "
            f"{latest_valid['company_id'].nunique()}"
        )

    print("\nPRESET CONDITION COUNTS\n")

    snapshot_rows = []

    for company_id, group in ratios.groupby("company_id"):
        group = group.sort_values("year")

        output = {
            "company_id": company_id
        }

        for column in ratios.columns:
            valid_values = group[column].dropna()

            if len(valid_values) > 0:
                output[column] = valid_values.iloc[-1]
            else:
                output[column] = None

        snapshot_rows.append(output)

    snapshot = pd.DataFrame(snapshot_rows)

    roe = pd.to_numeric(
        snapshot["return_on_equity_pct"],
        errors="coerce"
    )

    debt = pd.to_numeric(
        snapshot["debt_to_equity"],
        errors="coerce"
    )

    fcf = pd.to_numeric(
        snapshot["free_cash_flow_cr"],
        errors="coerce"
    )

    revenue_5 = pd.to_numeric(
        snapshot["revenue_cagr_5yr"],
        errors="coerce"
    )

    revenue_3 = pd.to_numeric(
        snapshot["revenue_cagr_3yr"],
        errors="coerce"
    )

    pat_5 = pd.to_numeric(
        snapshot["pat_cagr_5yr"],
        errors="coerce"
    )

    print("ROE > 15:", int((roe > 15).sum()))
    print("D/E < 1:", int((debt < 1).sum()))
    print("FCF > 0:", int((fcf > 0).sum()))
    print("Revenue CAGR 5Y > 10:", int((revenue_5 > 10).sum()))
    print("PAT CAGR 5Y > 20:", int((pat_5 > 20).sum()))
    print("Revenue CAGR 3Y > 10:", int((revenue_3 > 10).sum()))

    quality = snapshot[
        (roe > 15)
        & (debt < 1)
        & (fcf > 0)
        & (revenue_5 > 10)
    ]

    growth = snapshot[
        (pat_5 > 20)
        & (revenue_5 > 15)
        & (debt < 2)
    ]

    print("\nQuality Compounder exact count:", len(quality))
    print("Growth Accelerator exact count:", len(growth))


if __name__ == "__main__":
    main()