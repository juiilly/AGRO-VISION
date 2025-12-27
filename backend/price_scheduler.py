# backend/price_scheduler.py
# Optional: run as a service or with screen/tmux to update data daily and retrain models.

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import date
from pathlib import Path
from backend.data_ingest import fetch_weather_for_coords, save_weather, fetch_prices_agmarknet, save_prices
from backend.data_prep import merge_prices_weather, make_price_lags
from backend.train_price_model import train_all_crops

# configure here
LAT = 19.0760
LON = 72.8777
COMMODITY = "Wheat"

def job_daily_update():
    print("Daily job start -", date.today().isoformat())
    try:
        # fetch last 365 days weather for sample coords
        w = fetch_weather_for_coords(LAT, LON, days=365)
        save_weather(w)
    except Exception as e:
        print("Weather fetch error:", e)
    try:
        # attempt agmarknet fetch (best effort)
        p = fetch_prices_agmarknet(COMMODITY)
        save_prices(p)
    except Exception as e:
        print("Agmarknet fetch failed:", e)
    # prepare and train (you can call the other scripts or functions)
    try:
        import backend.data_prep as dp
        prices = dp.load_prices()
        weather = dp.load_weather()
        merged = dp.merge_prices_weather(prices, weather)
        merged.to_csv(Path("backend/data/merged_prices_weather.csv"), index=False)
        df_lags = dp.make_price_lags(merged, n_lags=7)
        df_lags.to_csv(Path("backend/data/prices_model_ready.csv"), index=False)
        train_all_crops(input_csv=Path("backend/data/prices_model_ready.csv"))
        print("Daily update done.")
    except Exception as e:
        print("Prepare/train step failed:", e)

if __name__ == "__main__":
    sched = BlockingScheduler()
    sched.add_job(job_daily_update, "interval", days=1, next_run_time=None)
    print("Scheduler started (daily job).")
    sched.start()
