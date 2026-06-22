import pandas as pd
from pathlib import Path

PROCESSED = Path("data/processed")


def generate_peer_intelligence():

    peers = pd.read_csv(
        PROCESSED / "peer_summary.csv"
    )

    leaders = pd.read_csv(
        PROCESSED / "sector_leaders.csv"
    )

    report = []

    for _, row in leaders.iterrows():

        report.append([
            row["company_id"],
            row["company_name"],
            "Sector Leader",
            row["health_score"]
        ])

    peer_report = pd.DataFrame(
        report,
        columns=[
            "company_id",
            "company_name",
            "peer_status",
            "health_score"
        ]
    )

    peer_report.to_csv(
        PROCESSED / "peer_intelligence.csv",
        index=False
    )

    print(
        "peer_intelligence.csv generated"
    )

    print(
        "Peer Leaders:",
        len(peer_report)
    )


if __name__ == "__main__":
    generate_peer_intelligence()