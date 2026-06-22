import pandas as pd
from pathlib import Path


def test_kpi_master_exists():
    assert Path("data/processed/kpi_master.csv").exists()


def test_health_score_column_exists():
    df = pd.read_csv("data/processed/kpi_master.csv")
    assert "health_score" in df.columns


def test_screener_exists():
    assert Path("data/processed/quality_growth_screener.csv").exists()


def test_reports_generated():
    assert Path("reports/generated").exists()


def test_radar_charts_generated():
    assert Path("reports/radar_charts").exists()