import pandas as pd


COMPANY_YEAR_TABLES = {
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "financial_ratios.xlsx",
    "market_cap.xlsx",
}


def check_null_company_id(df, table_name):
    failures = []

    if "company_id" in df.columns:
        bad_rows = df[df["company_id"].isna()]

        for _, row in bad_rows.iterrows():
            failures.append({
                "table": table_name,
                "company_id": "",
                "year": "",
                "issue": "NULL_COMPANY_ID",
                "severity": "CRITICAL"
            })

    return failures


def check_duplicate_company_year(df, table_name):
    failures = []

    if table_name not in COMPANY_YEAR_TABLES:
        return failures

    if "company_id" in df.columns and "year" in df.columns:
        duplicates = df[
            df.duplicated(
                subset=["company_id", "year"],
                keep=False
            )
        ]

        for _, row in duplicates.iterrows():
            failures.append({
                "table": table_name,
                "company_id": row.get("company_id", ""),
                "year": row.get("year", ""),
                "issue": "DUPLICATE_COMPANY_YEAR",
                "severity": "CRITICAL"
            })

    return failures


def check_positive_sales(df, table_name):
    failures = []

    if table_name != "profitandloss.xlsx":
        return failures

    if "sales" in df.columns:
        bad_rows = df[df["sales"] <= 0]

        for _, row in bad_rows.iterrows():
            failures.append({
                "table": table_name,
                "company_id": row.get("company_id", ""),
                "year": row.get("year", ""),
                "issue": "SALES_NOT_POSITIVE",
                "severity": "WARNING"
            })

    return failures


def check_balance_sheet_balance(df, table_name):
    failures = []

    if table_name != "balancesheet.xlsx":
        return failures

    required_cols = {"total_assets", "total_liabilities"}

    if not required_cols.issubset(df.columns):
        return failures

    temp = df.copy()
    temp["diff_pct"] = (
        (temp["total_assets"] - temp["total_liabilities"]).abs()
        / temp["total_assets"].replace(0, pd.NA)
    ) * 100

    bad_rows = temp[temp["diff_pct"] > 1]

    for _, row in bad_rows.iterrows():
        failures.append({
            "table": table_name,
            "company_id": row.get("company_id", ""),
            "year": row.get("year", ""),
            "issue": "BALANCE_SHEET_NOT_BALANCED",
            "severity": "WARNING"
        })

    return failures


def validate_dataframe(df, table_name):
    failures = []

    failures.extend(check_null_company_id(df, table_name))
    failures.extend(check_duplicate_company_year(df, table_name))
    failures.extend(check_positive_sales(df, table_name))
    failures.extend(check_balance_sheet_balance(df, table_name))

    return failures