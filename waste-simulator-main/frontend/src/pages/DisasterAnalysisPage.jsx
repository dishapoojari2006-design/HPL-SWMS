import React, { useState, useEffect } from "react";
import { useLocationContext } from "../context/LocationContext";
import { disasterService } from "../api/services";
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from "recharts";
import {
  ShieldAlert, TrendingUp, AlertTriangle, Truck, Layers, Activity,
  RefreshCw
} from "lucide-react";

export default function DisasterAnalysisPage() {
  const { selectedLocationId, selectedLocation } = useLocationContext();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const [params, setParams] = useState({
    disaster_type: "Flood",
    severity: "HIGH",
    duration_days: 7,
    affected_population: 5000,
    displaced_population: 2000,
    shelter_population: 1200,
    road_access_pct: 50,
    collection_efficiency_pct: 60,
    treatment_capacity_pct: 80,
    additional_waste_pct: 25,
    debris_tonnes_day: 2.5
  });

  const runSimulation = async () => {
    if (!selectedLocationId) return;
    setLoading(true);
    try {
      const res = await disasterService.simulateAccumulation({
        ...params,
        location_id: selectedLocationId,
        duration_days: parseInt(params.duration_days, 10),
        affected_population: parseFloat(params.affected_population),
        displaced_population: parseFloat(params.displaced_population),
        shelter_population: parseFloat(params.shelter_population),
        road_access_pct: parseFloat(params.road_access_pct),
        collection_efficiency_pct: parseFloat(params.collection_efficiency_pct),
        treatment_capacity_pct: parseFloat(params.treatment_capacity_pct),
        additional_waste_pct: parseFloat(params.additional_waste_pct),
        debris_tonnes_day: parseFloat(params.debris_tonnes_day)
      });
      setResults(res.data);
    } catch (err) {
      console.error(err);
      alert("Failed to run disaster accumulation simulation.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runSimulation();
  }, [selectedLocationId]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            <Activity className="h-6 w-6 text-amber-600" />
            Disaster Multi-Day Accumulation & Impact Engine
          </h1>
          <p className="text-sm text-slate-500">
            Day-by-day generation surge, road blockage disruptions, shelter waste, and cumulative uncollected backlog for {selectedLocation?.name || "Selected Location"}.
          </p>
        </div>

        <button
          onClick={runSimulation}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-medium text-sm rounded-lg shadow-sm transition disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Run Disaster Simulation
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
          Disaster Scenario Parameters & Disruption Controls
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
          <div>
            <label className="font-semibold text-slate-700 block mb-1">Disaster Type</label>
            <select
              value={params.disaster_type}
              onChange={(e) => setParams({ ...params, disaster_type: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500"
            >
              <option value="Flood">Flood</option>
              <option value="Flash Flood">Flash Flood</option>
              <option value="Cyclone">Cyclone / Gale Storm</option>
              <option value="Landslide">Landslide</option>
              <option value="Earthquake">Earthquake</option>
              <option value="Extreme Heat">Extreme Heatwave</option>
            </select>
          </div>

          <div>
            <label className="font-semibold text-slate-700 block mb-1">Severity Level</label>
            <select
              value={params.severity}
              onChange={(e) => setParams({ ...params, severity: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500"
            >
              <option value="LOW">LOW</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="HIGH">HIGH</option>
              <option value="EXTREME">EXTREME</option>
            </select>
          </div>

          <div>
            <label className="font-semibold text-slate-700 block mb-1">Duration: {params.duration_days} Days</label>
            <input
              type="range"
              min="3"
              max="21"
              value={params.duration_days}
              onChange={(e) => setParams({ ...params, duration_days: e.target.value })}
              className="w-full accent-amber-600"
            />
          </div>

          <div>
            <label className="font-semibold text-slate-700 block mb-1">Road Accessibility: {params.road_access_pct}%</label>
            <input
              type="range"
              min="10"
              max="100"
              value={params.road_access_pct}
              onChange={(e) => setParams({ ...params, road_access_pct: e.target.value })}
              className="w-full accent-amber-600"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs pt-2 border-t border-slate-100">
          <div>
            <label className="font-semibold text-slate-700 block mb-1">Collection Efficiency: {params.collection_efficiency_pct}%</label>
            <input
              type="range"
              min="10"
              max="100"
              value={params.collection_efficiency_pct}
              onChange={(e) => setParams({ ...params, collection_efficiency_pct: e.target.value })}
              className="w-full accent-amber-600"
            />
          </div>

          <div>
            <label className="font-semibold text-slate-700 block mb-1">Treatment Capacity: {params.treatment_capacity_pct}%</label>
            <input
              type="range"
              min="10"
              max="100"
              value={params.treatment_capacity_pct}
              onChange={(e) => setParams({ ...params, treatment_capacity_pct: e.target.value })}
              className="w-full accent-amber-600"
            />
          </div>

          <div>
            <label className="font-semibold text-slate-700 block mb-1">Shelter Population</label>
            <input
              type="number"
              value={params.shelter_population}
              onChange={(e) => setParams({ ...params, shelter_population: e.target.value })}
              className="w-full px-3 py-1.5 border rounded-lg"
            />
          </div>

          <div>
            <label className="font-semibold text-slate-700 block mb-1">Daily Debris (Tonnes)</label>
            <input
              type="number"
              step="0.5"
              value={params.debris_tonnes_day}
              onChange={(e) => setParams({ ...params, debris_tonnes_day: e.target.value })}
              className="w-full px-3 py-1.5 border rounded-lg"
            />
          </div>
        </div>
      </div>

      {results && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
              <span className="text-xs font-semibold text-slate-500 block">Daily Generated Waste</span>
              <div className="mt-1 flex items-baseline gap-1">
                <span className="text-2xl font-bold text-slate-900">{results.components?.total_disaster_waste_tonnes_day}</span>
                <span className="text-xs text-slate-500">T/day</span>
              </div>
              <span className="text-xs text-amber-600 font-medium mt-1 block">
                +{results.components?.disaster_surge_percentage}% surge over baseline
              </span>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
              <span className="text-xs font-semibold text-slate-500 block">Total Disaster Waste</span>
              <div className="mt-1 flex items-baseline gap-1">
                <span className="text-2xl font-bold text-slate-900">{results.total_period_generated_tonnes}</span>
                <span className="text-xs text-slate-500">Tonnes</span>
              </div>
              <span className="text-xs text-slate-500 mt-1 block">Over {results.duration_days} days period</span>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
              <span className="text-xs font-semibold text-slate-500 block">Peak Uncollected Backlog</span>
              <div className="mt-1 flex items-baseline gap-1">
                <span className="text-2xl font-bold text-red-600">{results.peak_accumulated_waste_tonnes}</span>
                <span className="text-xs text-slate-500">Tonnes</span>
              </div>
              <span className="text-xs text-red-500 font-medium mt-1 block">Maximum street accumulation</span>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
              <span className="text-xs font-semibold text-slate-500 block">Treatment Capacity Gap</span>
              <div className="mt-1 flex items-baseline gap-1">
                <span className="text-2xl font-bold text-amber-700">{results.total_period_treatment_gap_tonnes}</span>
                <span className="text-xs text-slate-500">Tonnes</span>
              </div>
              <span className="text-xs text-amber-600 mt-1 block">Exceeds plant throughput</span>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
              <span className="text-xs font-semibold text-slate-500 block">Peak Vehicle Deficit</span>
              <div className="mt-1 flex items-baseline gap-1">
                <span className="text-2xl font-bold text-slate-900">{results.max_vehicle_deficit}</span>
                <span className="text-xs text-slate-500">Trucks</span>
              </div>
              <span className="text-xs text-slate-500 mt-1 block">Required emergency reinforcements</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <h3 className="text-base font-bold text-slate-900 mb-1 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-red-600" />
                Cumulative Uncollected Waste Backlog (Tonnes)
              </h3>
              <p className="text-xs text-slate-500 mb-4">
                Day-by-day accumulation curve showing uncollected waste buildup during emergency disruption.
              </p>
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={results.daily_series}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="day" label={{ value: "Disaster Day", position: "insideBottom", offset: -5 }} />
                    <YAxis label={{ value: "Tonnes", angle: -90, position: "insideLeft" }} />
                    <Tooltip />
                    <Legend />
                    <Area type="monotone" dataKey="cumulative_accumulated_tonnes" stroke="#dc2626" fill="#fee2e2" name="Cumulative Backlog (T)" />
                    <Area type="monotone" dataKey="total_generated_tonnes" stroke="#d97706" fill="#fef3c7" name="Daily Generated (T)" />
                    <Area type="monotone" dataKey="collected_tonnes" stroke="#16a34a" fill="#dcfce7" name="Daily Collected (T)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
              <h3 className="text-base font-bold text-slate-900 mb-1 flex items-center gap-2">
                <Layers className="h-5 w-5 text-amber-600" />
                Disaster Waste Component Breakdown
              </h3>
              <p className="text-xs text-slate-500 mb-4">
                Separation of Normal Baseline, Shelter Surge, Additional Disaster Waste, and Debris/Silt.
              </p>
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={[
                    { name: "Normal Baseline", tonnes: results.components?.normal_baseline_waste_tonnes_day },
                    { name: "Shelter Population", tonnes: results.components?.shelter_waste_tonnes_day },
                    { name: "Additional Surge", tonnes: results.components?.disaster_additional_waste_tonnes_day },
                    { name: "Debris & Silt", tonnes: results.components?.debris_cleanup_waste_tonnes_day }
                  ]}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="name" />
                    <YAxis label={{ value: "T/day", angle: -90, position: "insideLeft" }} />
                    <Tooltip />
                    <Bar dataKey="tonnes" fill="#f59e0b" name="Tonnes per Day" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
