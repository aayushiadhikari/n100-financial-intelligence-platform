import pandas as pd
import numpy as np
from pathlib import Path

PROCESSED = Path("data/processed")
OUTPUT = Path("output")


def free_cash_flow(operating_activity, investing_activity):
    if (
        operating_activity is None
        or investing_activity is None
        or pd.isna(operating_activity)
        or pd.isna(investing_activity)
    ):
        return None

    return operating_activity + investing_activity


def cfo_quality_score(cfo_series, pat_series):
    ratios = []

    for cfo, pat in zip(cfo_series, pat_series):
        if (
            cfo is None
            or pat is None
            or pd.isna(cfo)
            or pd.isna(pat)
            or pat == 0
        ):
            continue

        ratios.append(cfo / pat)

    if len(ratios) == 0:
        return None, "NA"

    avg = np.mean(ratios)

    if avg > 1:
        label = "High Quality"
    elif avg >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"

    return round(avg, 2), label


def capex_intensity(investing_activity, sales):
    if (
        investing_activity is None
        or sales is None
        or pd.isna(investing_activity)
        or pd.isna(sales)
        or sales == 0
    ):
        return None, "NA"

    intensity = abs(investing_activity) / sales * 100

    if intensity < 3:
        label = "Asset Light"
    elif intensity <= 8:
        label = "Moderate"
    else:
        label = "Capital Intensive"

    return round(intensity, 2), label


def fcf_conversion(free_cash_flow_value, operating_profit):
    if (
        free_cash_flow_value is None
        or operating_profit is None
        or pd.isna(free_cash_flow_value)
        or pd.isna(operating_profit)
        or operating_profit == 0
    ):
        return None

    return round((free_cash_flow_value / operating_profit) * 100, 2)


def sign_label(value):
    if value is None or pd.isna(value):
        return "0"

    if value > 0:
        return "+"

    if value < 0:
        return "-"

    return "0"


def capital_allocation_pattern(cfo, cfi, cff, cfo_quality=None):
    cfo_sign = sign_label(cfo)
    cfi_sign = sign_label(cfi)
    cff_sign = sign_label(cff)

    pattern = (cfo_sign, cfi_sign, cff_sign)

    if pattern == ("+", "-", "-"):
        if cfo_quality is not None and cfo_quality > 1:
            label = "Shareholder Returns"
        else:
            label = "Reinvestor"

    elif pattern == ("+", "+", "-"):
        label = "Liquidating Assets"

    elif pattern == ("-", "+", "+"):
        label = "Distress Signal"

    elif pattern == ("-", "-", "+"):
        label = "Growth Funded by Debt"

    elif pattern == ("+", "+", "+"):
        label = "Cash Accumulator"

    elif pattern == ("-", "-", "-"):
        label = "Pre-Revenue"

    elif pattern == ("+", "-", "+"):
        label = "Mixed"

    else:
        label = "Other"

    return cfo_sign, cfi_sign, cff_sign, label


def generate_capital_allocation_csv():
    OUTPUT.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(PROCESSED / "kpi_master.csv")

    rows = []

    for _, row in df.iterrows():
        cfo = row.get("cash_from_operations_cr_final")
        cfi = -abs(row.get("capex_to_sales_pct", 0))
        fcf = row.get("free_cash_flow_cr_final")
        cff = fcf - cfo if pd.notna(fcf) and pd.notna(cfo) else 0

        cfo_quality = None
        if pd.notna(cfo) and pd.notna(row.get("earnings_per_share_final", None)):
            cfo_quality = 1

        cfo_sign, cfi_sign, cff_sign, label = capital_allocation_pattern(
            cfo,
            cfi,
            cff,
            cfo_quality
        )

        rows.append({
            "company_id": row.get("company_id"),
            "year": row.get("year"),
            "cfo_sign": cfo_sign,
            "cfi_sign": cfi_sign,
            "cff_sign": cff_sign,
            "pattern_label": label
        })

    output_df = pd.DataFrame(rows)
    output_df.to_csv(OUTPUT / "capital_allocation.csv", index=False)

    print("output/capital_allocation.csv generated")
    print("Rows:", len(output_df))


if __name__ == "__main__":
    generate_capital_allocation_csv()