# backend/data_prep.py
# Loads the raw price CSV and weather CSV, merges them by date, creates lag features for price forecasting.

import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data"

def load_prices(path=None):
    if path is None:
        path = DATA_DIR / "market_prices_real.csv"
    return pd.read_csv(path, parse_dates=["date"])

def load_weather(path=None):
    if path is None:
        path = DATA_DIR / "weather_recent.csv"
    df = pd.read_csv(path, parse_dates=["date"])
    return df

def merge_prices_weather(prices_df, weather_df):
    """
    Merge by date; prices may be daily or monthly. We'll merge on exact date.
    If weather has daily rows and prices are monthly, consider resampling weather to price dates.
    """
    # Ensure date columns are datetime.date
    prices_df = prices_df.copy()
    weather_df = weather_df.copy()
    prices_df["date"] = pd.to_datetime(prices_df["date"]).dt.date
    weather_df["date"] = pd.to_datetime(weather_df["date"]).dt.date

    merged = prices_df.merge(weather_df, on="date", how="left")
    return merged

def make_price_lags(df, n_lags=7):
    """
    For each commodity, create lag_1..lag_n features of price.
    """
    df = df.sort_values("date").copy()
    lag_cols = []
    for lag in range(1, n_lags+1):
        col = f"lag_{lag}"
        df[col] = df.groupby("commodity")["price"].shift(lag)
        lag_cols.append(col)
    return df.dropna(subset=lag_cols + ["price"]).reset_index(drop=True)

if __name__ == "__main__":
    prices = load_prices()
    weather = load_weather()
    merged = merge_prices_weather(prices, weather)
    merged.to_csv(DATA_DIR / "merged_prices_weather.csv", index=False)
    df_lags = make_price_lags(merged, n_lags=7)
    df_lags.to_csv(DATA_DIR / "prices_model_ready.csv", index=False)
    print("Wrote merged_prices_weather.csv and prices_model_ready.csv")
