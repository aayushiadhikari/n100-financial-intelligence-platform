import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

PROCESSED = Path("data/processed")
OUTPUT = Path("reports/radar_charts")

OUTPUT.mkdir(
    parents=True,
    exist_ok=True
)


def normalize(series):

    series = pd.to_numeric(
        series,
        errors="coerce"
    ).fillna(0)

    min_val = series.min()
    max_val = series.max()

    if max_val == min_val:
        return pd.Series(
            [50] * len(series),
            index=series.index
        )

    return (
        (series - min_val)
        /
        (max_val - min_val)
        * 100
    )


def generate_radar():

    df = pd.read_csv(
        PROCESSED / "kpi_master.csv"
    )

    latest = (
        df.sort_values("year")
        .groupby("company_id")
        .tail(1)
        .copy()
    )

    metrics = [
        "health_score",
        "return_on_equity_pct_final",
        "operating_profit_margin_pct_final",
        "free_cash_flow_cr_final",
        "asset_turnover_final"
    ]

    available_metrics = [
        m for m in metrics
        if m in latest.columns
    ]

    for metric in available_metrics:

        latest[f"{metric}_norm"] = normalize(
            latest[metric]
        )

    created = 0

    for _, row in latest.iterrows():

        values = []

        for metric in available_metrics:

            values.append(
                float(
                    row[f"{metric}_norm"]
                )
            )

        values += values[:1]

        angles = np.linspace(
            0,
            2 * np.pi,
            len(available_metrics),
            endpoint=False
        ).tolist()

        angles += angles[:1]

        plt.figure(figsize=(6, 6))

        ax = plt.subplot(
            polar=True
        )

        ax.plot(
            angles,
            values,
            linewidth=2
        )

        ax.fill(
            angles,
            values,
            alpha=0.25
        )

        ax.set_xticks(
            angles[:-1]
        )

        ax.set_xticklabels(
            [
                m.replace("_final", "")
                for m in available_metrics
            ]
        )

        company = str(
            row["company_id"]
        )

        plt.title(
            company
        )

        plt.savefig(
            OUTPUT /
            f"{company}_radar.png",
            bbox_inches="tight"
        )

        plt.close()

        created += 1

    print(
        "Radar charts generated"
    )

    print(
        "Charts:",
        created
    )


if __name__ == "__main__":
    generate_radar()