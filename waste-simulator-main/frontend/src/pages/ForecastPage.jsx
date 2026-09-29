import React, { useState, useEffect } from "react";
import { useLocation } from "../context/LocationContext";
import { forecastService } from "../api/services";
import { TrendingUp, Award, AlertCircle, BarChart3 } from "lucide-react";
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

export default function ForecastPage() {
  const { selectedLocation } = useLocation();
  const [period, setPeriod] = useState("NEXT_MONTH");
  const [selectedMethod, setSelectedMethod] = useState("AUTO");
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedLocation) return;
    setLoading(true);
    forecastService.getEvaluation(selectedLocation.id, {
      period,
      selected_method_override: selectedMethod !== "AUTO" ? selectedMethod : undefined,
    })
      .then((res) => setForecast(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [selectedLocation, period, selectedMethod]);

  if (!selectedLocation) return <div className="page-loading">Please select an administrative location.</div>;
  if (loading || !forecast) return <div className="page-loading">Evaluating forecasting models & computing backtests...</div>;

  return (
    <div className="forecast-view">
      <div className="page-header">
        <div>
          <h2>Time-Series Forecasting & Error Backtesting</h2>
          <p>Multi-model projection with empirical validation (MAE, RMSE, MAPE)</p>
        </div>

        <div className="flex gap-2">
          <select value={period} onChange={(e) => setPeriod(e.target.value)} className="select-pill">
            <option value="NEXT_WEEK">Next 7 Days</option>
            <option value="NEXT_MONTH">Next 30 Days</option>
            <option value="NEXT_YEAR">Next 12 Months</option>
          </select>

          <select value={selectedMethod} onChange={(e) => setSelectedMethod(e.target.value)} className="select-pill">
            <option value="AUTO">Auto-Select (Lowest Error)</option>
            <option value="BASELINE">Baseline Mean</option>
            <option value="MOVING_AVERAGE">Moving Average</option>
            <option value="WEIGHTED_MOVING_AVERAGE">Weighted Moving Avg</option>
            <option value="TREND_ADJUSTED">Linear Trend Adjusted</option>
            <option value="SEASONAL_BASELINE">Seasonal Composite</option>
          </select>
        </div>
      </div>

      {/* Model Selection Recommendation Card */}
      <div className="reconcile-card">
        <div className="rec-header">
          <Award size={22} className="text-emerald-500" />
          <div>
            <h3>Selected Model: <strong>{forecast.selected_method}</strong> ({forecast.confidence_level} Confidence)</h3>
            <p>{forecast.selection_reason}</p>
          </div>
        </div>
      </div>

      {/* Accuracy Metrics Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <span className="card-label">Projected Daily Average</span>
          <div className="card-val">{forecast.forecast_value} <span className="unit">T/day</span></div>
          <div className="card-sub">Horizon: {period.replace("_", " ")}</div>
        </div>
        <div className="metric-card">
          <span className="card-label">Mean Absolute Error (MAE)</span>
          <div className="card-val">{forecast.mae !== null ? `${forecast.mae} T` : "N/A"}</div>
          <div className="card-sub">Absolute average variance</div>
        </div>
        <div className="metric-card">
          <span className="card-label">Root Mean Sq. Error (RMSE)</span>
          <div className="card-val">{forecast.rmse !== null ? `${forecast.rmse} T` : "N/A"}</div>
          <div className="card-sub">Penalizes large deviations</div>
        </div>
        <div className="metric-card">
          <span className="card-label">Mean Absolute % Error</span>
          <div className="card-val">{forecast.mape !== null ? `${forecast.mape}%` : "N/A"}</div>
          <div className="card-sub">Relative error percentage</div>
        </div>
      </div>

      {/* Projected Trajectory Chart */}
      <div className="charts-grid">
        <div className="chart-card">
          <div className="chart-header">
            <h3>Forecast Trajectory</h3>
            <span className="subtext">Projected future intake series</span>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={forecast.projected_series || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#fff" }} />
                <Line type="monotone" dataKey="forecast_tonnes" stroke="#3b82f6" strokeWidth={2} dot={{ r: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Model Error Comparison */}
        <div className="chart-card">
          <div className="chart-header">
            <h3>Backtesting Model Error Comparison (MAE)</h3>
            <span className="subtext">Lower MAE indicates superior accuracy</span>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={forecast.method_comparison || []}>
                <XAxis dataKey="method" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#fff" }} />
                <Bar dataKey="mae" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
