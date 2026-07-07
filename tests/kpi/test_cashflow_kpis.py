import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion,
    sign_label,
    capital_allocation_pattern
)


def test_free_cash_flow():
    assert free_cash_flow(100, -40) == 60


def test_free_cash_flow_negative():
    assert free_cash_flow(50, -100) == -50


def test_cfo_quality_high():
    score, label = cfo_quality_score([120, 140], [100, 100])
    assert label == "High Quality"


def test_cfo_quality_moderate():
    score, label = cfo_quality_score([60, 70], [100, 100])
    assert label == "Moderate"


def test_cfo_quality_accrual():
    score, label = cfo_quality_score([20, 30], [100, 100])
    assert label == "Accrual Risk"


def test_capex_asset_light():
    value, label = capex_intensity(-20, 1000)
    assert label == "Asset Light"


def test_capex_capital_intensive():
    value, label = capex_intensity(-150, 1000)
    assert label == "Capital Intensive"


def test_fcf_conversion():
    assert fcf_conversion(50, 100) == 50


def test_sign_label_positive():
    assert sign_label(10) == "+"


def test_sign_label_negative():
    assert sign_label(-10) == "-"


def test_pattern_reinvestor():
    cfo, cfi, cff, label = capital_allocation_pattern(100, -50, -20, 0.8)
    assert label == "Reinvestor"


def test_pattern_shareholder_returns():
    cfo, cfi, cff, label = capital_allocation_pattern(100, -50, -20, 1.2)
    assert label == "Shareholder Returns"


def test_pattern_distress_signal():
    cfo, cfi, cff, label = capital_allocation_pattern(-100, 50, 20)
    assert label == "Distress Signal"


def test_pattern_growth_funded_by_debt():
    cfo, cfi, cff, label = capital_allocation_pattern(-100, -50, 200)
    assert label == "Growth Funded by Debt"