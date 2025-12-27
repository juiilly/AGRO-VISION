import React, { useState, useEffect } from "react";
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  CircularProgress,
} from "@mui/material";
import {
  geocodeCity,
  fetchWeather,
  predictHealth,
  predictPrice,
  getRecentPrices,
  trainModels,
} from "../api";
import CropSelector from "../components/CropSelector";
import WeatherCard from "../components/WeatherCard";
import PredictionPanel from "../components/PredictionPanel";
import MapDisplay from "../components/MapDisplay";
import PriceChart from "../PriceChart";
import RetrainStatus from "../RetrainStatus";
import SupplyAnalytics from "../SupplyAnalytics";

export default function Dashboard({ user }) {
  const [city, setCity] = useState("Mumbai");
  const [crop, setCrop] = useState("wheat");
  const [geo, setGeo] = useState(null);
  const [weather, setWeather] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    (async () => {
      const r = await getRecentPrices("wheat");
      setRecent(r || []);
    })();
  }, []);

  const handlePredict = async () => {
    setLoading(true);
    try {
      const g = await geocodeCity(city);
      setGeo(g);
      const w = await fetchWeather(g.lat, g.lon);
      setWeather(w);

      const features = {
        ndvi: 0.62,
        evi: 0.45,
        soil_moisture: 0.23,
        pest_index: 0.2,
        temp_max: w.daily.temperature_2m_max.slice(-1)[0],
        temp_min: w.daily.temperature_2m_min.slice(-1)[0],
        precip_mm: w.daily.precipitation_sum.slice(-1)[0],
        humidity: 50,
        wind_speed: w.daily.windspeed_10m_max.slice(-1)[0],
      };

      const h = await predictHealth(features);
      const p = await predictPrice(crop, recent, features);

      setPrediction({
        health: h.label,
        probability: h.probability,
        price: p.price,
      });
    } catch (e) {
      console.error(e);
      alert("Error fetching predictions");
    }
    setLoading(false);
  };

  const handleTrain = async () => {
    setLoading(true);
    await trainModels();
    alert("✅ Models retrained successfully!");
    setLoading(false);
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 3, mb: 5 }}>
      {/* HEADER */}
      <Card
        sx={{
          mb: 3,
          background: "linear-gradient(to right, #43cea2, #185a9d)",
          color: "white",
          boxShadow: 3,
        }}
      >
        <CardContent
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <Typography variant="h4" fontWeight="bold">
              🌾 AGRO-VISION Dashboard
            </Typography>
            <Typography variant="subtitle1">
              Welcome {user?.email || "User"}
            </Typography>
          </div>
          <div>
            <Button
              variant="contained"
              sx={{ mr: 2, background: "#fbc02d", color: "#000" }}
              onClick={handleTrain}
            >
              🔁 Retrain Models
            </Button>
            <Button
              variant="contained"
              sx={{ background: "#1b5e20" }}
              onClick={() => (window.location.href = "/about")}
            >
              ℹ️ About
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* INPUT PANEL */}
      <Card sx={{ mb: 3, p: 2, boxShadow: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={5}>
            <TextField
              fullWidth
              label="Enter City"
              value={city}
              onChange={(e) => setCity(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <CropSelector crop={crop} setCrop={setCrop} />
          </Grid>
          <Grid item xs={12} md={4}>
            <Button
              variant="contained"
              fullWidth
              sx={{ background: "#1976d2" }}
              onClick={handlePredict}
              disabled={loading}
            >
              {loading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                "🚀 Get Predictions"
              )}
            </Button>
          </Grid>
        </Grid>
      </Card>

      {/* DASHBOARD GRID */}
      <Grid container spacing={3}>
        {/* LEFT COLUMN */}
        <Grid item xs={12} md={6}>
          <WeatherCard weather={weather} city={city} />
          <div style={{ height: 20 }} />
          {geo && <MapDisplay lat={geo.lat} lon={geo.lon} />}
          <div style={{ height: 20 }} />
          <RetrainStatus />
        </Grid>

        {/* RIGHT COLUMN */}
        <Grid item xs={12} md={6}>
          <PredictionPanel prediction={prediction} />
          <div style={{ height: 20 }} />
          <PriceChart crop={crop} />
          <div style={{ height: 20 }} />
          {/* ✅ Pass city dynamically to SupplyAnalytics */}
          <SupplyAnalytics city={city || "ALL"} />
        </Grid>
      </Grid>

      {/* FOOTER */}
      <Card sx={{ mt: 4, background: "#f5f5f5", p: 2, textAlign: "center" }}>
        <Typography variant="body2">
          © 2025 AGRO-VISION — AI-Driven Crop Health, Price Forecasting & Supply
          Chain Insights
        </Typography>
      </Card>
    </Container>
  );
}
