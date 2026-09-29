import React, { useState } from "react";
import { useLocationContext } from "../context/LocationContext";
import { disasterService } from "../api/services";
import { GitCompare, ShieldCheck, RefreshCw } from "lucide-react";

export default function DisasterScenariosPage() {
  const { selectedLocation } = useLocationContext();
  const [loading, setLoading] = useState(false);
  const [comparison, setComparison] = useState(null);

  const [baseParams, setBaseParams] = useState({
    disaster_type: "Flood",
    severity: "HIGH",
    duration_days: 7,
    affected_population: 5000,
    displaced_population: 2000,
    shelter_population: 1500,
    road_access_pct: 50,
    collection_efficiency_pct: 60,
    treatment_capacity_pct: 80,
    additional_waste_pct: 25,
    debris_tonnes_day: 2.5
  });

  const [scenParams, setScenParams] = useState({
    disaster_type: "Flood",
    severity: "HIGH",
    duration_days: 7,
    affected_population: 5000,
    displaced_population: 2000,
    shelter_population: 1500,
    road_access_pct: 80,
    collection_efficiency_pct: 85,
    treatment_capacity_pct: 95,
    additional_waste_pct: 25,
    debris_tonnes_day: 2.5
  });

  const runComparison = async () => {
    setLoading(true);
    try {
      const res = await disasterService.whatIfAnalysis({
        baseline_scenario: {
          location_id: 1,
          name: "Baseline Disaster Scenario",
          ...baseParams,
          duration_days: parseInt(baseParams.duration_days, 10),
          road_access_pct: parseFloat(baseParams.road_access_pct),
          collection_efficiency_pct: parseFloat(baseParams.collection_efficiency_pct),
          treatment_capacity_pct: parseFloat(baseParams.treatment_capacity_pct),
          additional_waste_pct: parseFloat(baseParams.additional_waste_pct),
          debris_tonnes_day: parseFloat(baseParams.debris_tonnes_day)
        },
        modified_scenario: {
          location_id: 1,
          name: "Mitigated / Rapid Response Scenario",
          ...scenParams,
          duration_days: parseInt(scenParams.duration_days, 10),
          road_access_pct: parseFloat(scenParams.road_access_pct),
          collection_efficiency_pct: parseFloat(scenParams.collection_efficiency_pct),
          treatment_capacity_pct: parseFloat(scenParams.treatment_capacity_pct),
          additional_waste_pct: parseFloat(scenParams.additional_waste_pct),
          debris_tonnes_day: parseFloat(scenParams.debris_tonnes_day)
        }
      });
      setComparison(res.data);
    } catch (err) {
      console.error(err);
      alert("Failed to run what-if scenario comparison.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            <GitCompare className="h-6 w-6 text-amber-600" />
            Disaster What-If & Mitigation Scenario Analyzer
          </h1>
          <p className="text-sm text-slate-500">
            Compare unmitigated disaster accumulation versus rapid-clearance, contractor fleet deployment, and emergency treatment interventions.
          </p>
        </div>

        <button
          onClick={runComparison}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-medium text-sm rounded-lg shadow-sm transition disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Run Scenario Comparison
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
          <div className="flex items-center justify-between border-b pb-3">
            <h3 className="font-bold text-slate-900 flex items-center gap-2 text-sm">
              <span className="w-3 h-3 rounded-full bg-red-500 inline-block" />
              Scenario A: Unmitigated Baseline Disaster
            </h3>
            <span className="text-xs bg-red-50 text-red-700 font-semibold px-2 py-0.5 rounded">High Disruption</span>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <label className="font-medium text-slate-700 block mb-1">Road Accessibility: {baseParams.road_access_pct}%</label>
              <input
                type="range"
                min="10"
                max="100"
                value={baseParams.road_access_pct}
                onChange={(e) => setBaseParams({ ...baseParams, road_access_pct: e.target.value })}
                className="w-full accent-red-600"
              />
            </div>

            <div>
              <label className="font-medium text-slate-700 block mb-1">Collection Efficiency: {baseParams.collection_efficiency_pct}%</label>
              <input
                type="range"
                min="10"
                max="100"
                value={baseParams.collection_efficiency_pct}
                onChange={(e) => setBaseParams({ ...baseParams, collection_efficiency_pct: e.target.value })}
                className="w-full accent-red-600"
              />
            </div>

            <div>
              <label className="font-medium text-slate-700 block mb-1">Treatment Capacity: {baseParams.treatment_capacity_pct}%</label>
              <input
                type="range"
                min="10"
                max="100"
                value={baseParams.treatment_capacity_pct}
                onChange={(e) => setBaseParams({ ...baseParams, treatment_capacity_pct: e.target.value })}
                className="w-full accent-red-600"
              />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
          <div className="flex items-center justify-between border-b pb-3">
            <h3 className="font-bold text-slate-900 flex items-center gap-2 text-sm">
              <span className="w-3 h-3 rounded-full bg-green-500 inline-block" />
              Scenario B: Mitigated / Rapid Response Strategy
            </h3>
            <span className="text-xs bg-green-50 text-green-700 font-semibold px-2 py-0.5 rounded">Reinforced Response</span>
          </div>

          <div className="space-y-3 text-xs">
            <div>
              <label className="font-medium text-slate-700 block mb-1">Road Accessibility: {scenParams.road_access_pct}%</label>
              <input
                type="range"
                min="10"
                max="100"
                value={scenParams.road_access_pct}
                onChange={(e) => setScenParams({ ...scenParams, road_access_pct: e.target.value })}
                className="w-full accent-green-600"
              />
            </div>

            <div>
              <label className="font-medium text-slate-700 block mb-1">Collection Efficiency: {scenParams.collection_efficiency_pct}%</label>
              <input
                type="range"
                min="10"
                max="100"
                value={scenParams.collection_efficiency_pct}
                onChange={(e) => setScenParams({ ...scenParams, collection_efficiency_pct: e.target.value })}
                className="w-full accent-green-600"
              />
            </div>

            <div>
              <label className="font-medium text-slate-700 block mb-1">Treatment Capacity: {scenParams.treatment_capacity_pct}%</label>
              <input
                type="range"
                min="10"
                max="100"
                value={scenParams.treatment_capacity_pct}
                onChange={(e) => setScenParams({ ...scenParams, treatment_capacity_pct: e.target.value })}
                className="w-full accent-green-600"
              />
            </div>
          </div>
        </div>
      </div>

      {comparison && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-6">
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-green-600" />
            Mitigation Impact Results & Comparative Delta
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-xs text-slate-500 font-semibold block">Baseline Peak Backlog</span>
              <span className="text-2xl font-bold text-red-600 block mt-1">
                {comparison.baseline?.peak_accumulated_waste_tonnes} T
              </span>
              <span className="text-xs text-slate-500">Unmitigated maximum accumulation</span>
            </div>

            <div className="p-4 rounded-xl bg-green-50 border border-green-200">
              <span className="text-xs text-green-700 font-semibold block">Mitigated Peak Backlog</span>
              <span className="text-2xl font-bold text-green-700 block mt-1">
                {comparison.scenario?.peak_accumulated_waste_tonnes} T
              </span>
              <span className="text-xs text-green-600">With clearance & contractor fleet</span>
            </div>

            <div className="p-4 rounded-xl bg-amber-50 border border-amber-200">
              <span className="text-xs text-amber-700 font-semibold block">Backlog Reduction</span>
              <span className="text-2xl font-bold text-amber-800 block mt-1">
                {comparison.delta?.peak_accumulation_percentage}%
              </span>
              <span className="text-xs text-amber-700 font-medium">Reduction in street waste accumulation</span>
            </div>
          </div>

          <div className="p-4 bg-slate-100/70 rounded-lg text-xs text-slate-700">
            <strong>System Impact Summary: </strong>
            {comparison.explanation}
          </div>
        </div>
      )}
    </div>
  );
}
