import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path("data/db/nifty100.db")
SQL_PATH = Path("notebooks/exploratory_queries.sql")
OUTPUT_PATH = Path("output/query_results.txt")

connection = sqlite3.connect(DB_PATH)

sql_text = SQL_PATH.read_text(encoding="utf-8")

queries = [
    query.strip()
    for query in sql_text.split(";")
    if query.strip()
]

results = []

for i, query in enumerate(queries, start=1):
    try:
        df = pd.read_sql_query(query, connection)
        results.append(f"\nQUERY {i}\n")
        results.append(query + ";\n")
        results.append(df.head(10).to_string(index=False))
        results.append("\n" + "-" * 80 + "\n")
    except Exception as error:
        results.append(f"\nQUERY {i} FAILED: {error}\n")

connection.close()

OUTPUT_PATH.write_text("\n".join(results), encoding="utf-8")

print("All exploratory queries executed.")
print("Results saved to output/query_results.txt")