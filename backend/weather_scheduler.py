import schedule, time, datetime, requests, pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[0]
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(exist_ok=True)

def fetch_weather(lat, lon, region_name="unknown"):
    """Fetch daily forecast for the past 7 days and next 7 days."""
    print(f"Fetching weather for {region_name} ({lat},{lon})")
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
        "past_days": 7,
        "forecast_days": 7,
        "timezone": "auto"
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    j = r.json()
    daily = j["daily"]
    df = pd.DataFrame({
        "region": region_name,
        "date": pd.to_datetime(daily["time"]),
        "temp_max": daily["temperature_2m_max"],
        "temp_min": daily["temperature_2m_min"],
        "precip_mm": daily["precipitation_sum"],
        "wind_speed": daily["windspeed_10m_max"],
    })
    path = DATA_DIR / f"weather_{region_name}.csv"
    df.to_csv(path, index=False)
    print(f"✅ Weather saved to {path}")

# --- Schedule updates ---
def job():
    fetch_weather(19.0760, 72.8777, "mumbai")
    fetch_weather(26.8467, 80.9462, "lucknow")
    fetch_weather(23.2599, 77.4126, "bhopal")

if __name__ == "__main__":
    job()  # run once immediately
    schedule.every(24).hours.do(job)
    print("🌤 Weather scheduler running...")
    while True:
        schedule.run_pending()
        time.sleep(60)
