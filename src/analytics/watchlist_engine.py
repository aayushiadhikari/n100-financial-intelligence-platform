import pandas as pd

def generate_watchlist():
    df = pd.read_csv("data/processed/kpi_master.csv")

    alerts = []

    for _, row in df.iterrows():

        if row["health_score"] < 35:
            alerts.append([
                row["company_id"],
                row["company_name"],
                "Poor Health Score"
            ])

        if row["debt_to_equity_final"] > 2:
            alerts.append([
                row["company_id"],
                row["company_name"],
                "High Debt"
            ])

    alerts_df = pd.DataFrame(
        alerts,
        columns=[
            "company_id",
            "company_name",
            "alert_reason"
        ]
    )

    alerts_df.to_csv(
        "data/processed/alerts.csv",
        index=False
    )

    alerts_df.to_csv(
        "data/processed/watchlist.csv",
        index=False
    )

    print("alerts.csv generated")
    print("watchlist.csv generated")