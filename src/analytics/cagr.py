from typing import Optional, Tuple
import pandas as pd


def calculate_cagr(start_value, end_value, years) -> Tuple[Optional[float], str]:
    """
    CAGR formula:
    ((end / start) ** (1 / years) - 1) * 100
    """

    if years <= 0:
        return None, "INSUFFICIENT"

    if start_value is None or end_value is None:
        return None, "INSUFFICIENT"

    if pd.isna(start_value) or pd.isna(end_value):
        return None, "INSUFFICIENT"

    if start_value == 0:
        return None, "ZERO_BASE"

    if start_value > 0 and end_value > 0:
        cagr = ((end_value / start_value) ** (1 / years) - 1) * 100
        return round(cagr, 2), "NORMAL"

    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"

    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"

    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    return None, "INSUFFICIENT"


def compute_metric_cagr(company_df, metric_col, window):
    """
    Compute CAGR for one company and one metric.
    Uses first and latest value inside required window.
    """

    company_df = company_df.sort_values("year").copy()

    if len(company_df) <= window:
        return None, "INSUFFICIENT"

    start_row = company_df.iloc[-(window + 1)]
    end_row = company_df.iloc[-1]

    start_value = start_row.get(metric_col)
    end_value = end_row.get(metric_col)

    return calculate_cagr(
        start_value=start_value,
        end_value=end_value,
        years=window
    )


def compute_all_cagrs(df):
    """
    Computes 3Y, 5Y, 10Y CAGR for:
    - revenue/sales
    - PAT/net_profit
    - EPS
    """

    rows = []

    for company_id in df["company_id"].dropna().unique():

        company_df = (
            df[df["company_id"] == company_id]
            .sort_values("year")
            .copy()
        )

        latest = company_df.iloc[-1]

        row = {
            "company_id": company_id,
            "year": latest.get("year")
        }

        metric_map = {
            "revenue": "sales",
            "pat": "net_profit",
            "eps": "eps"
        }

        for output_prefix, metric_col in metric_map.items():

            for window in [3, 5, 10]:

                value, flag = compute_metric_cagr(
                    company_df,
                    metric_col,
                    window
                )

                row[f"{output_prefix}_cagr_{window}yr"] = value
                row[f"{output_prefix}_cagr_{window}yr_flag"] = flag

        rows.append(row)

    return pd.DataFrame(rows)