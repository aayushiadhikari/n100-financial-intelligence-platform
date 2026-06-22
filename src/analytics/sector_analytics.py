import pandas as pd
from pathlib import Path

PROCESSED_PATH = Path("data/processed")


def generate_sector_analytics():

    df = pd.read_csv(
        PROCESSED_PATH / "kpi_master.csv"
    )

    sector_summary = (
        df.groupby("broad_sector")
        .agg({
            "health_score": "mean",
            "market_cap_crore_final": "mean",
            "return_on_equity_pct_final": "mean",
            "debt_to_equity_final": "mean"
        })
        .reset_index()
    )

    sector_summary = sector_summary.sort_values(
        "health_score",
        ascending=False
    )

    sector_summary.to_csv(
        PROCESSED_PATH / "sector_summary.csv",
        index=False
    )

    company_rankings = (
        df.sort_values(
            "health_score",
            ascending=False
        )
    )

    company_rankings.to_csv(
        PROCESSED_PATH / "company_rankings.csv",
        index=False
    )

    print("sector_summary.csv generated")
    print("company_rankings.csv generated")

    print("\nTop Sectors:")
    print(sector_summary.head())

    print("\nTop Companies:")
    print(
        company_rankings[
            [
                "company_id",
                "company_name",
                "health_score"
            ]
        ].head()
    )


if __name__ == "__main__":
    generate_sector_analytics()