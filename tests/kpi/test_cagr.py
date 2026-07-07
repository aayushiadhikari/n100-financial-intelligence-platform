import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from src.analytics.cagr import (
    calculate_cagr,
    compute_metric_cagr,
    compute_all_cagrs
)


def test_normal_cagr():
    value, flag = calculate_cagr(100, 121, 2)
    assert round(value, 2) == 10
    assert flag == "NORMAL"


def test_zero_base_flag():
    value, flag = calculate_cagr(0, 100, 5)
    assert value is None
    assert flag == "ZERO_BASE"


def test_decline_to_loss_flag():
    value, flag = calculate_cagr(100, -50, 5)
    assert value is None
    assert flag == "DECLINE_TO_LOSS"


def test_turnaround_flag():
    value, flag = calculate_cagr(-100, 50, 5)
    assert value is None
    assert flag == "TURNAROUND"


def test_both_negative_flag():
    value, flag = calculate_cagr(-100, -50, 5)
    assert value is None
    assert flag == "BOTH_NEGATIVE"


def test_insufficient_years_flag():
    df = pd.DataFrame({
        "company_id": ["ABC", "ABC"],
        "year": ["2022", "2023"],
        "sales": [100, 120]
    })

    value, flag = compute_metric_cagr(df, "sales", 3)

    assert value is None
    assert flag == "INSUFFICIENT"


def test_compute_metric_cagr_normal():
    df = pd.DataFrame({
        "company_id": ["ABC"] * 4,
        "year": ["2020", "2021", "2022", "2023"],
        "sales": [100, 110, 120, 133.1]
    })

    value, flag = compute_metric_cagr(df, "sales", 3)

    assert round(value, 2) == 10
    assert flag == "NORMAL"


def test_compute_all_cagrs_columns():
    df = pd.DataFrame({
        "company_id": ["ABC"] * 6,
        "year": ["2018", "2019", "2020", "2021", "2022", "2023"],
        "sales": [100, 110, 120, 130, 140, 150],
        "net_profit": [10, 11, 12, 13, 14, 15],
        "eps": [1, 1.1, 1.2, 1.3, 1.4, 1.5]
    })

    result = compute_all_cagrs(df)

    assert "revenue_cagr_3yr" in result.columns
    assert "pat_cagr_5yr" in result.columns
    assert "eps_cagr_10yr_flag" in result.columns


def test_none_input_flag():
    value, flag = calculate_cagr(None, 100, 5)
    assert value is None
    assert flag == "INSUFFICIENT"


def test_nan_input_flag():
    value, flag = calculate_cagr(float("nan"), 100, 5)
    assert value is None
    assert flag == "INSUFFICIENT"