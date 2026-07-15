import pandas as pd
from pathlib import Path


SNAPSHOT_PATH = Path(
    "output/screener_company_snapshot.csv"
)


def numeric(dataframe, column):
    return pd.to_numeric(
        dataframe[column],
        errors="coerce"
    )


def print_company_list(title, dataframe, columns):
    print()
    print(title)
    print("-" * 90)

    if dataframe.empty:
        print("No companies found.")
        return

    available_columns = [
        column
        for column in columns
        if column in dataframe.columns
    ]

    print(
        dataframe[available_columns]
        .sort_values(
            "company_id"
        )
        .to_string(index=False)
    )


def main():
    if not SNAPSHOT_PATH.exists():
        raise FileNotFoundError(
            "output/screener_company_snapshot.csv not found. "
            "Run python run_screener.py first."
        )

    dataframe = pd.read_csv(
        SNAPSHOT_PATH
    )

    pe = numeric(
        dataframe,
        "pe_ratio"
    )

    pb = numeric(
        dataframe,
        "pb_ratio"
    )

    debt = numeric(
        dataframe,
        "debt_to_equity"
    )

    dividend_yield = numeric(
        dataframe,
        "dividend_yield_pct"
    )

    roe = numeric(
        dataframe,
        "return_on_equity_pct"
    )

    sales = numeric(
        dataframe,
        "sales"
    )

    print()
    print("SPRINT 3 PRESET DIAGNOSTIC")
    print("=" * 90)

    print()
    print("SNAPSHOT STATUS")
    print("-" * 90)

    print("Total companies:", dataframe["company_id"].nunique())
    print("PE available:", int(pe.notna().sum()))
    print("PB available:", int(pb.notna().sum()))
    print(
        "Dividend Yield available:",
        int(dividend_yield.notna().sum())
    )
    print("Debt/Equity available:", int(debt.notna().sum()))
    print("ROE available:", int(roe.notna().sum()))
    print("Sales available:", int(sales.notna().sum()))

    print()
    print("VALUE PICK — INDIVIDUAL CONDITION COUNTS")
    print("-" * 90)

    pe_pass = pe < 20
    pb_pass = pb < 3
    dividend_pass = dividend_yield > 1

    # As per Sprint requirement, D/E maximum is skipped for Financials.
    debt_pass = (
        dataframe["broad_sector"].eq("Financials")
        | debt.lt(2)
    )

    print("P/E < 20:", int(pe_pass.sum()))
    print("P/B < 3:", int(pb_pass.sum()))
    print("Dividend Yield > 1:", int(dividend_pass.sum()))
    print(
        "D/E < 2 or Financials:",
        int(debt_pass.sum())
    )

    print(
        "P/E + P/B:",
        int((pe_pass & pb_pass).sum())
    )

    print(
        "P/E + P/B + D/E:",
        int(
            (
                pe_pass
                & pb_pass
                & debt_pass
            ).sum()
        )
    )

    value_pick_mask = (
        pe_pass
        & pb_pass
        & debt_pass
        & dividend_pass
    )

    print(
        "Exact Value Pick:",
        int(value_pick_mask.sum())
    )

    value_pick = dataframe[
        value_pick_mask
    ].copy()

    print_company_list(
        "EXACT VALUE PICK COMPANIES",
        value_pick,
        [
            "company_id",
            "company_name",
            "broad_sector",
            "pe_ratio",
            "pb_ratio",
            "debt_to_equity",
            "dividend_yield_pct"
        ]
    )

    print()
    print("DEBT-FREE BLUE CHIP — INDIVIDUAL CONDITION COUNTS")
    print("-" * 90)

    debt_free_pass = debt.eq(0)
    roe_pass = roe > 12
    sales_pass = sales > 5000

    print("D/E = 0:", int(debt_free_pass.sum()))
    print("ROE > 12:", int(roe_pass.sum()))
    print("Sales > 5000:", int(sales_pass.sum()))

    print(
        "D/E = 0 + ROE > 12:",
        int(
            (
                debt_free_pass
                & roe_pass
            ).sum()
        )
    )

    debt_free_blue_chip_mask = (
        debt_free_pass
        & roe_pass
        & sales_pass
    )

    print(
        "Exact Debt-Free Blue Chip:",
        int(
            debt_free_blue_chip_mask.sum()
        )
    )

    debt_free_blue_chip = dataframe[
        debt_free_blue_chip_mask
    ].copy()

    print_company_list(
        "EXACT DEBT-FREE BLUE CHIP COMPANIES",
        debt_free_blue_chip,
        [
            "company_id",
            "company_name",
            "broad_sector",
            "debt_to_equity",
            "return_on_equity_pct",
            "sales"
        ]
    )

    print()
    print("NEAR-MATCH VALUE PICK COMPANIES")
    print("-" * 90)

    value_near_match = dataframe[
        (
            pe_pass.astype(int)
            + pb_pass.astype(int)
            + debt_pass.astype(int)
            + dividend_pass.astype(int)
        ) >= 3
    ].copy()

    value_near_match["conditions_passed"] = (
        pe_pass.astype(int)
        + pb_pass.astype(int)
        + debt_pass.astype(int)
        + dividend_pass.astype(int)
    )

    print_company_list(
        "Companies passing at least 3 of 4 Value Pick rules",
        value_near_match,
        [
            "company_id",
            "company_name",
            "broad_sector",
            "pe_ratio",
            "pb_ratio",
            "debt_to_equity",
            "dividend_yield_pct",
            "conditions_passed"
        ]
    )

    print()
    print("NEAR-MATCH DEBT-FREE BLUE CHIP COMPANIES")
    print("-" * 90)

    debt_near_match = dataframe[
        (
            debt_free_pass.astype(int)
            + roe_pass.astype(int)
            + sales_pass.astype(int)
        ) >= 2
    ].copy()

    debt_near_match["conditions_passed"] = (
        debt_free_pass.astype(int)
        + roe_pass.astype(int)
        + sales_pass.astype(int)
    )

    print_company_list(
        "Companies passing at least 2 of 3 Debt-Free Blue Chip rules",
        debt_near_match,
        [
            "company_id",
            "company_name",
            "broad_sector",
            "debt_to_equity",
            "return_on_equity_pct",
            "sales",
            "conditions_passed"
        ]
    )


if __name__ == "__main__":
    main()