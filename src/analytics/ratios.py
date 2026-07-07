from typing import Optional, Dict, Any


def safe_divide(numerator, denominator) -> Optional[float]:
    if denominator is None or denominator == 0:
        return None
    return numerator / denominator


def net_profit_margin(net_profit, sales) -> Optional[float]:
    result = safe_divide(net_profit, sales)
    if result is None:
        return None
    return result * 100


def operating_profit_margin(operating_profit, sales) -> Optional[float]:
    result = safe_divide(operating_profit, sales)
    if result is None:
        return None
    return result * 100


def check_opm_mismatch(computed_opm, source_opm, tolerance=1.0) -> bool:
    if computed_opm is None or source_opm is None:
        return False
    return abs(computed_opm - source_opm) > tolerance


def return_on_equity(net_profit, equity_capital, reserves) -> Optional[float]:
    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return (net_profit / equity) * 100


def return_on_capital_employed(
    operating_profit,
    depreciation,
    equity_capital,
    reserves,
    borrowings
) -> Optional[float]:

    ebit = operating_profit - depreciation
    capital_employed = equity_capital + reserves + borrowings

    if capital_employed <= 0:
        return None

    return (ebit / capital_employed) * 100


def return_on_assets(net_profit, total_assets) -> Optional[float]:
    if total_assets == 0:
        return None

    return (net_profit / total_assets) * 100


def debt_to_equity(borrowings, equity_capital, reserves) -> Optional[float]:
    equity = equity_capital + reserves

    if borrowings == 0:
        return 0

    if equity <= 0:
        return None

    return borrowings / equity


def high_leverage_flag(de_ratio, broad_sector) -> bool:
    if de_ratio is None:
        return False

    if broad_sector == "Financials":
        return False

    return de_ratio > 5


def interest_coverage_ratio(
    operating_profit,
    other_income,
    interest
) -> Optional[float]:

    if interest == 0:
        return None

    return (operating_profit + other_income) / interest


def icr_label(icr) -> str:
    if icr is None:
        return "Debt Free"
    return "Covered"


def icr_warning_flag(icr) -> bool:
    if icr is None:
        return False
    return icr < 1.5


def net_debt(borrowings, investments) -> float:
    return borrowings - investments


def asset_turnover(sales, total_assets) -> Optional[float]:
    if total_assets == 0:
        return None
    return sales / total_assets


def compute_profitability_ratios(row: Dict[str, Any]) -> Dict[str, Any]:
    sales = row.get("sales")
    net_profit = row.get("net_profit")
    operating_profit = row.get("operating_profit")
    source_opm = row.get("opm_percentage")
    equity_capital = row.get("equity_capital")
    reserves = row.get("reserves")
    borrowings = row.get("borrowings")
    depreciation = row.get("depreciation")
    total_assets = row.get("total_assets")

    npm = net_profit_margin(net_profit, sales)
    computed_opm = operating_profit_margin(operating_profit, sales)

    roe = return_on_equity(
        net_profit,
        equity_capital,
        reserves
    )

    roce = return_on_capital_employed(
        operating_profit,
        depreciation,
        equity_capital,
        reserves,
        borrowings
    )

    roa = return_on_assets(
        net_profit,
        total_assets
    )

    opm_mismatch = check_opm_mismatch(
        computed_opm,
        source_opm
    )

    return {
        "net_profit_margin_pct": npm,
        "operating_profit_margin_pct": computed_opm,
        "opm_source_value": source_opm,
        "opm_mismatch_flag": opm_mismatch,
        "return_on_equity_pct": roe,
        "return_on_capital_employed_pct": roce,
        "return_on_assets_pct": roa
    }


def compute_leverage_efficiency_ratios(row: Dict[str, Any]) -> Dict[str, Any]:
    borrowings = row.get("borrowings")
    equity_capital = row.get("equity_capital")
    reserves = row.get("reserves")
    operating_profit = row.get("operating_profit")
    other_income = row.get("other_income")
    interest = row.get("interest")
    investments = row.get("investments")
    sales = row.get("sales")
    total_assets = row.get("total_assets")
    broad_sector = row.get("broad_sector")

    de_ratio = debt_to_equity(
        borrowings,
        equity_capital,
        reserves
    )

    icr = interest_coverage_ratio(
        operating_profit,
        other_income,
        interest
    )

    return {
        "debt_to_equity": de_ratio,
        "high_leverage_flag": high_leverage_flag(
            de_ratio,
            broad_sector
        ),
        "interest_coverage": icr,
        "icr_label": icr_label(icr),
        "icr_warning_flag": icr_warning_flag(icr),
        "net_debt": net_debt(
            borrowings,
            investments
        ),
        "asset_turnover": asset_turnover(
            sales,
            total_assets
        )
    }