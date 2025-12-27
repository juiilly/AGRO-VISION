import React, { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  Legend,
} from "recharts";

export default function SupplyAnalytics({ city }) {
  const [allocations, setAllocations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchSupplyData = async () => {
    if (!city) {
      setError("Please enter a city on the dashboard first.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://127.0.0.1:5000/api/supply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          city: city,
          demand: { [city]: 10000 },
        }),
      });

      if (!response.ok) throw new Error("Server error");

      const data = await response.json();
      if (data.allocations && data.allocations.length > 0) {
        setAllocations(data.allocations);
      } else {
        setAllocations([]);
        setError("No stock available or no matching warehouses found.");
      }
    } catch (e) {
      console.error(e);
      setError("Failed to fetch allocations. Please try again.");
    }

    setLoading(false);
  };

  // 📊 Prepare data for bar chart
  const warehouseTotals = {};
  allocations.forEach((a) => {
    if (!a.warehouse) return;
    warehouseTotals[a.warehouse] =
      (warehouseTotals[a.warehouse] || 0) + a.allocated;
  });

  const chartData = Object.entries(warehouseTotals).map(([wh, val]) => ({
    warehouse: wh,
    allocated: val,
  }));

  return (
    <div
      style={{
        background: "#e3f2fd",
        borderRadius: 10,
        padding: 16,
        boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
      }}
    >
      <h3>🚚 Live Supply Chain Analytics</h3>
      <p className="small">
        Real-time warehouse allocation and stock levels across regions.
      </p>

      <button
        onClick={fetchSupplyData}
        disabled={loading}
        style={{
          padding: "10px 18px",
          background: loading ? "#999" : "#2e7d32",
          color: "white",
          border: "none",
          borderRadius: 8,
          marginBottom: 15,
          cursor: loading ? "not-allowed" : "pointer",
          fontWeight: 600,
        }}
      >
        🔄 {loading ? "Loading..." : "Refresh Live Data"}
      </button>

      {error && (
        <div
          style={{
            background: "#ffebee",
            color: "#c62828",
            padding: "8px 12px",
            borderRadius: 6,
            marginBottom: 10,
          }}
        >
          ⚠️ {error}
        </div>
      )}

      {allocations.length > 0 && (
        <>
          {/* Table */}
          <table className="table">
            <thead>
              <tr>
                <th>Region</th>
                <th>Warehouse</th>
                <th>Allocated (tons)</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {allocations.map((a, i) => (
                <tr key={i}>
                  <td>{a.region}</td>
                  <td>{a.warehouse || "—"}</td>
                  <td>{a.allocated}</td>
                  <td>{a.note ? "⚠️ " + a.note : "✅ Fulfilled"}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Chart */}
          <div style={{ marginTop: 30 }}>
            <h4>📊 Allocation per Warehouse</h4>
            <div
              style={{
                background: "white",
                borderRadius: 10,
                padding: 10,
                height: 300,
                boxShadow: "inset 0 1px 4px rgba(0,0,0,0.1)",
              }}
            >
              {chartData.length === 0 ? (
                <p
                  style={{
                    textAlign: "center",
                    color: "#777",
                    marginTop: 120,
                  }}
                >
                  No warehouse data to display.
                </p>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={chartData}
                    margin={{ top: 10, right: 30, left: 10, bottom: 20 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="warehouse" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar
                      dataKey="allocated"
                      fill="#42a5f5"
                      name="Allocated (tons)"
                      barSize={40}
                    />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </>
      )}

      {!loading && !error && allocations.length === 0 && (
        <p
          className="small"
          style={{
            color: "#555",
            marginTop: 10,
          }}
        >
          No allocation data yet. Click “Refresh Live Data” to fetch from server.
        </p>
      )}
    </div>
  );
}
