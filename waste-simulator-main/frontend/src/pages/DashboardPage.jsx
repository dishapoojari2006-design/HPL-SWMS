import React, { useEffect, useState } from "react";
import { useLocation } from "../context/LocationContext";
import { useAuth } from "../context/AuthContext";
import { wasteService, dataQualityService } from "../api/services";
import {
  Trash2,
  Truck,
  Building,
  CheckCircle2,
  AlertTriangle,
  Users,
  Activity,
  ArrowUpRight
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell
} from "recharts";

const COLORS = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6", "#64748b"];

export default function DashboardPage() {
  const { user } = useAuth();
  const { selectedLocation } = useLocation();
  const [data, setData] = useState(null);
  const [dataQuality, setDataQuality] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedLocation) return;
    setLoading(true);
    Promise.all([
      wasteService.calculateComprehensive(selectedLocation.id),
      dataQualityService.getReport(selectedLocation.id),
    ])
      .then(([wasteRes, dqRes]) => {
        setData(wasteRes.data);
        setDataQuality(dqRes.data);
      })
      .catch((err) => console.error("Error loading dashboard:", err))
      .finally(() => setLoading(false));
  }, [selectedLocation]);

  if (!selectedLocation) {
    return <div className="page-loading">Please select an administrative location above.</div>;
  }

  if (loading || !data) {
    return <div className="page-loading">Loading live municipal analytics...</div>;
  }

  const compositionData = [
    { name: "Organic / Food", value: data.composition?.organic_percent || 50 },
    { name: "Recyclable (Paper/Plastic/Metal)", value: (data.composition?.paper_percent || 10) + (data.composition?.plastic_percent || 10) + (data.composition?.metal_percent || 3) },
    { name: "Glass", value: data.composition?.glass_percent || 4 },
    { name: "Textile", value: data.composition?.textile_percent || 4 },
    { name: "E-Waste / Other", value: (data.composition?.ewaste_percent || 2) + (data.composition?.other_percent || 2) },
  ];

  const methodsComparison = [
    { name: "Method A (Person)", tonnes: data.method_a?.daily_tonnes || 0 },
    { name: "Method B (Household)", tonnes: data.method_b?.daily_tonnes || 0 },
    { name: "Method C (Weighbridge)", tonnes: data.method_c?.daily_tonnes || 0 },
    { name: "Source Aggregated", tonnes: (data.source_aggregated_daily_kg || 0) / 1000 },
  ];

  return (
    <div className="dashboard-view">
      <div className="dashboard-banner">
        <div>
          <h2>{data.location?.name} ({data.location?.location_type})</h2>
          <p>District: {data.location?.district || "N/A"} | State: {data.location?.state || "Karnataka"} | Terrain: {data.location?.terrain || "Plain"}</p>
        </div>
        <div className="banner-badge">
          <CheckCircle2 size={16} />
          <span>Reconciled Source of Truth: {data.reconciliation?.selected_method}</span>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="card-top">
            <span className="card-label">Daily Waste Generation</span>
            <Trash2 className="card-icon text-emerald-500" size={20} />
          </div>
          <div className="card-val">{data.reconciliation?.selected_estimate_tonnes} <span className="unit">T / day</span></div>
          <div className="card-sub">{Math.round((data.reconciliation?.selected_estimate_tonnes || 0) * 1000)} kg/day (Annual: {Math.round((data.reconciliation?.selected_estimate_tonnes || 0) * 365)} T)</div>
        </div>

        <div className="metric-card">
          <div className="card-top">
            <span className="card-label">Current Fleet Capacity</span>
            <Truck className="card-icon text-blue-500" size={20} />
          </div>
          <div className="card-val">{data.collection?.current_fleet_capacity_tonnes_day} <span className="unit">T / day</span></div>
          <div className={`card-sub ${data.collection?.collection_gap_kg_day > 0 ? "text-amber-500" : "text-emerald-500"}`}>
            {data.collection?.collection_gap_kg_day > 0 ? `Deficit: ${data.collection?.collection_gap_kg_day} kg/day` : "Adequate Collection Fleet"}
          </div>
        </div>

        <div className="metric-card">
          <div className="card-top">
            <span className="card-label">Treatment Capacity</span>
            <Building className="card-icon text-indigo-500" size={20} />
          </div>
          <div className="card-val">{data.treatment?.total_treatment_capacity_tonnes} <span className="unit">T / day</span></div>
          <div className={`card-sub ${data.treatment?.treatment_gap_kg > 0 ? "text-red-500" : "text-emerald-500"}`}>
            {data.treatment?.treatment_gap_kg > 0 ? `Processing Gap: ${data.treatment?.treatment_gap_kg} kg/day` : "100% Processing Capacity"}
          </div>
        </div>

        <div className="metric-card">
          <div className="card-top">
            <span className="card-label">Data Completeness</span>
            <Activity className="card-icon text-teal-500" size={20} />
          </div>
          <div className="card-val">{dataQuality?.completeness_percent}%</div>
          <div className="card-sub text-emerald-500">
            {dataQuality?.checklist?.filter(c => c.status).length} / {dataQuality?.checklist?.length} Modules Surveyed
          </div>
        </div>
      </div>

      {/* Visual Analytics */}
      <div className="charts-grid">
        <div className="chart-card">
          <div className="chart-header">
            <h3>Methods A–H Reconciliation Matrix</h3>
            <span className="subtext">Cross-validation against physical weighbridge</span>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={methodsComparison}>
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#fff" }} />
                <Bar dataKey="tonnes" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-header">
            <h3>Waste Composition Profile</h3>
            <span className="subtext">Empirical mass fraction breakdown</span>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={compositionData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                  {compositionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#fff" }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Facilities & Waste Sources Table */}
      <div className="section-card">
        <div className="chart-header">
          <h3>Registered Municipal Waste Processing Facilities</h3>
          <span className="subtext">Operational infrastructure connected to location</span>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Facility Name</th>
              <th>Type</th>
              <th>Design Capacity (kg/day)</th>
              <th>Current Intake</th>
              <th>Operating Status</th>
            </tr>
          </thead>
          <tbody>
            {data.facilities && data.facilities.length > 0 ? (
              data.facilities.map((fac) => (
                <tr key={fac.id}>
                  <td>{fac.name}</td>
                  <td><span className="badge-blue">{fac.facility_type}</span></td>
                  <td>{fac.capacity_kg_day} kg/day ({fac.capacity_kg_day / 1000} T)</td>
                  <td>{fac.current_utilization_kg_day || 0} kg/day</td>
                  <td><span className="badge-green">{fac.operating_status || "Active"}</span></td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5" className="text-center py-4 text-slate-400">No registered treatment facilities found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
