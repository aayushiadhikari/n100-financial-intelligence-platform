import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path("data/db/nifty100.db")

TABLES = [
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "analysis",
    "documents",
    "prosandcons",
    "sectors",
    "financial_ratios",
    "market_cap",
    "peer_groups",
    "stock_prices",
]

connection = sqlite3.connect(DB_PATH)

print("\nDATABASE VERIFICATION\n")

for table in TABLES:
    query = f"SELECT COUNT(*) AS row_count FROM {table}"
    count = pd.read_sql_query(query, connection)["row_count"].iloc[0]
    print(f"{table:20} : {count}")

print("\nFOREIGN KEY CHECK\n")

fk_check = pd.read_sql_query("PRAGMA foreign_key_check;", connection)

if fk_check.empty:
    print("Foreign Key Check: PASSED")
else:
    print("Foreign Key Check: FAILED")
    print(fk_check)

print("\nSAMPLE COMPANIES\n")
sample = pd.read_sql_query(
    "SELECT id, company_name FROM companies LIMIT 10",
    connection
)
print(sample)

connection.close()