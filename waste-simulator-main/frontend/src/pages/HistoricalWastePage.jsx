import React, { useState, useEffect } from "react";
import { useLocation } from "../context/LocationContext";
import { historicalService } from "../api/services";
import { History, Calendar, TrendingUp, BarChart2, PlusCircle } from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar
} from "recharts";

export default function HistoricalWastePage() {
  const { selectedLocation } = useLocation();
  const [period, setPeriod] = useState("1_MONTH");
  const [analytics, setAnalytics] = useState(null);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);

  // New record modal state
  const [newDate, setNewDate] = useState(new Date().toISOString().split("T")[0]);
  const [newQty, setNewQty] = useState("");
  const [newMethod, setNewMethod] = useState("WEIGHBRIDGE");

  const loadData = () => {
    if (!selectedLocation) return;
    setLoading(true);
    Promise.all([
      historicalService.getAnalytics(selectedLocation.id, { period_type: period }),
      historicalService.list(selectedLocation.id, { limit: 100 }),
    ])
      .then(([aRes, rRes]) => {
        setAnalytics(aRes.data);
        setRecords(rRes.data);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, [selectedLocation, period]);

  const handleAddRecord = async (e) => {
    e.preventDefault();
    if (!newQty || !selectedLocation) return;
    try {
      await historicalService.create({
        habitation_id: selectedLocation.id,
        measurement_date: newDate,
        quantity: parseFloat(newQty),
        unit: "tonnes",
        waste_category: "MIXED",
        measurement_method: newMethod,
        quality_status: "MEASURED",
        notes: "Field weighbridge log entry",
      });
      setNewQty("");
      loadData();
    } catch (err) {
      alert("Failed to record historical entry.");
    }
  };

  if (!selectedLocation) return <div className="page-loading">Please select an administrative location.</div>;

  const weekdayData = analytics?.weekday_pattern
    ? Object.entries(analytics.weekday_pattern).map(([day, val]) => ({ day, avg: val }))
    : [];

  return (
    <div className="history-view">
      <div className="page-header">
        <div>
          <h2>Historical Waste Time Series</h2>
          <p>Weighbridge intake records with multi-period aggregation</p>
        </div>

        {/* Period Selector Tabs */}
        <div className="period-tabs">
          {["1_DAY", "2_DAY", "1_WEEK", "1_MONTH", "3_MONTH", "6_MONTH", "1_YEAR", "CUSTOM"].map((p) => (
            <button
              key={p}
              className={`tab-btn ${period === p ? "active" : ""}`}
              onClick={() => setPeriod(p)}
            >
              {p.replace("_", " ")}
            </button>
          ))}
        </div>
      </div>

      {/* Analytics Summary */}
      <div className="metrics-grid">
        <div className="metric-card">
          <span className="card-label">Total Volume in Period</span>
          <div className="card-val">{analytics?.total_quantity_tonnes || 0} <span className="unit">T</span></div>
          <div className="card-sub">{analytics?.records_count || 0} measurements</div>
        </div>
        <div className="metric-card">
          <span className="card-label">Daily Average Intake</span>
          <div className="card-val">{analytics?.daily_average_tonnes || 0} <span className="unit">T/day</span></div>
          <div className="card-sub">Std Dev: {analytics?.std_dev || 0} T</div>
        </div>
        <div className="metric-card">
          <span className="card-label">Peak Daily Intake</span>
          <div className="card-val">{analytics?.maximum_tonnes || 0} <span className="unit">T</span></div>
          <div className="card-sub">Min: {analytics?.minimum_tonnes || 0} T</div>
        </div>
        <div className="metric-card">
          <span className="card-label">Empirical Trend</span>
          <div className="card-val text-emerald-500">{analytics?.trend_direction || "STABLE"}</div>
          <div className="card-sub">Change: {analytics?.percentage_change || 0}%</div>
        </div>
      </div>

      {/* Time Series Charts */}
      <div className="charts-grid">
        <div className="chart-card">
          <div className="chart-header">
            <h3>Time Series Trajectory (Tonnes / Day)</h3>
            <span className="subtext">Chronological weighbridge logs</span>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={analytics?.daily_time_series || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" domain={['auto', 'auto']} />
                <Tooltip contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#fff" }} />
                <Line type="monotone" dataKey="quantity" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-header">
            <h3>Weekly Day-of-Week Pattern</h3>
            <span className="subtext">Intra-week cyclic load distribution</span>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={weekdayData}>
                <XAxis dataKey="day" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#fff" }} />
                <Bar dataKey="avg" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Add New Entry Form & Table */}
      <div className="section-card">
        <div className="chart-header">
          <h3>Log New Weighbridge Measurement</h3>
        </div>
        <form onSubmit={handleAddRecord} className="inline-entry-form">
          <input
            type="date"
            required
            value={newDate}
            onChange={(e) => setNewDate(e.target.value)}
          />
          <input
            type="number"
            step="0.01"
            placeholder="Quantity (Tonnes)"
            required
            value={newQty}
            onChange={(e) => setNewQty(e.target.value)}
          />
          <select value={newMethod} onChange={(e) => setNewMethod(e.target.value)}>
            <option value="WEIGHBRIDGE">Weighbridge (Automated)</option>
            <option value="TRUCK_COUNT">Truck Volume Count</option>
            <option value="SAMPLE_WEIGHING">Sample Weighing</option>
          </select>
          <button type="submit" className="add-btn">
            <PlusCircle size={16} /> Record Measurement
          </button>
        </form>

        <table className="data-table mt-4">
          <thead>
            <tr>
              <th>Date</th>
              <th>Quantity (Tonnes)</th>
              <th>Category</th>
              <th>Method</th>
              <th>Quality Status</th>
            </tr>
          </thead>
          <tbody>
            {records.map((r) => (
              <tr key={r.id}>
                <td>{r.measurement_date}</td>
                <td><strong>{r.quantity} T</strong> ({Math.round(r.quantity * 1000)} kg)</td>
                <td>{r.waste_category}</td>
                <td><span className="badge-blue">{r.measurement_method}</span></td>
                <td><span className="badge-green">{r.quality_status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
