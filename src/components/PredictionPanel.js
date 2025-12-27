import React from "react";

export default function PredictionPanel({ prediction, selectedCrop }) {
  if (!prediction)
    return (
      <div
        className="small"
        style={{
          color: "#555",
          padding: "10px",
          textAlign: "center",
          background: "#f5f5f5",
          borderRadius: 10,
        }}
      >
        No prediction yet — click <b>“Get Predictions”</b> to see results.
      </div>
    );

  const healthColor = prediction.health === "healthy" ? "#2e7d32" : "#d32f2f";
  const healthIcon = prediction.health === "healthy" ? "✅" : "⚠️";
  const confidence = (prediction.probability * 100).toFixed(1);
  const cropName =
    selectedCrop?.charAt(0).toUpperCase() + selectedCrop?.slice(1) || "Crop";

  return (
    <div
      style={{
        background: "#ffffff",
        borderRadius: 12,
        padding: 18,
        boxShadow: "0 3px 10px rgba(0,0,0,0.1)",
      }}
    >
      {/* Crop Name */}
      <div
        style={{
          fontSize: 18,
          fontWeight: 700,
          marginBottom: 12,
          color: "#1565c0",
        }}
      >
        🌾 Prediction for <span style={{ color: "#0b8457" }}>{cropName}</span>
      </div>

      {/* Crop Health */}
      <div
        style={{
          background: healthColor,
          color: "white",
          borderRadius: 8,
          padding: "8px 12px",
          marginBottom: 10,
          fontWeight: 600,
          fontSize: 17,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <span>
          🌱 Crop Health: {prediction.health.toUpperCase()} {healthIcon}
        </span>
        <span style={{ fontSize: 13, opacity: 0.9 }}>
          Confidence: {confidence}%
        </span>
      </div>

      {/* Forecasted Price */}
      <div
        style={{
          background: "#1976d2",
          color: "white",
          borderRadius: 8,
          padding: "10px 12px",
          fontWeight: 600,
          fontSize: 18,
        }}
      >
        💰 Forecasted Price: ₹{Number(prediction.price).toFixed(2)}{" "}
        <span style={{ fontSize: 14, fontWeight: 400 }}>/ quintal</span>
      </div>

      <div
        style={{
          fontSize: 13,
          color: "#555",
          marginTop: 8,
          fontStyle: "italic",
        }}
      >
        (Price estimated from recent market data, weather trends, and model
        learning.)
      </div>
    </div>
  );
}
