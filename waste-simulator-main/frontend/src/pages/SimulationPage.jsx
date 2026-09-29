import React, { useState, useEffect } from "react";
import { useLocation } from "../context/LocationContext";
import { simulationService, wasteService } from "../api/services";
import { Sliders, AlertTriangle, TrendingUp, ShieldAlert, Play } from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from "recharts";

export default function SimulationPage() {
  const { selectedLocation } = useLocation();
  const [years, setYears] = useState(20);
  const [growthRate, setGrowthRate] = useState(2.0);
  const [fleetGrowth, setFleetGrowth] = useState(0.0);
  const [treatmentGrowth, setTreatmentGrowth] = useState(0.0);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const runSim = () => {
    if (!selectedLocation) return;
    setLoading(true);
    simulationService.run({
      location_id: selectedLocation.id,
      years,
      growth_rate_override: growthRate,
      fleet_growth_rate: fleetGrowth,
      treatment_growth_rate: treatmentGrowth,
    })
      .then((res) => setResults(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    runSim();
  }, [selectedLocation]);

  if (!selectedLocation) return <div className="page-loading">Please select an administrative location.</div>;

  return (
    <div className="simulation-view">
      <div className="page-header">
        <div>
          <h2>20-Year Long-Term Simulation & Infrastructure Breach Analyzer</h2>
          <p>Dynamic capacity deficit forecasting under demographic & economic pressure</p>
        </div>
      </div>

      {/* Simulation Controls */}
      <div className="sim-controls-card">
        <div className="control-field">
          <label>Simulation Horizon (Years): {years}</label>
          <input type="range" min="5" max="30" value={years} onChange={(e) => setYears(parseInt(e.target.value))} />
        </div>
        <div className="control-field">
          <label>Pop. Growth Rate: {growthRate}% / yr</label>
          <input type="range" min="0" max="5" step="0.1" value={growthRate} onChange={(e) => setGrowthRate(parseFloat(e.target.value))} />
        </div>
        <div className="control-field">
          <label>Fleet Expansion: {fleetGrowth}% / yr</label>
          <input type="range" min="0" max="10" step="0.5" value={fleetGrowth} onChange={(e) => setFleetGrowth(parseFloat(e.target.value))} />
        </div>
        <div className="control-field">
          <label>Treatment Expansion: {treatmentGrowth}% / yr</label>
          <input type="range" min="0" max="10" step="0.5" value={treatmentGrowth} onChange={(e) => setTreatmentGrowth(parseFloat(e.target.value))} />
        </div>
        <button className="run-sim-btn" onClick={runSim} disabled={loading}>
          <Play size={16} /> {loading ? "Simulating..." : "Run Simulation"}
        </button>
      </div>

      {/* Breach Warnings */}
      <div className="breach-grid">
        <div className="breach-card">
          <ShieldAlert size={20} className="text-amber-500" />
          <div>
            <h4>Collection Fleet Capacity Breach</h4>
            <p>
              {results?.fleet_breach_year
                ? `Current fleet will become deficient in Year ${results.fleet_breach_year}.`
                : "No collection fleet breach projected within this horizon."}
            </p>
          </div>
        </div>

        <div className="breach-card">
          <AlertTriangle size={20} className="text-red-500" />
          <div>
            <h4>Treatment Facility Capacity Breach</h4>
            <p>
              {results?.treatment_breach_year
                ? `Treatment plants will exceed 100% capacity in Year ${results.treatment_breach_year}.`
                : "Treatment infrastructure remains adequate."}
            </p>
          </div>
        </div>
      </div>

      {/* Simulation Trajectory Chart */}
      <div className="section-card">
        <div className="chart-header">
          <h3>20-Year Generation vs Infrastructure Capacity (Tonnes / Day)</h3>
          <span className="subtext">Intersection points represent critical municipal breach years</span>
        </div>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={results?.years || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="year" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#fff" }} />
              <Legend />
              <Line type="monotone" dataKey="daily_waste_tonnes" name="Daily Generation (T)" stroke="#ef4444" strokeWidth={2} />
              <Line type="monotone" dataKey="fleet_capacity_tonnes" name="Fleet Capacity (T)" stroke="#3b82f6" strokeWidth={2} strokeDasharray="5 5" />
              <Line type="monotone" dataKey="treatment_capacity_tonnes" name="Treatment Capacity (T)" stroke="#10b981" strokeWidth={2} strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
