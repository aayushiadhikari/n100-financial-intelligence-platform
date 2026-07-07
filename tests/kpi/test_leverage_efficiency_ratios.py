import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from src.analytics.ratios import (
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    icr_label,
    icr_warning_flag,
    net_debt,
    asset_turnover,
    compute_leverage_efficiency_ratios
)


def test_debt_to_equity_normal_case():
    assert debt_to_equity(500, 200, 300) == 1


def test_debt_to_equity_debt_free_returns_zero():
    assert debt_to_equity(0, 200, 300) == 0


def test_debt_to_equity_negative_equity_returns_none():
    assert debt_to_equity(100, -200, 100) is None


def test_high_leverage_flag_true_for_non_financial():
    assert high_leverage_flag(6, "Industrials") is True


def test_high_leverage_flag_false_for_financials():
    assert high_leverage_flag(6, "Financials") is False


def test_interest_coverage_normal_case():
    assert interest_coverage_ratio(100, 50, 25) == 6


def test_interest_coverage_interest_zero_returns_none():
    assert interest_coverage_ratio(100, 50, 0) is None


def test_icr_label_debt_free():
    assert icr_label(None) == "Debt Free"


def test_icr_label_covered():
    assert icr_label(4) == "Covered"


def test_icr_warning_flag_true():
    assert icr_warning_flag(1.2) is True


def test_icr_warning_flag_false_for_none():
    assert icr_warning_flag(None) is False


def test_net_debt():
    assert net_debt(1000, 300) == 700


def test_asset_turnover_normal_case():
    assert asset_turnover(1000, 500) == 2


def test_asset_turnover_zero_assets_returns_none():
    assert asset_turnover(1000, 0) is None


def test_compute_leverage_efficiency_ratios_full_row():
    row = {
        "borrowings": 500,
        "equity_capital": 200,
        "reserves": 300,
        "operating_profit": 100,
        "other_income": 50,
        "interest": 25,
        "investments": 100,
        "sales": 1000,
        "total_assets": 500,
        "broad_sector": "Industrials"
    }

    result = compute_leverage_efficiency_ratios(row)

    assert result["debt_to_equity"] == 1
    assert result["high_leverage_flag"] is False
    assert result["interest_coverage"] == 6
    assert result["icr_label"] == "Covered"
    assert result["icr_warning_flag"] is False
    assert result["net_debt"] == 400
    assert result["asset_turnover"] == 2