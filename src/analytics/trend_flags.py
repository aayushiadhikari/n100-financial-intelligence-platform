import pandas as pd
from pathlib import Path

PROCESSED = Path("data/processed")

def generate_trend_flags():

    df = pd.read_csv(
        PROCESSED / "kpi_master.csv"
    )

    rows = []

    for company in df["company_id"].dropna().unique():

        company_df = (
            df[df["company_id"] == company]
            .sort_values("year")
        )

        if len(company_df) < 2:
            continue

        latest = company_df.iloc[-1]
        previous = company_df.iloc[-2]

        roe_now = latest.get(
            "return_on_equity_pct_final", 0
        )

        roe_prev = previous.get(
            "return_on_equity_pct_final", 0
        )

        debt_now = latest.get(
            "debt_to_equity_final", 0
        )

        debt_prev = previous.get(
            "debt_to_equity_final", 0
        )

        if roe_now > roe_prev:

            rows.append([
                company,
                latest["company_name"],
                latest["year"],
                "ROE Improving"
            ])

        elif roe_now < roe_prev:

            rows.append([
                company,
                latest["company_name"],
                latest["year"],
                "ROE Deteriorating"
            ])

        if debt_now < debt_prev:

            rows.append([
                company,
                latest["company_name"],
                latest["year"],
                "Debt Reducing"
            ])

        elif debt_now > debt_prev:

            rows.append([
                company,
                latest["company_name"],
                latest["year"],
                "Debt Increasing"
            ])

    out = pd.DataFrame(
        rows,
        columns=[
            "company_id",
            "company_name",
            "year",
            "trend_flag"
        ]
    )

    out.to_csv(
        PROCESSED / "trend_flags.csv",
        index=False
    )

    print(
        "trend_flags.csv generated"
    )

    print(
        "Total trend flags:",
        len(out)
    )

if __name__ == "__main__":
    generate_trend_flags()