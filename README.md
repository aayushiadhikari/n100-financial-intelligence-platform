# N100 Financial Intelligence Platform

## Overview

N100 Financial Intelligence Platform is a financial analytics system built for all Nifty 100 companies.

The platform performs:

- ETL Pipeline
- Data Validation
- SQLite Data Warehouse
- Financial KPI Engine
- Company Health Scoring
- Sector Analytics
- Peer Group Analysis
- Investment Screeners
- Interactive Streamlit Dashboard

---

## Project Statistics

- Companies: 90+
- Records: 1000+
- KPIs: 36
- Sectors: 10
- Reports Generated: Multiple CSV Outputs
- Database: SQLite

---

## Folder Structure

```text
data/
│
├── raw/
├── processed/
├── db/
│
reports/
│
src/
├── etl/
├── analytics/
├── dashboard/
│
tests/
```

---

## ETL Pipeline

The ETL pipeline performs:

- Data loading
- Data cleaning
- Data normalization
- Duplicate removal
- Validation checks
- SQLite database loading

Files:

- loader.py
- normaliser.py
- validator.py

---

## KPI Engine

Generated KPIs include:

- ROE
- Debt to Equity
- Free Cash Flow
- EPS
- Book Value
- Market Cap
- PE Ratio
- PB Ratio

Output:

```text
data/processed/kpi_master.csv
```

---

## Health Score Model

Health score range:

- 80-100 = Excellent
- 65-79 = Good
- 50-64 = Average
- 35-49 = Weak
- 0-34 = Poor

---

## Sector Analytics

Outputs:

- sector_summary.csv
- sector_leaders.csv

---

## Investment Screeners

Available Screeners:

- Quality Growth
- Debt Free
- High ROE
- Low Debt
- Strong Cashflow
- Value Screener

Outputs stored in:

```text
data/processed/
```

---

## Peer Analysis

Outputs:

- peer_summary.csv
- top_20_companies.csv
- bottom_20_companies.csv

---

## Streamlit Dashboard

Pages:

### Overview

- Company Count
- KPI Count
- Health Band Distribution
- Top Companies

### Company View

- Company KPIs
- Health Score
- Historical Data

### Sector Analytics

- Sector Rankings
- Average Health Scores

### Screeners

- Quality Growth
- Debt Free
- High ROE
- Low Debt
- Strong Cashflow

### Peer Analysis

- Peer Summary
- Sector Leaders

---

## Dashboard Screenshots

Located in:

```text
reports/
```

Files:

- dashboard_overview_top.png
- dashboard_overview_bottom.png
- dashboard_company_view_top.png
- dashboard_company_view_bottom.png
- dashboard_sector_analytics_top.png
- dashboard_sector_analytics_bottom.png
- dashboard_screeners.png
- dashboard_peer_analysis_top.png
- dashboard_peer_analysis_bottom.png

---

## How To Run

Create environment:

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

Install packages:

```bash
pip install -r requirements.txt
```

Run dashboard:

```bash
streamlit run src/dashboard/app.py
```

---

## Tech Stack

- Python
- Pandas
- NumPy
- SQLite
- Streamlit
- Plotly
- OpenPyXL

---

## Author

Aayushi Adhikari

B.Tech CSE (AI & ML)

N100 Financial Intelligence Platform