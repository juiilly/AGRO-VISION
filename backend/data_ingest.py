# backend/data_ingest.py
# Fetch price and weather data. Aggregates into CSV files under backend/data/
# Handles Agmarknet-style CSV or public dataset URLs.

import os
from pathlib import Path
import datetime
import requests
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(exist_ok=True)

OPEN_METEO_DAILY_PARAMS = "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max"

# --------------------------------------------------------------------------------
# WEATHER FETCH
# --------------------------------------------------------------------------------
def fetch_weather_for_coords(lat, lon, days=30):
    """
    Fetch daily weather via Open-Meteo for the last `days`.
    Uses the archive API for past data and forecast API for recent days.
    """
    import datetime, requests, pandas as pd

    end = datetime.date.today() - datetime.timedelta(days=1)  # ✅ avoid invalid end_date
    start = end - datetime.timedelta(days=days)
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "timezone": "UTC",
    }

    print(f"🌦 Fetching weather from {start} to {end}...")
    r = requests.get(url, params=params, timeout=20)

    if r.status_code != 200:
        print(f"⚠️ Archive API failed ({r.status_code}) — using forecast fallback")
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
            "forecast_days": 7,
            "timezone": "auto",
        }
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()

    j = r.json()
    daily = j.get("daily", {})
    df = pd.DataFrame({
        "date": pd.to_datetime(daily.get("time", [])),
        "temp_max": daily.get("temperature_2m_max", []),
        "temp_min": daily.get("temperature_2m_min", []),
        "precip_mm": daily.get("precipitation_sum", []),
        "wind_speed": daily.get("windspeed_10m_max", []),
    })
    df["date"] = df["date"].dt.date
    print(f"✅ Got {len(df)} weather records.")
    return df


# --------------------------------------------------------------------------------
# PRICE FETCH
# --------------------------------------------------------------------------------
def fetch_prices_csv(csv_url):
    """
    Fetch and clean agricultural market price CSV (supports Agmarknet format).
    """
    print(f"📥 Loading price data from: {csv_url}")
    df = pd.read_csv(csv_url)

    # --- Handle date column ---
    if 'date' in df.columns:
        date_col = 'date'
    elif 'Date' in df.columns:
        date_col = 'Date'
    elif 'Price Date' in df.columns:
        date_col = 'Price Date'
    elif 'PRICE DATE' in df.columns:
        date_col = 'PRICE DATE'
    else:
        print("⚠️ No 'date' column found — generating sequential dates.")
        df['date'] = pd.date_range(end=pd.Timestamp.today(), periods=len(df))
        date_col = 'date'

    df.rename(columns={date_col: 'date'}, inplace=True)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # --- Handle price column ---
    if 'Modal_Price' in df.columns:
        df.rename(columns={'Modal_Price': 'price'}, inplace=True)
    elif 'Price' in df.columns:
        df.rename(columns={'Price': 'price'}, inplace=True)
    elif 'Max_Price' in df.columns:
        df.rename(columns={'Max_Price': 'price'}, inplace=True)
    elif 'Min_Price' in df.columns:
        df.rename(columns={'Min_Price': 'price'}, inplace=True)
    else:
        raise ValueError("❌ No price-related column found in dataset!")

    # --- Handle commodity column ---
    if 'Commodity' in df.columns:
        df.rename(columns={'Commodity': 'commodity'}, inplace=True)
    elif 'Crop' in df.columns:
        df.rename(columns={'Crop': 'commodity'}, inplace=True)
    elif 'Product' in df.columns:
        df.rename(columns={'Product': 'commodity'}, inplace=True)
    else:
        df['commodity'] = "Unknown"

    # Keep only essential columns
    keep_cols = ['date', 'commodity', 'price']
    df = df[[col for col in keep_cols if col in df.columns]].dropna()

    # Clean price data
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])
    df = df.sort_values("date")

    output_path = DATA_DIR / "processed_prices.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ Cleaned price dataset saved to {output_path}")
    print(df.head())
    return df

# --------------------------------------------------------------------------------
# SAVE HELPERS
# --------------------------------------------------------------------------------
def save_prices(df, filename="market_prices_real.csv"):
    path = DATA_DIR / filename
    df.to_csv(path, index=False)
    print(f"💾 Saved prices to {path}")
    return path

def save_weather(df, filename="weather_recent.csv"):
    path = DATA_DIR / filename
    df.to_csv(path, index=False)
    print(f"💾 Saved weather to {path}")
    return path

# --------------------------------------------------------------------------------
# MAIN CLI ENTRY
# --------------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Fetch and clean agriculture data")
    parser.add_argument("--fetch-weather", nargs=2, metavar=("LAT", "LON"), help="Fetch weather for lat lon")
    parser.add_argument("--fetch-prices-csv", nargs=1, metavar=("CSV_PATH"), help="Fetch prices from CSV or URL")
    args = parser.parse_args()

    if args.fetch_weather:
        lat, lon = args.fetch_weather
        dfw = fetch_weather_for_coords(float(lat), float(lon), days=365)
        save_weather(dfw)

    if args.fetch_prices_csv:
        csv = args.fetch_prices_csv[0]
        dfp = fetch_prices_csv(csv)
        save_prices(dfp)
