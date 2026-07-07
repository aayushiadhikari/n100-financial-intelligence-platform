import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    check_opm_mismatch,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    compute_profitability_ratios
)


def test_net_profit_margin_normal_case():
    assert net_profit_margin(100, 1000) == 10


def test_net_profit_margin_zero_sales_returns_none():
    assert net_profit_margin(100, 0) is None


def test_operating_profit_margin_normal_case():
    assert operating_profit_margin(200, 1000) == 20


def test_operating_profit_margin_zero_sales_returns_none():
    assert operating_profit_margin(200, 0) is None


def test_opm_cross_check_mismatch_true():
    assert check_opm_mismatch(20, 18) is True


def test_opm_cross_check_mismatch_false():
    assert check_opm_mismatch(20, 19.5) is False


def test_roe_normal_case():
    result = return_on_equity(
        net_profit=100,
        equity_capital=200,
        reserves=300
    )
    assert result == 20


def test_roe_negative_equity_returns_none():
    result = return_on_equity(
        net_profit=100,
        equity_capital=-200,
        reserves=100
    )
    assert result is None


def test_roce_normal_case():
    result = return_on_capital_employed(
        operating_profit=500,
        depreciation=100,
        equity_capital=1000,
        reserves=500,
        borrowings=500
    )
    assert result == 20


def test_roa_zero_assets_returns_none():
    assert return_on_assets(100, 0) is None


def test_compute_profitability_ratios_full_row():
    row = {
        "sales": 1000,
        "net_profit": 100,
        "operating_profit": 200,
        "opm_percentage": 20,
        "equity_capital": 200,
        "reserves": 300,
        "borrowings": 500,
        "depreciation": 50,
        "total_assets": 2000
    }

    result = compute_profitability_ratios(row)

    assert result["net_profit_margin_pct"] == 10
    assert result["operating_profit_margin_pct"] == 20
    assert result["opm_mismatch_flag"] is False
    assert result["return_on_equity_pct"] == 20
    assert result["return_on_assets_pct"] == 5