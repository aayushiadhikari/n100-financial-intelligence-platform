import pandas as pd


def normalize_ticker(value):
    """
    Normalize company ticker symbols.
    Example:
    ' tcs ' -> 'TCS'
    'INFY.NS' -> 'INFY'
    """
    if pd.isna(value):
        return value

    value = str(value).strip().upper()
    value = value.replace(".NS", "")
    value = value.replace(".BO", "")
    return value


def normalize_year(value):
    """
    Normalize financial year labels.
    Example:
    'Mar-23' -> '2023-03'
    'Mar-2024' -> '2024-03'
    2024 -> '2024'
    """
    if pd.isna(value):
        return value

    value = str(value).strip()

    # If already numeric year like 2024
    if value.isdigit():
        return value

    try:
        parsed = pd.to_datetime(value, format="%b-%y", errors="coerce")
        if pd.notna(parsed):
            return parsed.strftime("%Y-%m")
    except Exception:
        pass

    try:
        parsed = pd.to_datetime(value, errors="coerce")
        if pd.notna(parsed):
            return parsed.strftime("%Y-%m")
    except Exception:
        pass

    return value


def clean_dataframe(df, ticker_column="company_id", year_column="year"):
    """
    Apply common cleaning rules to all loaded datasets.
    """
    df = df.copy()

    df.columns = [str(col).strip() for col in df.columns]

    if ticker_column in df.columns:
        df[ticker_column] = df[ticker_column].apply(normalize_ticker)

    if year_column in df.columns:
        df[year_column] = df[year_column].apply(normalize_year)

    # documents.xlsx has 'Year' capital Y
    if "Year" in df.columns:
        df["Year"] = df["Year"].apply(normalize_year)

    return df