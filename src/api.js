import axios from 'axios';
const API_BASE = 'http://127.0.0.1:5000';

export async function geocodeCity(city){
  const res = await axios.get(`${API_BASE}/api/geocode`, { params: { q: city } });
  if(res.data && res.data.length>0) return res.data[0];
  return null;
}

export async function fetchWeather(lat, lon){
  const res = await axios.get(`${API_BASE}/api/weather`, { params: { lat, lon } });
  return res.data;
}

export async function predictHealth(features){
  const res = await axios.post(`${API_BASE}/api/predict/health`, features);
  return res.data;
}

export async function predictPrice(crop, recent_prices, weather){
  const res = await axios.post(`${API_BASE}/api/predict/price`, { crop, recent_prices, weather });
  return res.data;
}

export async function getRecentPrices(crop){
  const res = await axios.get(`${API_BASE}/api/prices`);
  return res.data;
}

export async function trainModels(){
  const res = await axios.post(`${API_BASE}/api/train`);
  return res.data;
}

// --- Supply Chain ---
export async function getSupplyAllocations(demand) {
  const res = await fetch("http://127.0.0.1:5000/api/supply", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ demand }),
  });
  if (!res.ok) throw new Error("Failed to fetch supply allocation");
  return await res.json();
}
