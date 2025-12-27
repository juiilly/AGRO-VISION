import React from 'react';

export default function WeatherCard({ weather, city }){
  if(!weather) return <div className="small">No live weather (locate a city and press predict)</div>;
  // display summary using Open-Meteo daily fields
  const d = weather.daily;
  const lastIdx = d.time.length - 1;
  return (
    <div style={{display:'flex',gap:12,alignItems:'center'}}>
      <div style={{flex:1}}>
        <div className="small">Location</div>
        <div style={{fontWeight:700}}>{city}</div>
        <div className="small" style={{marginTop:8}}>Date: {d.time[lastIdx]}</div>
      </div>
      <div style={{minWidth:140}}>
        <div className="small">🌡️ Temp (max): {d.temperature_2m_max[lastIdx]} °C</div>
        <div className="small">🌧️ Precip: {d.precipitation_sum[lastIdx]} mm</div>
        <div className="small">🌬️ Wind: {d.windspeed_10m_max[lastIdx]} m/s</div>
      </div>
    </div>
  );
}