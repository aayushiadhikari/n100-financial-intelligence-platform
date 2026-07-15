import re
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DB_PATH = Path("data/db/nifty100.db")
OUTPUT_PATH = Path("reports/radar_charts")

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


RADAR_METRICS = {
    "ROE": "return_on_equity_pct",
    "ROCE": "return_on_capital_employed_pct",
    "Net Profit Margin": "net_profit_margin_pct",
    "Debt to Equity": "debt_to_equity",
    "Free Cash Flow": "free_cash_flow_cr",
    "PAT CAGR 5Y": "pat_cagr_5yr",
    "Revenue CAGR 5Y": "revenue_cagr_5yr",
    "Composite Score": "composite_quality_score",
}

INVERSE_METRICS = {
    "debt_to_equity"
}


def load_data():
    connection = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql_query(
        "SELECT * FROM financial_ratios",
        connection
    )

    peer_groups = pd.read_sql_query(
        "SELECT * FROM peer_groups",
        connection
    )

    companies = pd.read_sql_query(
        "SELECT id, company_name FROM companies",
        connection
    )

    connection.close()

    return ratios, peer_groups, companies


def get_latest_annual_data(ratios):
    annual_mask = ratios["year"].astype(str).str.match(
        r"^\d{4}-\d{2}$",
        na=False
    )

    annual = ratios[annual_mask].copy()

    if annual.empty:
        raise ValueError(
            "financial_ratios table me koi valid annual year nahi mila."
        )

    latest_year = annual["year"].max()

    latest = annual[
        annual["year"] == latest_year
    ].copy()

    return latest, latest_year


def clean_filename(value):
    text = str(value).strip()

    text = re.sub(
        r'[<>:"/\\|?*\n\r\t]',
        "_",
        text
    )

    return text


def percentile_score(series, inverse=False):
    numeric = pd.to_numeric(
        series,
        errors="coerce"
    )

    valid_count = numeric.notna().sum()

    if valid_count == 0:
        return pd.Series(
            [50.0] * len(series),
            index=series.index
        )

    if valid_count == 1:
        return pd.Series(
            [50.0 if pd.notna(value) else 0.0 for value in numeric],
            index=series.index
        )

    ranks = numeric.rank(
        method="average",
        pct=True
    ) * 100

    if inverse:
        ranks = 100 - ranks

    return ranks.fillna(0).clip(0, 100)


def prepare_peer_group_scores(group):
    scored = group.copy()

    available_metrics = []

    for label, column in RADAR_METRICS.items():
        if column not in scored.columns:
            continue

        score_column = f"{column}_radar_score"

        scored[score_column] = percentile_score(
            scored[column],
            inverse=column in INVERSE_METRICS
        )

        available_metrics.append(
            (label, column, score_column)
        )

    return scored, available_metrics


def generate_peer_radar_chart(
    row,
    peer_average,
    peer_group_name,
    metric_details,
    latest_year
):
    labels = [
        detail[0]
        for detail in metric_details
    ]

    company_values = [
        float(row[detail[2]])
        if pd.notna(row[detail[2]])
        else 0.0
        for detail in metric_details
    ]

    average_values = [
        float(peer_average[detail[2]])
        if pd.notna(peer_average[detail[2]])
        else 0.0
        for detail in metric_details
    ]

    company_values += company_values[:1]
    average_values += average_values[:1]

    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
        endpoint=False
    ).tolist()

    angles += angles[:1]

    figure = plt.figure(
        figsize=(9, 8)
    )

    axis = figure.add_subplot(
        111,
        polar=True
    )

    axis.plot(
        angles,
        company_values,
        linewidth=2.2,
        label=str(row["company_id"])
    )

    axis.fill(
        angles,
        company_values,
        alpha=0.22
    )

    axis.plot(
        angles,
        average_values,
        linewidth=2,
        linestyle="--",
        label="Peer Group Average"
    )

    axis.set_xticks(
        angles[:-1]
    )

    axis.set_xticklabels(
        labels,
        fontsize=9
    )

    axis.set_ylim(
        0,
        100
    )

    axis.set_yticks(
        [20, 40, 60, 80, 100]
    )

    axis.set_yticklabels(
        ["20", "40", "60", "80", "100"],
        fontsize=8
    )

    company_name = row.get(
        "company_name",
        row["company_id"]
    )

    axis.set_title(
        (
            f"{company_name}\n"
            f"Peer Group: {peer_group_name} | Year: {latest_year}"
        ),
        fontsize=13,
        pad=25
    )

    axis.legend(
        loc="upper right",
        bbox_to_anchor=(1.32, 1.15)
    )

    figure.tight_layout()

    company_id = clean_filename(
        row["company_id"]
    )

    output_file = (
        OUTPUT_PATH /
        f"{company_id}_radar.png"
    )

    figure.savefig(
        output_file,
        dpi=180,
        bbox_inches="tight"
    )

    plt.close(figure)


def generate_standalone_chart(
    row,
    nifty_average,
    latest_year
):
    metric = "composite_quality_score"

    company_value = pd.to_numeric(
        pd.Series([row.get(metric)]),
        errors="coerce"
    ).iloc[0]

    if pd.isna(company_value):
        company_value = 0.0

    figure, axis = plt.subplots(
        figsize=(8, 5)
    )

    labels = [
        str(row["company_id"]),
        "Nifty 100 Average"
    ]

    values = [
        float(company_value),
        float(nifty_average)
    ]

    axis.bar(
        labels,
        values
    )

    axis.set_ylabel(
        "Composite Quality Score"
    )

    axis.set_ylim(
        0,
        max(100, max(values) * 1.2)
    )

    company_name = row.get(
        "company_name",
        row["company_id"]
    )

    axis.set_title(
        (
            f"{company_name}\n"
            f"No Peer Group Assigned | Year: {latest_year}"
        )
    )

    for index, value in enumerate(values):
        axis.text(
            index,
            value,
            f"{value:.2f}",
            ha="center",
            va="bottom"
        )

    figure.tight_layout()

    company_id = clean_filename(
        row["company_id"]
    )

    output_file = (
        OUTPUT_PATH /
        f"{company_id}_standalone.png"
    )

    figure.savefig(
        output_file,
        dpi=180,
        bbox_inches="tight"
    )

    plt.close(figure)


def remove_old_charts():
    for file_path in OUTPUT_PATH.glob(
        "*.png"
    ):
        file_path.unlink()


def generate_radar():
    remove_old_charts()

    ratios, peer_groups, companies = load_data()

    latest, latest_year = get_latest_annual_data(
        ratios
    )

    latest = latest.merge(
        companies,
        left_on="company_id",
        right_on="id",
        how="left"
    )

    peer_data = peer_groups.merge(
        latest,
        on="company_id",
        how="left"
    )

    peer_chart_count = 0

    for peer_group_name, group in peer_data.groupby(
        "peer_group_name"
    ):
        valid_group = group[
            group["company_id"].notna()
        ].copy()

        if valid_group.empty:
            continue

        scored_group, metric_details = prepare_peer_group_scores(
            valid_group
        )

        if len(metric_details) < 3:
            print(
                f"Skipped {peer_group_name}: insufficient metrics."
            )
            continue

        peer_average = scored_group[
            [
                detail[2]
                for detail in metric_details
            ]
        ].mean()

        for _, row in scored_group.iterrows():
            generate_peer_radar_chart(
                row=row,
                peer_average=peer_average,
                peer_group_name=peer_group_name,
                metric_details=metric_details,
                latest_year=latest_year
            )

            peer_chart_count += 1

    assigned_companies = set(
        peer_groups["company_id"]
        .dropna()
        .astype(str)
    )

    unassigned = latest[
        ~latest["company_id"]
        .astype(str)
        .isin(assigned_companies)
    ].copy()

    nifty_average = pd.to_numeric(
        latest["composite_quality_score"],
        errors="coerce"
    ).mean()

    if pd.isna(nifty_average):
        nifty_average = 50.0

    standalone_count = 0

    for _, row in unassigned.iterrows():
        generate_standalone_chart(
            row=row,
            nifty_average=nifty_average,
            latest_year=latest_year
        )

        standalone_count += 1

    print("Sprint 3 radar charts generated successfully.")
    print("Latest Year:", latest_year)
    print("Peer Radar Charts:", peer_chart_count)
    print("Standalone Charts:", standalone_count)
    print("Total Charts:", peer_chart_count + standalone_count)


if __name__ == "__main__":
    generate_radar()