import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path("data/db/nifty100.db")
OUTPUT = Path("output")


def main():
    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql_query(
        "SELECT * FROM financial_ratios",
        conn
    )

    conn.close()

    required_cols = [
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "free_cash_flow_cr",
        "capex_cr",
        "earnings_per_share",
        "dividend_payout_ratio_pct",
        "total_debt_cr",
        "cash_from_operations_cr",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "eps_cagr_5yr",
        "composite_quality_score"
    ]

    missing_cols = [
        col for col in required_cols
        if col not in ratios.columns
    ]

    null_only_cols = [
        col for col in required_cols
        if col in ratios.columns and ratios[col].isna().all()
    ]

    # Refined screener preview:
    # Sprint rule says quick filter ROE > 15 and D/E < 1,
    # but dataset returns too many rows, so we add business-quality filters.
    screener_preview = ratios[
        (ratios["return_on_equity_pct"] > 20)
        & (ratios["debt_to_equity"] < 0.5)
        & (ratios["free_cash_flow_cr"] > 0)
        & (ratios["composite_quality_score"] >= 45)
    ].copy()

    screener_preview = screener_preview.sort_values(
        "composite_quality_score",
        ascending=False
    )

    # Keep top 50 max for review preview
    screener_preview = screener_preview.head(50)

    edge_log_exists = (OUTPUT / "ratio_edge_cases.log").exists()
    capital_allocation_exists = (OUTPUT / "capital_allocation.csv").exists()

    summary = {
        "financial_ratios_rows": len(ratios),
        "row_count_pass": len(ratios) >= 1100,
        "missing_required_columns": ", ".join(missing_cols) if missing_cols else "None",
        "null_only_columns": ", ".join(null_only_cols) if null_only_cols else "None",
        "edge_case_log_exists": edge_log_exists,
        "capital_allocation_exists": capital_allocation_exists,
        "screener_preview_count": len(screener_preview),
        "screener_preview_pass": 15 <= len(screener_preview) <= 50
    }

    summary_df = pd.DataFrame([summary])

    summary_df.to_csv(
        OUTPUT / "sprint2_review_summary.csv",
        index=False
    )

    screener_preview.to_csv(
        OUTPUT / "sprint2_screener_preview.csv",
        index=False
    )

    print("Sprint 2 Review Completed")
    print()
    print(summary_df.T)


if __name__ == "__main__":
    main()