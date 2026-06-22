import pandas as pd
from pathlib import Path

PROCESSED_PATH = Path("data/processed")


def generate_pros_cons():

    df = pd.read_csv(PROCESSED_PATH / "kpi_master.csv")

    rows = []

    for _, row in df.iterrows():

        company_id = row.get("company_id")
        company_name = row.get("company_name")
        year = row.get("year")

        roe = row.get("return_on_equity_pct_final", 0)
        debt = row.get("debt_to_equity_final", 0)
        fcf = row.get("free_cash_flow_cr_final", 0)
        opm = row.get("operating_profit_margin_pct_final", 0)
        health = row.get("health_score", 0)

        if pd.notna(roe) and roe >= 20:
            rows.append([
                company_id,
                company_name,
                year,
                "PRO",
                "High return on equity indicates strong profitability."
            ])

        if pd.notna(debt) and debt == 0:
            rows.append([
                company_id,
                company_name,
                year,
                "PRO",
                "Debt-free balance sheet improves financial stability."
            ])

        if pd.notna(fcf) and fcf > 0:
            rows.append([
                company_id,
                company_name,
                year,
                "PRO",
                "Positive free cash flow indicates healthy cash generation."
            ])

        if pd.notna(opm) and opm >= 20:
            rows.append([
                company_id,
                company_name,
                year,
                "PRO",
                "Strong operating margin shows good operational efficiency."
            ])

        if pd.notna(health) and health >= 65:
            rows.append([
                company_id,
                company_name,
                year,
                "PRO",
                "Good financial health score indicates overall strength."
            ])

        if pd.notna(debt) and debt > 2:
            rows.append([
                company_id,
                company_name,
                year,
                "CON",
                "High debt-to-equity ratio indicates leverage risk."
            ])

        if pd.notna(fcf) and fcf < 0:
            rows.append([
                company_id,
                company_name,
                year,
                "CON",
                "Negative free cash flow may indicate weak cash generation."
            ])

        if pd.notna(roe) and roe < 5:
            rows.append([
                company_id,
                company_name,
                year,
                "CON",
                "Low return on equity indicates weak profitability."
            ])

        if pd.notna(health) and health < 35:
            rows.append([
                company_id,
                company_name,
                year,
                "CON",
                "Poor financial health score indicates higher risk."
            ])

    output = pd.DataFrame(
        rows,
        columns=[
            "company_id",
            "company_name",
            "year",
            "type",
            "insight"
        ]
    )

    output.to_csv(
        PROCESSED_PATH / "pros_cons_generated.csv",
        index=False
    )

    print("pros_cons_generated.csv generated")
    print("Total generated insights:", len(output))


if __name__ == "__main__":
    generate_pros_cons()