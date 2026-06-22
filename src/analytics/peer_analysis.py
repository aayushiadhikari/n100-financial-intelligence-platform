import pandas as pd
from pathlib import Path

PROCESSED_PATH = Path("data/processed")


def generate_peer_analysis():

    df = pd.read_csv(PROCESSED_PATH / "kpi_master.csv")

    latest = df[df["year"] == "2024-03"].copy()

    # Sector Summary
    peer_summary = (
        latest.groupby("broad_sector")
        .agg(
            avg_health_score=("health_score", "mean"),
            avg_roe=("return_on_equity_pct_final", "mean"),
            avg_debt_to_equity=("debt_to_equity_final", "mean"),
            avg_market_cap=("market_cap_crore_final", "mean"),
            company_count=("company_id", "nunique")
        )
        .reset_index()
    )

    peer_summary = peer_summary.sort_values(
        "avg_health_score",
        ascending=False
    )

    peer_summary.to_csv(
        PROCESSED_PATH / "peer_summary.csv",
        index=False
    )

    # Sector Leaders
    sector_leaders = (
        latest.sort_values(
            "health_score",
            ascending=False
        )
        .groupby("broad_sector")
        .head(1)
    )

    sector_leaders.to_csv(
        PROCESSED_PATH / "sector_leaders.csv",
        index=False
    )

    # Top 20 Companies
    top_companies = latest.sort_values(
        "health_score",
        ascending=False
    ).head(20)

    top_companies.to_csv(
        PROCESSED_PATH / "top_20_companies.csv",
        index=False
    )

    # Bottom 20 Companies
    bottom_companies = latest.sort_values(
        "health_score",
        ascending=True
    ).head(20)

    bottom_companies.to_csv(
        PROCESSED_PATH / "bottom_20_companies.csv",
        index=False
    )

    print("peer_summary.csv generated")
    print("sector_leaders.csv generated")
    print("top_20_companies.csv generated")
    print("bottom_20_companies.csv generated")

    print("\nTop Sectors:")
    print(peer_summary.head())

    print("\nTop Companies:")
    print(
        top_companies[
            [
                "company_id",
                "company_name",
                "health_score"
            ]
        ].head()
    )


if __name__ == "__main__":
    generate_peer_analysis()