import schedule
import time
import pandas as pd
import os
import json
from pathlib import Path
from datetime import datetime

# Import core modules
from backend.data_prep import merge_prices_weather, make_price_lags
from backend.train_price_model import train_all_crops
from backend.data_ingest import (
    fetch_prices_csv,
    fetch_weather_for_coords,
    save_prices,
    save_weather,
)

# --- Paths ---
BASE = Path(__file__).resolve().parents[0]
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(exist_ok=True)
STATUS_FILE = DATA_DIR / "retrain_status.json"

# --- Coordinates for fallback weather fetch (Mumbai default) ---
DEFAULT_LAT, DEFAULT_LON = 19.0760, 72.8777


def log_status(status: str, error: str = None):
    """Save retraining status and timestamp for frontend dashboard."""
    data = {
        "last_run": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status if not error else f"failed: {error}",
    }
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def ensure_datasets():
    """Ensure both price and weather data exist. Auto-fetch if missing."""
    price_path = DATA_DIR / "market_prices_real.csv"
    weather_path = DATA_DIR / "weather_recent.csv"

    # ✅ Ensure price dataset
    if not price_path.exists():
        print("⚠️  Price dataset not found — attempting fallback load...")
        csv_path = BASE / "Agriculture_price_dataset.csv"
        if csv_path.exists():
            dfp = fetch_prices_csv(str(csv_path))
            save_prices(dfp)
        else:
            raise FileNotFoundError("❌ Missing both market_prices_real.csv and fallback CSV!")

    # ✅ Ensure weather dataset
    if not weather_path.exists():
        print("🌦  Weather dataset missing — fetching from Open-Meteo API...")
        dfw = fetch_weather_for_coords(DEFAULT_LAT, DEFAULT_LON, days=365)
        save_weather(dfw)


def retrain_models():
    """Main retraining process — merges, trains and updates status."""
    try:
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n📈 Starting model retraining at {start_time} ...")

        ensure_datasets()

        # Load datasets
        prices = pd.read_csv(DATA_DIR / "market_prices_real.csv", parse_dates=["date"])
        weather_files = list(DATA_DIR.glob("weather_*.csv"))
        if not weather_files:
            weather_files = [DATA_DIR / "weather_recent.csv"]

        weather = pd.concat(
            [pd.read_csv(f, parse_dates=["date"]) for f in weather_files],
            ignore_index=True,
        )

        # Merge and prepare model dataset
        merged = merge_prices_weather(prices, weather)
        df_lags = make_price_lags(merged, n_lags=7)
        df_lags.to_csv(DATA_DIR / "prices_model_ready.csv", index=False)

        # Train models
        train_all_crops(input_csv=DATA_DIR / "prices_model_ready.csv")

        print("✅ Model retraining complete!")
        log_status("success")

    except Exception as e:
        print(f"❌ Retraining failed: {e}")
        log_status("failed", str(e))

def ensure_datasets():
    """Ensure both price and weather data exist before training."""
    price_path = DATA_DIR / "market_prices_real.csv"
    weather_path = DATA_DIR / "weather_recent.csv"

    if not price_path.exists():
        print("⚠️  Price dataset not found — generating fallback CSV...")
        from backend.data_ingest import fetch_prices_csv, save_prices
        dfp = fetch_prices_csv(BASE / "Agriculture_price_dataset.csv")
        save_prices(dfp)

    if not weather_path.exists():
        print("🌦  Weather dataset missing — fetching via Open-Meteo API...")
        from backend.data_ingest import fetch_weather_for_coords, save_weather
        dfw = fetch_weather_for_coords(19.0760, 72.8777, days=365)
        save_weather(dfw)



if __name__ == "__main__":
    print("🕒 Retraining scheduler active (runs weekly)...")
    retrain_models()  # Run immediately once on startup
    schedule.every().week.do(retrain_models)

    while True:
        schedule.run_pending()
        time.sleep(60)
