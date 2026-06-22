from pathlib import Path
from datetime import datetime
import sqlite3
import pandas as pd

from normaliser import clean_dataframe
from validator import validate_dataframe


RAW_DATA_PATH = Path("data/raw")
OUTPUT_PATH = Path("output")
DATABASE_PATH = Path("data/db/nifty100.db")
SCHEMA_PATH = Path("db/schema.sql")

CORE_FILES = {
    "companies.xlsx",
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "analysis.xlsx",
    "documents.xlsx",
    "prosandcons.xlsx",
}

COMPANY_YEAR_TABLES = {
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "financial_ratios.xlsx",
    "market_cap.xlsx",
}

FILE_TABLE_MAP = {
    "companies.xlsx": "companies",
    "profitandloss.xlsx": "profitandloss",
    "balancesheet.xlsx": "balancesheet",
    "cashflow.xlsx": "cashflow",
    "analysis.xlsx": "analysis",
    "documents.xlsx": "documents",
    "prosandcons.xlsx": "prosandcons",
    "sectors.xlsx": "sectors",
    "financial_ratios.xlsx": "financial_ratios",
    "market_cap.xlsx": "market_cap",
    "peer_groups.xlsx": "peer_groups",
    "stock_prices.xlsx": "stock_prices",
}

LOAD_ORDER = [
    "companies.xlsx",
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "analysis.xlsx",
    "documents.xlsx",
    "prosandcons.xlsx",
    "sectors.xlsx",
    "financial_ratios.xlsx",
    "market_cap.xlsx",
    "peer_groups.xlsx",
    "stock_prices.xlsx",
]

VALID_COMPANY_IDS = set()


def read_excel_file(file_path: Path) -> pd.DataFrame:
    if file_path.name in CORE_FILES:
        return pd.read_excel(file_path, header=1)
    return pd.read_excel(file_path, header=0)


def remove_duplicates(df: pd.DataFrame, file_name: str) -> pd.DataFrame:
    df = df.drop_duplicates()

    if file_name in COMPANY_YEAR_TABLES:
        if "company_id" in df.columns and "year" in df.columns:
            df = df.drop_duplicates(
                subset=["company_id", "year"],
                keep="first"
            )

    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    rename_map = {
        "Year": "year",
        "Annual_Report": "annual_report",
    }

    df = df.rename(columns=rename_map)
    df.columns = [str(col).strip().lower() for col in df.columns]

    return df


def filter_invalid_company_ids(df: pd.DataFrame, file_name: str) -> tuple[pd.DataFrame, int]:
    if file_name == "companies.xlsx":
        return df, 0

    if "company_id" not in df.columns:
        return df, 0

    before = len(df)
    df = df[df["company_id"].isin(VALID_COMPANY_IDS)].copy()
    rejected = before - len(df)

    return df, rejected


def create_database():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

    connection = sqlite3.connect(DATABASE_PATH)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
        schema_sql = file.read()

    connection.executescript(schema_sql)
    connection.commit()
    connection.close()


def load_table_to_database(df: pd.DataFrame, table_name: str):
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON;")

    df.to_sql(
        table_name,
        connection,
        if_exists="append",
        index=False
    )

    connection.commit()
    connection.close()


def main():
    global VALID_COMPANY_IDS

    OUTPUT_PATH.mkdir(exist_ok=True)
    create_database()

    audit_rows = []
    all_failures = []

    for file_name in LOAD_ORDER:
        file = RAW_DATA_PATH / file_name

        try:
            df = read_excel_file(file)
            rows_in = df.shape[0]

            df = clean_dataframe(df)
            df = standardize_columns(df)
            df = remove_duplicates(df, file.name)

            if file.name == "companies.xlsx":
                VALID_COMPANY_IDS = set(df["id"].astype(str).str.strip().str.upper())

            df, rejected_fk_rows = filter_invalid_company_ids(df, file.name)

            rows_out = df.shape[0]

            failures = validate_dataframe(df, file.name)
            all_failures.extend(failures)

            table_name = FILE_TABLE_MAP.get(file.name)

            if table_name:
                load_table_to_database(df, table_name)
                load_status = "loaded_to_database"
            else:
                load_status = "skipped_no_table_mapping"

            audit_rows.append({
                "file_name": file.name,
                "table_name": table_name if table_name else "",
                "rows_in": rows_in,
                "rows_out": rows_out,
                "rows_removed": rows_in - rows_out,
                "fk_rejected_rows": rejected_fk_rows,
                "columns": df.shape[1],
                "column_names": ", ".join(df.columns.astype(str)),
                "status": load_status,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        except Exception as error:
            audit_rows.append({
                "file_name": file.name,
                "table_name": FILE_TABLE_MAP.get(file.name, ""),
                "rows_in": 0,
                "rows_out": 0,
                "rows_removed": 0,
                "fk_rejected_rows": 0,
                "columns": 0,
                "column_names": "",
                "status": f"failed: {error}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            all_failures.append({
                "table": file.name,
                "company_id": "",
                "year": "",
                "issue": str(error),
                "severity": "CRITICAL"
            })

    audit_df = pd.DataFrame(audit_rows)
    audit_df.to_csv(OUTPUT_PATH / "load_audit.csv", index=False)

    failure_df = pd.DataFrame(all_failures)

    if failure_df.empty:
        failure_df = pd.DataFrame(
            columns=["table", "company_id", "year", "issue", "severity"]
        )

    failure_df.to_csv(OUTPUT_PATH / "validation_failures.csv", index=False)

    print("Database created successfully:", DATABASE_PATH)
    print("load_audit.csv generated successfully.")
    print("validation_failures.csv generated successfully.")
    print()
    print(
        audit_df[
            [
                "file_name",
                "table_name",
                "rows_in",
                "rows_out",
                "rows_removed",
                "fk_rejected_rows",
                "status",
            ]
        ]
    )
    print()
    print(f"Validation Failures: {len(all_failures)}")


if __name__ == "__main__":
    main()