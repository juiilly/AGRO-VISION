import React, { useEffect, useState } from "react";
import { Card, CardContent, Typography } from "@mui/material";
import axios from "axios";

export default function WeatherPanel({ lat = 19.076, lon = 72.8777 }) {
  const [weather, setWeather] = useState(null);

  useEffect(() => {
    axios.get(`http://127.0.0.1:5000/api/weather?lat=${lat}&lon=${lon}`)
      .then(res => setWeather(res.data.daily))
      .catch(() => setWeather(null));
  }, [lat, lon]);

  if (!weather) return <p>Loading weather...</p>;

  return (
    <Card sx={{ boxShadow: 3, borderRadius: 3, background: "#f0fff4" }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>🌦 7-Day Weather Forecast</Typography>
        <div style={{ display: "flex", gap: "12px", overflowX: "scroll" }}>
          {weather.time.map((date, i) => (
            <div key={i} style={{ textAlign: "center", minWidth: "100px" }}>
              <Typography variant="body2">{date}</Typography>
              <Typography variant="body2">🌡 {weather.temperature_2m_max[i]}°C</Typography>
              <Typography variant="body2">💨 {weather.windspeed_10m_max[i]} km/h</Typography>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
