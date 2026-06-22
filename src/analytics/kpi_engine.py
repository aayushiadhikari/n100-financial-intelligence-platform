from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np


DB_PATH = Path("data/db/nifty100.db")
PROCESSED_PATH = Path("data/processed")


def safe_divide(numerator, denominator):
    return np.where(
        (denominator == 0) | (pd.isna(denominator)),
        np.nan,
        numerator / denominator
    )


def minmax_score(series, higher_is_better=True):
    series = pd.to_numeric(series, errors="coerce")

    min_val = series.min()
    max_val = series.max()

    if pd.isna(min_val) or pd.isna(max_val) or min_val == max_val:
        return pd.Series([50] * len(series), index=series.index)

    score = (series - min_val) / (max_val - min_val) * 100

    if not higher_is_better:
        score = 100 - score

    return score.clip(0, 100)


def generate_kpis():
    PROCESSED_PATH.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    companies = pd.read_sql_query("SELECT id, company_name FROM companies", conn)
    pnl = pd.read_sql_query("SELECT * FROM profitandloss", conn)
    bs = pd.read_sql_query("SELECT * FROM balancesheet", conn)
    cf = pd.read_sql_query("SELECT * FROM cashflow", conn)
    ratios = pd.read_sql_query("SELECT * FROM financial_ratios", conn)
    market = pd.read_sql_query("SELECT * FROM market_cap", conn)
    sectors = pd.read_sql_query(
        "SELECT company_id, broad_sector, sub_sector FROM sectors",
        conn
    )

    conn.close()

    df = ratios.merge(
        pnl,
        on=["company_id", "year"],
        how="left",
        suffixes=("_ratio", "_pnl")
    )

    df = df.merge(
        bs,
        on=["company_id", "year"],
        how="left",
        suffixes=("", "_bs")
    )

    df = df.merge(
        cf,
        on=["company_id", "year"],
        how="left",
        suffixes=("", "_cf")
    )

    df = df.merge(
        market,
        on=["company_id", "year"],
        how="left",
        suffixes=("", "_market")
    )

    df = df.merge(
        companies,
        left_on="company_id",
        right_on="id",
        how="left"
    )

    df = df.merge(
        sectors,
        on="company_id",
        how="left"
    )

    # Profitability KPIs
    df["net_profit_margin_pct_final"] = df["net_profit_margin_pct"]
    df["operating_profit_margin_pct_final"] = df["operating_profit_margin_pct"]
    df["return_on_equity_pct_final"] = df["return_on_equity_pct"]

    df["return_on_assets_pct"] = safe_divide(
        df["net_profit"],
        df["total_assets"]
    ) * 100

    df["return_on_capital_employed_pct"] = safe_divide(
        df["operating_profit"],
        df["total_assets"] - df["other_liabilities"]
    ) * 100

    # Leverage KPIs
    df["debt_to_equity_final"] = df["debt_to_equity"]
    df["interest_coverage_final"] = df["interest_coverage"]

    df["debt_to_assets_pct"] = safe_divide(
        df["total_debt_cr"],
        df["total_assets"]
    ) * 100

    df["borrowings_to_equity_pct"] = safe_divide(
        df["borrowings"],
        df["equity_capital"] + df["reserves"]
    ) * 100

    # Efficiency KPIs
    df["asset_turnover_final"] = df["asset_turnover"]

    df["sales_to_assets"] = safe_divide(
        df["sales"],
        df["total_assets"]
    )

    df["sales_to_fixed_assets"] = safe_divide(
        df["sales"],
        df["fixed_assets"]
    )

    # Cash Flow KPIs
    df["free_cash_flow_cr_final"] = df["free_cash_flow_cr"]
    df["cash_from_operations_cr_final"] = df["cash_from_operations_cr"]

    df["fcf_margin_pct"] = safe_divide(
        df["free_cash_flow_cr"],
        df["sales"]
    ) * 100

    df["cfo_to_net_profit"] = safe_divide(
        df["cash_from_operations_cr"],
        df["net_profit"]
    )

    df["capex_to_sales_pct"] = safe_divide(
        df["capex_cr"],
        df["sales"]
    ) * 100

    # Valuation KPIs
    df["pe_ratio_final"] = df["pe_ratio"]
    df["pb_ratio_final"] = df["pb_ratio"]
    df["ev_ebitda_final"] = df["ev_ebitda"]
    df["dividend_yield_pct_final"] = df["dividend_yield_pct"]
    df["market_cap_crore_final"] = df["market_cap_crore"]
    df["enterprise_value_crore_final"] = df["enterprise_value_crore"]

    # Per share KPIs
    df["earnings_per_share_final"] = df["earnings_per_share"]
    df["book_value_per_share_final"] = df["book_value_per_share"]
    df["dividend_payout_ratio_pct_final"] = df["dividend_payout_ratio_pct"]

    # Growth KPIs
    df = df.sort_values(["company_id", "year"])

    df["sales_growth_pct"] = df.groupby("company_id")["sales"].pct_change() * 100
    df["net_profit_growth_pct"] = df.groupby("company_id")["net_profit"].pct_change() * 100
    df["eps_growth_pct"] = df.groupby("company_id")["earnings_per_share"].pct_change() * 100
    df["market_cap_growth_pct"] = df.groupby("company_id")["market_cap_crore"].pct_change() * 100

    # Balance Sheet KPIs
    df["total_assets_final"] = df["total_assets"]
    df["total_liabilities_final"] = df["total_liabilities"]
    df["reserves_final"] = df["reserves"]
    df["borrowings_final"] = df["borrowings"]

    # Health Score Components
    df["score_roe"] = minmax_score(df["return_on_equity_pct_final"], True)
    df["score_opm"] = minmax_score(df["operating_profit_margin_pct_final"], True)
    df["score_debt"] = minmax_score(df["debt_to_equity_final"], False)
    df["score_interest"] = minmax_score(df["interest_coverage_final"], True)
    df["score_fcf"] = minmax_score(df["free_cash_flow_cr_final"], True)
    df["score_pe"] = minmax_score(df["pe_ratio_final"], False)

    df["health_score"] = (
        df["score_roe"] * 0.25
        + df["score_opm"] * 0.20
        + df["score_debt"] * 0.20
        + df["score_interest"] * 0.15
        + df["score_fcf"] * 0.10
        + df["score_pe"] * 0.10
    ).round(2)

    df["health_score"] = df["health_score"].fillna(50)

    df["health_band"] = pd.cut(
        df["health_score"],
        bins=[-1, 34, 49, 64, 79, 100],
        labels=["Poor", "Weak", "Average", "Good", "Excellent"]
    )

    df["health_band"] = df["health_band"].astype(str).replace("nan", "Average")

    final_cols = [
        "company_id",
        "company_name",
        "broad_sector",
        "sub_sector",
        "year",

        "net_profit_margin_pct_final",
        "operating_profit_margin_pct_final",
        "return_on_equity_pct_final",
        "return_on_assets_pct",
        "return_on_capital_employed_pct",

        "debt_to_equity_final",
        "interest_coverage_final",
        "debt_to_assets_pct",
        "borrowings_to_equity_pct",

        "asset_turnover_final",
        "sales_to_assets",
        "sales_to_fixed_assets",

        "free_cash_flow_cr_final",
        "cash_from_operations_cr_final",
        "fcf_margin_pct",
        "cfo_to_net_profit",
        "capex_to_sales_pct",

        "pe_ratio_final",
        "pb_ratio_final",
        "ev_ebitda_final",
        "dividend_yield_pct_final",
        "market_cap_crore_final",
        "enterprise_value_crore_final",

        "earnings_per_share_final",
        "book_value_per_share_final",
        "dividend_payout_ratio_pct_final",

        "sales_growth_pct",
        "net_profit_growth_pct",
        "eps_growth_pct",
        "market_cap_growth_pct",

        "total_assets_final",
        "total_liabilities_final",
        "reserves_final",
        "borrowings_final",

        "health_score",
        "health_band"
    ]

    final_df = df[final_cols]

    final_df.to_csv(PROCESSED_PATH / "kpi_master.csv", index=False)

    summary = {
        "total_rows": len(final_df),
        "total_companies": final_df["company_id"].nunique(),
        "total_kpis": len(final_cols) - 5,
        "output_file": "data/processed/kpi_master.csv"
    }

    pd.DataFrame([summary]).to_csv(
        PROCESSED_PATH / "kpi_summary.csv",
        index=False
    )

    print("kpi_master.csv generated successfully.")
    print("kpi_summary.csv generated successfully.")
    print()
    print(pd.DataFrame([summary]))
    print()
    print(final_df.head())


if __name__ == "__main__":
    generate_kpis()