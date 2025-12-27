import React, { useEffect, useState } from "react";

export default function RetrainStatus() {
  const [status, setStatus] = useState("checking");
  const [lastRun, setLastRun] = useState(null);
  const [details, setDetails] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStatus = async () => {
      setLoading(true);
      try {
        const res = await fetch("http://127.0.0.1:5000/api/retrain/status");
        const data = await res.json();
        setStatus(data.status || "unknown");
        setLastRun(data.last_run || null);
        setDetails(data.details || null);
      } catch (e) {
        console.error(e);
        setStatus("error");
      }
      setLoading(false);
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 20000); // auto-refresh every 20 sec
    return () => clearInterval(interval);
  }, []);

  const getStatusStyle = () => {
    if (status.includes("success"))
      return { color: "#2e7d32", fontWeight: 600 };
    if (status.includes("fail") || status === "error")
      return { color: "#d32f2f", fontWeight: 600 };
    return { color: "#f9a825", fontWeight: 600 };
  };

  return (
    <div
      className="card"
      style={{
        background: "#f9fafc",
        padding: "20px",
        borderRadius: "10px",
        boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
      }}
    >
      <h3 style={{ marginBottom: "10px" }}>🔁 Model Retraining Status</h3>

      {loading ? (
        <p style={{ color: "#555" }}>⏳ Checking latest retraining info...</p>
      ) : (
        <>
          <p style={getStatusStyle()}>
            {status === "pending"
              ? "⚠️ Retraining scheduled or in progress..."
              : status.includes("success")
              ? "✅ Retraining completed successfully!"
              : status.includes("fail")
              ? `❌ Retraining failed — ${status}`
              : status === "error"
              ? "⚠️ Unable to fetch retrain status (server offline?)"
              : "ℹ️ Waiting for retrain log..."}
          </p>

          {details && (
            <div style={{ marginTop: "10px", fontSize: "14px", color: "#333" }}>
              <b>Trained models:</b> {details.models_trained || 0} <br />
              <b>Records used:</b> {details.records_used || "N/A"}
            </div>
          )}

          <p
            style={{
              fontSize: "13px",
              marginTop: "10px",
              color: "#555",
            }}
          >
            {lastRun
              ? `🕒 Last updated: ${new Date(lastRun).toLocaleString()}`
              : "No retraining log yet."}
          </p>
        </>
      )}
    </div>
  );
}
