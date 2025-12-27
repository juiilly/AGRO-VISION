import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[0]
DATA_DIR = BASE / "data"

def analyze_supply_chain():
    supply = pd.read_csv(DATA_DIR / "supply.csv")
    demand = pd.read_csv(DATA_DIR / "demand.csv")
    merged = pd.merge(supply, demand, on="region", how="outer").fillna(0)
    merged["deficit"] = merged["demand"] - merged["capacity"]
    merged["status"] = merged["deficit"].apply(lambda x: "surplus" if x < 0 else "deficit")
    summary = merged.groupby("status")["region"].count().to_dict()
    print("🚚 Supply chain summary:", summary)
    merged.to_csv(DATA_DIR / "supply_analysis.csv", index=False)
    return merged

if __name__ == "__main__":
    df = analyze_supply_chain()
    print(df.head())
