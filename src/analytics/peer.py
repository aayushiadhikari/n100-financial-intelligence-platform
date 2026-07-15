import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path("data/db/nifty100.db")
OUTPUT = Path("output")

OUTPUT.mkdir(exist_ok=True)


METRIC_MAP = {
    "roe": "return_on_equity_pct",
    "roce": "return_on_capital_employed_pct",
    "npm": "net_profit_margin_pct",
    "debt_to_equity": "debt_to_equity",
    "fcf": "free_cash_flow_cr",
    "pat_cagr_5yr": "pat_cagr_5yr",
    "revenue_cagr_5yr": "revenue_cagr_5yr",
    "eps_cagr_5yr": "eps_cagr_5yr",
    "interest_coverage": "interest_coverage",
    "asset_turnover": "asset_turnover"
}

INVERSE_METRICS = {"debt_to_equity"}


def percent_rank(series, inverse=False):
    numeric = pd.to_numeric(series, errors="coerce")

    valid_count = numeric.notna().sum()

    if valid_count == 0:
        return pd.Series([0] * len(series), index=series.index)

    ranks = numeric.rank(method="min", pct=True)

    if inverse:
        ranks = 1 - ranks + (1 / valid_count)

    return ranks.fillna(0).clip(0, 1)


def load_data():
    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql_query(
        "SELECT * FROM financial_ratios",
        conn
    )

    peer_groups = pd.read_sql_query(
        "SELECT * FROM peer_groups",
        conn
    )

    companies = pd.read_sql_query(
        "SELECT id, company_name FROM companies",
        conn
    )

    conn.close()

    return ratios, peer_groups, companies


def get_latest_year_df(ratios):
    # TTM ko ignore karke latest annual year use karenge
    annual = ratios[
        ratios["year"].astype(str).str.match(r"^\d{4}-\d{2}$", na=False)
    ].copy()

    latest_year = annual["year"].dropna().max()

    latest = annual[annual["year"] == latest_year].copy()

    return latest, latest_year


def compute_peer_percentiles():
    ratios, peer_groups, companies = load_data()

    latest, latest_year = get_latest_year_df(ratios)

    df = peer_groups.merge(
        latest,
        on="company_id",
        how="left"
    )

    df = df.merge(
        companies,
        left_on="company_id",
        right_on="id",
        how="left"
    )

    rows = []

    for peer_group_name, group in df.groupby("peer_group_name"):

        for metric_name, column_name in METRIC_MAP.items():

            if column_name not in group.columns:
                continue

            inverse = metric_name in INVERSE_METRICS

            ranks = percent_rank(
                group[column_name],
                inverse=inverse
            )

            for idx, row in group.iterrows():

                rows.append({
                    "company_id": row["company_id"],
                    "company_name": row.get("company_name"),
                    "peer_group_name": peer_group_name,
                    "metric": metric_name,
                    "value": row.get(column_name),
                    "percentile_rank": round(float(ranks.loc[idx]), 4),
                    "year": latest_year
                })

    percentiles = pd.DataFrame(rows)

    return percentiles, latest_year


def write_peer_percentiles_to_sqlite(percentiles):
    conn = sqlite3.connect(DB_PATH)

    percentiles.to_sql(
        "peer_percentiles",
        conn,
        if_exists="replace",
        index=False
    )

    count = pd.read_sql_query(
        "SELECT COUNT(*) AS row_count FROM peer_percentiles",
        conn
    )["row_count"].iloc[0]

    conn.close()

    print("peer_percentiles table populated")
    print("Rows:", count)


def generate_peer_percentile_csv(percentiles):
    percentiles.to_csv(
        OUTPUT / "peer_percentiles.csv",
        index=False
    )

    print("output/peer_percentiles.csv generated")


def run_peer_engine():
    percentiles, latest_year = compute_peer_percentiles()

    generate_peer_percentile_csv(percentiles)

    write_peer_percentiles_to_sqlite(percentiles)

    peer_group_count = percentiles["peer_group_name"].nunique()
    company_count = percentiles["company_id"].nunique()

    print()
    print("Peer Engine Completed")
    print("Latest Year:", latest_year)
    print("Peer Groups:", peer_group_count)
    print("Companies Ranked:", company_count)


if __name__ == "__main__":
    run_peer_engine()