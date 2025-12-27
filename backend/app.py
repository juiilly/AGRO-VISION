from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests, joblib, os
from pathlib import Path
import pandas as pd, numpy as np
BASE = Path(__file__).resolve().parents[0]
DATA_DIR = BASE / 'data'
MODELS_DIR = BASE / 'models'
app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app)

@app.route('/api/geocode')
def geocode():
    q = request.args.get('q')
    if not q:
        return jsonify({'error':'missing q'}),400
    url = 'https://nominatim.openstreetmap.org/search'
    r = requests.get(url, params={'q':q,'format':'json','limit':1}, headers={'User-Agent':'agro-vision'})
    return jsonify(r.json())

@app.route('/api/weather')
def weather():
    lat = request.args.get('lat'); lon = request.args.get('lon')
    if not lat or not lon: return jsonify({'error':'missing coords'}),400
    url = 'https://api.open-meteo.com/v1/forecast'
    params = {'latitude':lat,'longitude':lon,'daily':'temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max','timezone':'auto'}
    r = requests.get(url, params=params, timeout=10)
    return jsonify(r.json())

@app.route('/api/train', methods=['POST'])
def train():
    sat = pd.read_csv(DATA_DIR / 'satellite.csv', parse_dates=['date'])
    w = pd.read_csv(DATA_DIR / 'weather.csv', parse_dates=['date'])
    prices = pd.read_csv(DATA_DIR / 'prices.csv', parse_dates=['date'])
    df = sat.merge(w, on='date', how='left')
    features = ['ndvi','evi','soil_moisture','pest_index','temp_max','temp_min','precip_mm','humidity','wind_speed']
    df2 = df.dropna(subset=features)
    X = df2[features]; y = (df2['health_label']=='healthy').astype(int)
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    clf = RandomForestClassifier(n_estimators=50, random_state=42)
    clf.fit(X,y)
    joblib.dump(clf, MODELS_DIR / 'crop_health_rf.joblib')
    # prices
    def make_lags(dfprices, n=7):
        dfp = dfprices.sort_values('date').copy()
        for lag in range(1,n+1):
            dfp[f'lag_{lag}'] = dfp.groupby('crop')['price'].shift(lag)
        return dfp.dropna()
    prices_w = prices.merge(w, on='date', how='left')
    pdf = make_lags(prices_w, n=7)
    for c in pdf['crop'].unique():
        sub = pdf[pdf['crop']==c].dropna()
        feats = [f'lag_{i}' for i in range(1,8)] + ['temp_max','temp_min','precip_mm','humidity','wind_speed']
        Xp = sub[feats]; yp = sub['price']
        reg = RandomForestRegressor(n_estimators=50, random_state=42)
        reg.fit(Xp, yp)
        joblib.dump(reg, MODELS_DIR / f'price_rf_{c}.joblib')
    return jsonify({'status':'trained'})

@app.route('/api/predict/health', methods=['POST'])
def predict_health():
    data = request.json or {}
    mp = MODELS_DIR / 'crop_health_rf.joblib'
    if not mp.exists(): return jsonify({'error':'model missing'}),400
    clf = joblib.load(mp)
    keys = ['ndvi','evi','soil_moisture','pest_index','temp_max','temp_min','precip_mm','humidity','wind_speed']
    X = np.array([[data.get(k) for k in keys]])
    prob = clf.predict_proba(X)[0,1]
    label = 'healthy' if prob>0.5 else 'stressed'
    return jsonify({'label':label,'probability':float(prob)})

@app.route('/api/predict/price', methods=['POST'])
def predict_price():
    data = request.json or {}
    crop = data.get('crop'); recent = data.get('recent_prices',[]); weather = data.get('weather',{})
    mp = MODELS_DIR / f'price_rf_{crop}.joblib'
    if not mp.exists(): return jsonify({'error':'model missing'}),400
    reg = joblib.load(mp)
    n=7
    if len(recent)<n:
        recent = ([recent[0]]*(n-len(recent)))+recent if recent else [1000]*n
    lags = recent[-n:][::-1]
    row = {f'lag_{i+1}':lags[i] for i in range(n)}
    for k in ['temp_max','temp_min','precip_mm','humidity','wind_speed']:
        row[k] = weather.get(k)
    import pandas as pd
    X = pd.DataFrame([row])
    pred = reg.predict(X)[0]
    return jsonify({'price':float(pred)})

@app.route('/api/prices')
def prices():
    df = pd.read_csv(DATA_DIR / 'prices.csv')
    last = df[df['crop']=='wheat'].sort_values('date').tail(7)['price'].tolist()
    return jsonify(last)

@app.route('/api/supply', methods=['POST'])
def supply_alloc():
    data = request.json or {}
    demand = data.get('demand',{})
    df = pd.read_csv(DATA_DIR / 'supply.csv')
    df['remaining'] = df['capacity']
    alloc = []
    for region,d in demand.items():
        rem=d
        for idx,row in df.sort_values('capacity',ascending=False).iterrows():
            if rem<=0: break
            take = min(row['remaining'], rem)
            if take>0:
                alloc.append({'region':region,'warehouse':row['warehouse_id'],'allocated':int(take)})
                df.at[idx,'remaining'] -= take
                rem -= take
        if rem>0:
            alloc.append({'region':region,'warehouse':None,'allocated':int(rem),'note':'unfulfilled'})
    return jsonify({'allocations':alloc})

# serve react build
@app.route('/', defaults={'path':''})
@app.route('/<path:path>')
def serve(path):
    build = BASE.parent / 'frontend' / 'build'
    if path!="" and (build / path).exists():
        return send_from_directory(str(build), path)
    return send_from_directory(str(build), 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)