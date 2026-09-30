import React, { useState, useEffect } from "react";
import { useLocation } from "../context/LocationContext";
import { useAuth } from "../context/AuthContext";
import { simulationService } from "../api/services";
import {
  Sliders,
  AlertTriangle,
  TrendingUp,
  ShieldAlert,
  Play,
  CheckCircle2,
  Activity,
  Layers,
  Building2,
  Sparkles,
  RefreshCw,
  Lock
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from "recharts";

export default function SimulationPage() {
  const { selectedLocation } = useLocation();
  const { user, hasRole } = useAuth();
  const isViewer = user?.role === "VIEWER";
  const canRunSim = hasRole("SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER", "VIEWER");
  const [years, setYears] = useState(20);
  const [growthRate, setGrowthRate] = useState(2.0);
  const [fleetGrowth, setFleetGrowth] = useState(0.0);
  const [treatmentGrowth, setTreatmentGrowth] = useState(0.0);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const runSim = (overrideParams = {}) => {
    if (!selectedLocation) return;
    setLoading(true);

    const activeYears = overrideParams.years ?? years;
    const activeGrowth = overrideParams.growthRate ?? growthRate;
    const activeFleet = overrideParams.fleetGrowth ?? fleetGrowth;
    const activeTreatment = overrideParams.treatmentGrowth ?? treatmentGrowth;

    simulationService.run({
      location_id: selectedLocation.id,
      years: activeYears,
      growth_rate_override: activeGrowth,
      fleet_growth_rate: activeFleet,
      treatment_growth_rate: activeTreatment,
    })
      .then((res) => setResults(res.data?.results || res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  const applyPreset = (gRate, fGrowth, tGrowth) => {
    setGrowthRate(gRate);
    setFleetGrowth(fGrowth);
    setTreatmentGrowth(tGrowth);
    runSim({ growthRate: gRate, fleetGrowth: fGrowth, treatmentGrowth: tGrowth });
  };

  useEffect(() => {
    runSim();
  }, [selectedLocation]);

  if (!selectedLocation) {
    return <div className="page-loading">Please select an administrative location from the top navigation bar.</div>;
  }

  const yearlySeries = results?.years || [];
  const startYr = yearlySeries[0] || {};
  const endYr = yearlySeries[yearlySeries.length - 1] || {};

  return (
    <div className="simulation-view">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <div className="sim-badge-row">
            <span className="sim-pill-tag"><Sparkles size={12} style={{ display: 'inline', marginRight: 4 }} /> Long-Term Strategic Modeling</span>
            <span className="text-xs text-slate-400">Monte-Carlo & Multi-Year Projection Engine</span>
          </div>
          <h2 className="text-2xl font-extrabold text-white">20-Year Infrastructure Breach & Deficit Simulator</h2>
          <p className="text-slate-400 text-sm mt-1">Dynamic capacity forecasting under population expansion & asset scaling</p>
        </div>
      </div>

      {isViewer && (
        <div style={{ background: 'rgba(59, 130, 246, 0.12)', border: '1px solid rgba(59, 130, 246, 0.3)', color: '#60a5fa', padding: '12px 16px', borderRadius: 8, display: 'flex', alignItems: 'center', gap: 10, fontSize: 13, fontWeight: 600 }}>
          <Sparkles size={16} />
          <span><strong>Interactive Citizen Mode:</strong> Logged in as <em>Citizen Viewer</em>. You can freely adjust sliders to test "What-If" scenarios in your browser. Saving permanent parameters to the database is reserved for Planners.</span>
        </div>
      )}

      {/* KPI Cards */}
      <div className="sim-kpi-grid">
        <div className="sim-kpi-card">
          <div className="sim-kpi-header">
            <span>20-Year Cumulative Volume</span>
            <Layers size={18} className="text-emerald-400" />
          </div>
          <div className="sim-kpi-val">
            {(results?.total_cumulative_20yr_tonnes || 0).toLocaleString()} <span className="sim-kpi-unit">Tonnes</span>
          </div>
          <div className="sim-kpi-sub">
            <TrendingUp size={14} className="text-emerald-400" /> Projected total municipal footprint over {years} yrs
          </div>
        </div>

        <div className="sim-kpi-card">
          <div className="sim-kpi-header">
            <span>Fleet Capacity Breach</span>
            <ShieldAlert size={18} className={results?.fleet_breach_year ? "text-amber-400" : "text-emerald-400"} />
          </div>
          <div className="sim-kpi-val">
            {results?.fleet_breach_year ? `Year ${results.fleet_breach_year}` : "NO BREACH"}
          </div>
          <div className="sim-kpi-sub">
            {results?.fleet_breach_year ? (
              <span className="sim-status-badge danger"><AlertTriangle size={12} /> Deficit in Y{results.fleet_breach_year}</span>
            ) : (
              <span className="sim-status-badge safe"><CheckCircle2 size={12} /> Fleet Adequate</span>
            )}
          </div>
        </div>

        <div className="sim-kpi-card">
          <div className="sim-kpi-header">
            <span>Treatment Facility Breach</span>
            <Building2 size={18} className={results?.treatment_breach_year ? "text-red-400" : "text-emerald-400"} />
          </div>
          <div className="sim-kpi-val">
            {results?.treatment_breach_year ? `Year ${results.treatment_breach_year}` : "NO BREACH"}
          </div>
          <div className="sim-kpi-sub">
            {results?.treatment_breach_year ? (
              <span className="sim-status-badge danger"><AlertTriangle size={12} /> Overcapacity in Y{results.treatment_breach_year}</span>
            ) : (
              <span className="sim-status-badge safe"><CheckCircle2 size={12} /> Plant Adequate</span>
            )}
          </div>
        </div>

        <div className="sim-kpi-card">
          <div className="sim-kpi-header">
            <span>Horizon End Generation</span>
            <Activity size={18} className="text-blue-400" />
          </div>
          <div className="sim-kpi-val">
            {endYr.daily_waste_tonnes || 0} <span className="sim-kpi-unit">T/day</span>
          </div>
          <div className="sim-kpi-sub">
            Up from {startYr.daily_waste_tonnes || 0} T/day at Y0 (+{(((endYr.daily_waste_tonnes - startYr.daily_waste_tonnes) / (startYr.daily_waste_tonnes || 1)) * 100).toFixed(1)}%)
          </div>
        </div>
      </div>

      {/* Simulation Controls Dashboard (Visible only to authorized Planners & Authorities) */}
      {canRunSim && (
        <div className="sim-controls-section">
          <div className="sim-controls-header">
            <h3><Sliders size={18} className="text-blue-400" /> Interactive Simulation Scenario Parameters</h3>
            <div className="sim-presets">
              <button className="sim-preset-btn" onClick={() => applyPreset(2.0, 0.0, 0.0)}>Baseline (0% Exp)</button>
              <button className="sim-preset-btn" onClick={() => applyPreset(2.0, 3.0, 3.5)}>Moderate Exp (+3%)</button>
              <button className="sim-preset-btn" onClick={() => applyPreset(3.5, 5.0, 5.0)}>High Growth (+5%)</button>
            </div>
          </div>

          <div className="sim-sliders-grid">
            <div className="sim-slider-box">
              <div className="sim-slider-label-row">
                <span>Simulation Horizon</span>
                <span className="sim-val-pill">{years} Years</span>
              </div>
              <input
                type="range"
                min="5"
                max="30"
                value={years}
                onChange={(e) => setYears(parseInt(e.target.value))}
                className="sim-slider-input"
              />
            </div>

            <div className="sim-slider-box">
              <div className="sim-slider-label-row">
                <span>Population Growth</span>
                <span className="sim-val-pill">{growthRate}% / yr</span>
              </div>
              <input
                type="range"
                min="0"
                max="5"
                step="0.1"
                value={growthRate}
                onChange={(e) => setGrowthRate(parseFloat(e.target.value))}
                className="sim-slider-input"
              />
            </div>

            <div className="sim-slider-box">
              <div className="sim-slider-label-row">
                <span>Fleet Expansion Rate</span>
                <span className="sim-val-pill">{fleetGrowth}% / yr</span>
              </div>
              <input
                type="range"
                min="0"
                max="10"
                step="0.5"
                value={fleetGrowth}
                onChange={(e) => setFleetGrowth(parseFloat(e.target.value))}
                className="sim-slider-input"
              />
            </div>

            <div className="sim-slider-box">
              <div className="sim-slider-label-row">
                <span>Treatment Capacity Expansion</span>
                <span className="sim-val-pill">{treatmentGrowth}% / yr</span>
              </div>
              <input
                type="range"
                min="0"
                max="10"
                step="0.5"
                value={treatmentGrowth}
                onChange={(e) => setTreatmentGrowth(parseFloat(e.target.value))}
                className="sim-slider-input"
              />
            </div>
          </div>

          <div className="sim-run-bar">
            <button className="sim-action-btn" onClick={() => runSim()} disabled={loading}>
              {loading ? (
                <><RefreshCw size={16} className="animate-spin" /> Computing Simulation...</>
              ) : (
                <><Play size={16} /> Re-Calculate Scenario</>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Main Simulation Trajectory Graph */}
      <div className="sim-chart-card">
        <div className="chart-header" style={{ marginBottom: 16 }}>
          <h3 style={{ fontSize: 16, fontWeight: 700, color: '#f8fafc' }}>
            Daily Generation vs Infrastructure Capacity Curves (Tonnes / Day)
          </h3>
          <span className="subtext">Intersections signal municipal infrastructure capacity breaches</span>
        </div>
        <div style={{ width: '100%', height: 340 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={yearlySeries}>
              <defs>
                <linearGradient id="colorGen" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.6} />
              <XAxis dataKey="year" stroke="#94a3b8" tickFormatter={(v) => `Yr ${v}`} />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: 8, color: "#fff" }}
                formatter={(val) => [`${val} T/day`, '']}
                labelFormatter={(label) => `Simulation Year ${label}`}
              />
              <Legend verticalAlign="top" height={36} />
              <Area type="monotone" dataKey="daily_waste_tonnes" name="Daily Generation (T)" stroke="#ef4444" strokeWidth={2.5} fillOpacity={1} fill="url(#colorGen)" />
              <Line type="monotone" dataKey="fleet_capacity_tonnes" name="Collection Fleet Capacity (T)" stroke="#3b82f6" strokeWidth={2.5} strokeDasharray="6 6" dot={false} />
              <Line type="monotone" dataKey="treatment_capacity_tonnes" name="Treatment Facility Capacity (T)" stroke="#10b981" strokeWidth={2.5} strokeDasharray="6 6" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Year 0 vs Year N Summary Table */}
      <div className="sim-table-card">
        <h3 style={{ fontSize: 16, fontWeight: 700, color: '#f8fafc', marginBottom: 12 }}>
          Strategic Metric Transition (Year 0 vs Year {years})
        </h3>
        <table className="sim-comparison-table">
          <thead>
            <tr>
              <th>Planning Metric</th>
              <th>Year 0 (Initial)</th>
              <th>Year {years} (Projected)</th>
              <th>Net Change</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Permanent Population</td>
              <td>{(startYr.permanent_population || 0).toLocaleString()}</td>
              <td>{(endYr.permanent_population || 0).toLocaleString()}</td>
              <td className="text-emerald-400">+{((endYr.permanent_population || 0) - (startYr.permanent_population || 0)).toLocaleString()}</td>
            </tr>
            <tr>
              <td>Daily Waste Generation</td>
              <td>{startYr.daily_waste_tonnes || 0} T/day</td>
              <td>{endYr.daily_waste_tonnes || 0} T/day</td>
              <td className="text-amber-400">+{((endYr.daily_waste_tonnes || 0) - (startYr.daily_waste_tonnes || 0)).toFixed(2)} T/day</td>
            </tr>
            <tr>
              <td>Collection Fleet Capacity</td>
              <td>{startYr.fleet_capacity_tonnes || 0} T/day</td>
              <td>{endYr.fleet_capacity_tonnes || 0} T/day</td>
              <td>+{((endYr.fleet_capacity_tonnes || 0) - (startYr.fleet_capacity_tonnes || 0)).toFixed(2)} T/day</td>
            </tr>
            <tr>
              <td>Treatment Infrastructure Capacity</td>
              <td>{startYr.treatment_capacity_tonnes || 0} T/day</td>
              <td>{endYr.treatment_capacity_tonnes || 0} T/day</td>
              <td>+{((endYr.treatment_capacity_tonnes || 0) - (startYr.treatment_capacity_tonnes || 0)).toFixed(2)} T/day</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
