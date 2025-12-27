# backend/train_price_model.py
# Trains one RandomForestRegressor per commodity using lag features + weather features.
# Saves models to backend/models/

import pandas as pd, joblib
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data"
MODELS_DIR = BASE / "models"
MODELS_DIR.mkdir(exist_ok=True)

def train_all_crops(input_csv=None, n_lags=7):
    if input_csv is None:
        input_csv = DATA_DIR / "prices_model_ready.csv"
    df = pd.read_csv(input_csv, parse_dates=["date"])
    # features: lag_1..lag_n + weather features
    lag_cols = [f"lag_{i}" for i in range(1, n_lags+1)]
    weather_feats = ["temp_max", "temp_min", "precip_mm", "wind_speed"]
    results = {}
    for crop in df["commodity"].unique():
        sub = df[df["commodity"] == crop].dropna(subset=lag_cols + weather_feats + ["price"])
        if len(sub) < 50:
            print(f"Skipping {crop} - not enough rows ({len(sub)})")
            continue
        X = sub[lag_cols + weather_feats]
        y = sub["price"]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        print(f"Trained {crop}: MAE = {mae:.2f} ({len(sub)} rows)")
        joblib.dump(model, MODELS_DIR / f"price_rf_{crop.replace(' ','_')}.joblib")
        results[crop] = {"mae": mae, "rows": len(sub)}
    return results

if __name__ == "__main__":
    res = train_all_crops()
    print("Training complete:", res)
