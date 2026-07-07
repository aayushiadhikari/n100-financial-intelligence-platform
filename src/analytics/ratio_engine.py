from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np

from src.analytics.ratios import (
    compute_profitability_ratios,
    compute_leverage_efficiency_ratios
)

from src.analytics.cagr import compute_all_cagrs
from src.analytics.cashflow_kpis import (
    free_cash_flow,
    capex_intensity,
    fcf_conversion,
    cfo_quality_score,
    capital_allocation_pattern
)


DB_PATH = Path("data/db/nifty100.db")
OUTPUT_PATH = Path("output")

OUTPUT_PATH.mkdir(exist_ok=True)


def load_tables():
    conn = sqlite3.connect(DB_PATH)

    tables = {
        "companies": pd.read_sql_query("SELECT * FROM companies", conn),
        "profitandloss": pd.read_sql_query("SELECT * FROM profitandloss", conn),
        "balancesheet": pd.read_sql_query("SELECT * FROM balancesheet", conn),
        "cashflow": pd.read_sql_query("SELECT * FROM cashflow", conn),
        "sectors": pd.read_sql_query("SELECT * FROM sectors", conn),
    }

    conn.close()
    return tables


def build_base_dataframe(tables):
    pnl = tables["profitandloss"]
    bs = tables["balancesheet"]
    cf = tables["cashflow"]
    companies = tables["companies"]
    sectors = tables["sectors"]

    df = pnl.merge(
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
        companies[["id", "company_name", "roce_percentage", "roe_percentage"]],
        left_on="company_id",
        right_on="id",
        how="left"
    )

    df = df.merge(
        sectors[["company_id", "broad_sector"]],
        on="company_id",
        how="left"
    )

    return df


def compute_row_ratios(df):
    rows = []

    for _, row in df.iterrows():
        row_dict = row.to_dict()

        profitability = compute_profitability_ratios(row_dict)
        leverage = compute_leverage_efficiency_ratios(row_dict)

        fcf = free_cash_flow(
            row_dict.get("operating_activity"),
            row_dict.get("investing_activity")
        )

        capex_value = abs(row_dict.get("investing_activity", 0))

        capex_pct, capex_label = capex_intensity(
            row_dict.get("investing_activity"),
            row_dict.get("sales")
        )

        fcf_conv = fcf_conversion(
            fcf,
            row_dict.get("operating_profit")
        )

        cfo_sign, cfi_sign, cff_sign, allocation_label = capital_allocation_pattern(
            row_dict.get("operating_activity"),
            row_dict.get("investing_activity"),
            row_dict.get("financing_activity")
        )

        result = {
            "id": row_dict.get("id"),
            "company_id": row_dict.get("company_id"),
            "year": row_dict.get("year"),

            "net_profit_margin_pct": profitability["net_profit_margin_pct"],
            "operating_profit_margin_pct": profitability["operating_profit_margin_pct"],
            "return_on_equity_pct": profitability["return_on_equity_pct"],
            "return_on_capital_employed_pct": profitability["return_on_capital_employed_pct"],
            "return_on_assets_pct": profitability["return_on_assets_pct"],

            "debt_to_equity": leverage["debt_to_equity"],
            "high_leverage_flag": leverage["high_leverage_flag"],
            "interest_coverage": leverage["interest_coverage"],
            "icr_label": leverage["icr_label"],
            "icr_warning_flag": leverage["icr_warning_flag"],
            "net_debt": leverage["net_debt"],
            "asset_turnover": leverage["asset_turnover"],

            "free_cash_flow_cr": fcf,
            "capex_cr": capex_value,
            "capex_intensity_pct": capex_pct,
            "capex_intensity_label": capex_label,
            "fcf_conversion_pct": fcf_conv,

            "earnings_per_share": row_dict.get("eps"),
            "dividend_payout_ratio_pct": row_dict.get("dividend_payout"),
            "total_debt_cr": row_dict.get("borrowings"),
            "cash_from_operations_cr": row_dict.get("operating_activity"),

            "cfo_sign": cfo_sign,
            "cfi_sign": cfi_sign,
            "cff_sign": cff_sign,
            "capital_allocation_label": allocation_label,

            "source_roce_percentage": row_dict.get("roce_percentage"),
            "source_roe_percentage": row_dict.get("roe_percentage"),
            "broad_sector": row_dict.get("broad_sector"),
        }

        rows.append(result)

    return pd.DataFrame(rows)


def add_cagrs(ratio_df, base_df):
    cagr_input = base_df[
        [
            "company_id",
            "year",
            "sales",
            "net_profit",
            "eps"
        ]
    ].copy()

    cagr_df = compute_all_cagrs(cagr_input)

    ratio_df = ratio_df.merge(
        cagr_df,
        on=["company_id", "year"],
        how="left"
    )

    return ratio_df


def add_cfo_quality(ratio_df):
    quality_rows = []

    for company_id, group in ratio_df.groupby("company_id"):
        group = group.sort_values("year").tail(5)

        score, label = cfo_quality_score(
            group["cash_from_operations_cr"],
            group["free_cash_flow_cr"].replace(0, np.nan)
        )

        quality_rows.append({
            "company_id": company_id,
            "cfo_quality_score": score,
            "cfo_quality_label": label
        })

    quality_df = pd.DataFrame(quality_rows)

    ratio_df = ratio_df.merge(
        quality_df,
        on="company_id",
        how="left"
    )

    return ratio_df


def add_composite_quality_score(ratio_df):
    def normalize(series, reverse=False):
        s = pd.to_numeric(series, errors="coerce")
        min_val = s.min()
        max_val = s.max()

        if pd.isna(min_val) or pd.isna(max_val) or min_val == max_val:
            return pd.Series([50] * len(s), index=s.index)

        score = (s - min_val) / (max_val - min_val) * 100

        if reverse:
            score = 100 - score

        return score.clip(0, 100)

    ratio_df["score_roe"] = normalize(ratio_df["return_on_equity_pct"])
    ratio_df["score_opm"] = normalize(ratio_df["operating_profit_margin_pct"])
    ratio_df["score_debt"] = normalize(ratio_df["debt_to_equity"], reverse=True)
    ratio_df["score_icr"] = normalize(ratio_df["interest_coverage"])
    ratio_df["score_fcf"] = normalize(ratio_df["free_cash_flow_cr"])

    ratio_df["composite_quality_score"] = (
        ratio_df["score_roe"] * 0.25
        + ratio_df["score_opm"] * 0.20
        + ratio_df["score_debt"] * 0.20
        + ratio_df["score_icr"] * 0.15
        + ratio_df["score_fcf"] * 0.20
    ).round(2)

    ratio_df["composite_quality_score"] = ratio_df["composite_quality_score"].fillna(50)

    return ratio_df


def generate_edge_case_log(ratio_df):
    log_lines = []

    for _, row in ratio_df.iterrows():
        company_id = row["company_id"]
        year = row["year"]

        if row.get("high_leverage_flag") is True:
            log_lines.append(
                f"{company_id},{year},HIGH_LEVERAGE,formula_discrepancy,D/E > 5 for non-financial company"
            )

        if row.get("icr_label") == "Debt Free":
            log_lines.append(
                f"{company_id},{year},DEBT_FREE,data_source_issue,Interest is zero so ICR is stored as None and label Debt Free"
            )

        source_roce = row.get("source_roce_percentage")
        computed_roce = row.get("return_on_capital_employed_pct")

        if pd.notna(source_roce) and pd.notna(computed_roce):
            if abs(source_roce - computed_roce) > 5:
                log_lines.append(
                    f"{company_id},{year},ROCE_MISMATCH,version_difference,Computed ROCE differs from source ROCE by >5%"
                )

        source_roe = row.get("source_roe_percentage")
        computed_roe = row.get("return_on_equity_pct")

        if pd.notna(source_roe) and pd.notna(computed_roe):
            if abs(source_roe - computed_roe) > 5:
                log_lines.append(
                    f"{company_id},{year},ROE_MISMATCH,data_source_issue,Source ROE appears inconsistent; ratio engine value used for analytics"
                )

        for col in [
            "revenue_cagr_3yr_flag",
            "revenue_cagr_5yr_flag",
            "revenue_cagr_10yr_flag",
            "pat_cagr_3yr_flag",
            "pat_cagr_5yr_flag",
            "pat_cagr_10yr_flag",
            "eps_cagr_3yr_flag",
            "eps_cagr_5yr_flag",
            "eps_cagr_10yr_flag",
        ]:
            if col in ratio_df.columns:
                flag = row.get(col)
                if pd.notna(flag) and flag != "NORMAL":
                    log_lines.append(
                        f"{company_id},{year},{col},{flag},CAGR edge case handled and documented"
                    )

    log_path = OUTPUT_PATH / "ratio_edge_cases.log"

    with open(log_path, "w", encoding="utf-8") as file:
        file.write("company_id,year,issue,category,explanation\n")
        for line in log_lines:
            file.write(line + "\n")

    print("output/ratio_edge_cases.log generated")
    print("Edge cases logged:", len(log_lines))


def write_to_sqlite(ratio_df):
    conn = sqlite3.connect(DB_PATH)

    ratio_df.to_sql(
        "financial_ratios",
        conn,
        if_exists="replace",
        index=False
    )

    count = pd.read_sql_query(
        "SELECT COUNT(*) AS row_count FROM financial_ratios",
        conn
    )["row_count"].iloc[0]

    conn.close()

    print("financial_ratios table populated")
    print("Row count:", count)


def run_ratio_engine():
    tables = load_tables()

    base_df = build_base_dataframe(tables)

    ratio_df = compute_row_ratios(base_df)

    ratio_df = add_cagrs(ratio_df, base_df)

    ratio_df = add_cfo_quality(ratio_df)

    ratio_df = add_composite_quality_score(ratio_df)

    generate_edge_case_log(ratio_df)

    write_to_sqlite(ratio_df)

    ratio_df.to_csv(
        OUTPUT_PATH / "financial_ratios_computed.csv",
        index=False
    )

    print("output/financial_ratios_computed.csv generated")
    print("Ratio Engine Completed")


if __name__ == "__main__":
    run_ratio_engine()