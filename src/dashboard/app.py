import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="N100 Financial Intelligence Platform",
    page_icon="📈",
    layout="wide"
)

DATA_PATH = Path("data/processed")

kpi = pd.read_csv(DATA_PATH / "kpi_master.csv")

st.title("📈 N100 Financial Intelligence Platform")
st.markdown("---")

page = st.sidebar.selectbox(
    "Navigation",
    [
        "Overview",
        "Company View",
        "Sector Analytics",
        "Screeners",
        "Peer Analysis"
    ]
)

if page == "Overview":
    st.header("Platform Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Companies", kpi["company_id"].nunique())
    col2.metric("Records", len(kpi))
    col3.metric("KPIs", 36)
    col4.metric("Sectors", kpi["broad_sector"].nunique())

    st.markdown("---")

    st.subheader("Health Band Distribution")

    health_counts = (
        kpi["health_band"]
        .value_counts()
        .reset_index()
    )

    health_counts.columns = ["health_band", "count"]

    fig = px.bar(
        health_counts,
        x="health_band",
        y="count",
        title="Health Band Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 10 Companies by Health Score")

    top10 = (
        kpi.sort_values("health_score", ascending=False)
        .head(10)
    )

    st.dataframe(
        top10[
            [
                "company_id",
                "company_name",
                "year",
                "health_score",
                "health_band"
            ]
        ],
        use_container_width=True
    )

elif page == "Company View":
    st.header("Company Analysis")

    company = st.selectbox(
        "Select Company",
        sorted(kpi["company_name"].dropna().unique())
    )

    company_df = kpi[kpi["company_name"] == company].copy()
    company_df = company_df.sort_values("year")

    latest = company_df.iloc[-1]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Health Score", round(latest["health_score"], 2))
    col2.metric("ROE %", round(latest["return_on_equity_pct_final"], 2))
    col3.metric("Debt/Equity", round(latest["debt_to_equity_final"], 2))
    col4.metric("FCF Cr", round(latest["free_cash_flow_cr_final"], 2))

    st.markdown("---")

    st.subheader("Health Score Trend")

    fig = px.line(
        company_df,
        x="year",
        y="health_score",
        title=f"Health Score Trend - {company}",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Historical KPI Data")

    st.dataframe(company_df, use_container_width=True)

elif page == "Sector Analytics":
    st.header("Sector Analytics")

    sector_summary = pd.read_csv(DATA_PATH / "sector_summary.csv")

    st.dataframe(sector_summary, use_container_width=True)

    if "health_score" in sector_summary.columns:
        y_col = "health_score"
    else:
        y_col = "avg_health_score"

    fig = px.bar(
        sector_summary,
        x="broad_sector",
        y=y_col,
        title="Average Health Score by Sector"
    )

    st.plotly_chart(fig, use_container_width=True)

elif page == "Screeners":
    st.header("Investment Screeners")

    screener_file = st.selectbox(
        "Select Screener",
        [
            "quality_growth_screener.csv",
            "debt_free_screener.csv",
            "high_roe_screener.csv",
            "low_debt_screener.csv",
            "strong_cashflow_screener.csv"
        ]
    )

    screener_df = pd.read_csv(DATA_PATH / screener_file)

    st.metric("Rows Found", len(screener_df))

    st.dataframe(screener_df, use_container_width=True)

elif page == "Peer Analysis":
    st.header("Peer Analysis")

    peer = pd.read_csv(DATA_PATH / "peer_summary.csv")
    leaders = pd.read_csv(DATA_PATH / "sector_leaders.csv")

    st.subheader("Peer Summary")
    st.dataframe(peer, use_container_width=True)

    st.subheader("Sector Leaders")
    st.dataframe(leaders, use_container_width=True)