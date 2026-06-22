import pandas as pd
from pathlib import Path

PROCESSED_PATH = Path("data/processed")


def generate_valuation():

    df = pd.read_csv(PROCESSED_PATH / "kpi_master.csv")

    latest = df[df["year"] == "2024-03"].copy()

    latest["pe_flag"] = "Normal"
    latest.loc[
        latest["pe_ratio_final"] > latest["pe_ratio_final"].median() * 1.5,
        "pe_flag"
    ] = "Caution"

    latest.loc[
        latest["pe_ratio_final"] < latest["pe_ratio_final"].median() * 0.7,
        "pe_flag"
    ] = "Discount"

    latest["pb_flag"] = "Normal"
    latest.loc[
        latest["pb_ratio_final"] > latest["pb_ratio_final"].median() * 1.5,
        "pb_flag"
    ] = "Caution"

    latest.loc[
        latest["pb_ratio_final"] < latest["pb_ratio_final"].median() * 0.7,
        "pb_flag"
    ] = "Discount"

    latest["ev_ebitda_flag"] = "Normal"
    latest.loc[
        latest["ev_ebitda_final"] > latest["ev_ebitda_final"].median() * 1.5,
        "ev_ebitda_flag"
    ] = "Caution"

    latest.loc[
        latest["ev_ebitda_final"] < latest["ev_ebitda_final"].median() * 0.7,
        "ev_ebitda_flag"
    ] = "Discount"

    valuation_summary = latest[
        [
            "company_id",
            "company_name",
            "broad_sector",
            "year",
            "market_cap_crore_final",
            "enterprise_value_crore_final",
            "pe_ratio_final",
            "pb_ratio_final",
            "ev_ebitda_final",
            "dividend_yield_pct_final",
            "pe_flag",
            "pb_flag",
            "ev_ebitda_flag",
            "health_score",
            "health_band"
        ]
    ]

    valuation_flags = valuation_summary[
        (valuation_summary["pe_flag"] != "Normal")
        | (valuation_summary["pb_flag"] != "Normal")
        | (valuation_summary["ev_ebitda_flag"] != "Normal")
    ]

    valuation_summary.to_csv(
        PROCESSED_PATH / "valuation_summary.csv",
        index=False
    )

    valuation_flags.to_csv(
        PROCESSED_PATH / "valuation_flags.csv",
        index=False
    )

    print("valuation_summary.csv generated")
    print("valuation_flags.csv generated")
    print("Total valuation records:", len(valuation_summary))
    print("Total valuation flags:", len(valuation_flags))


if __name__ == "__main__":
    generate_valuation()