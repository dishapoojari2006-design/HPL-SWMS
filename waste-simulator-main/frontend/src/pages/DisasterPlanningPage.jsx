import React, { useState, useEffect } from "react";
import { useLocationContext } from "../context/LocationContext";
import { disasterService } from "../api/services";
import { AlertTriangle, Plus, Trash2, Calendar, ShieldAlert } from "lucide-react";

export default function DisasterPlanningPage() {
  const { selectedLocationId, selectedLocation } = useLocationContext();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const [formData, setFormData] = useState({
    name: "Monsoon Surge 2026",
    disaster_type: "Flood",
    start_date: new Date().toISOString().split("T")[0],
    duration_days: 7,
    severity: "HIGH",
    warning_level: "ORANGE",
    affected_area_sqkm: 15.0,
    affected_population: 5000,
    displaced_population: 2000,
    temporary_population: 1000,
    phase: "DURING",
    status: "ACTIVE_DISASTER",
    source: "District Disaster Management Authority",
    notes: ""
  });

  const fetchEvents = async () => {
    if (!selectedLocationId) return;
    setLoading(true);
    try {
      const res = await disasterService.list(selectedLocationId);
      setEvents(res.data || []);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("Failed to load disaster records for this location.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [selectedLocationId]);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await disasterService.create({
        ...formData,
        location_id: selectedLocationId,
        duration_days: parseInt(formData.duration_days, 10),
        affected_area_sqkm: parseFloat(formData.affected_area_sqkm),
        affected_population: parseFloat(formData.affected_population),
        displaced_population: parseFloat(formData.displaced_population),
        temporary_population: parseFloat(formData.temporary_population)
      });
      setShowModal(false);
      fetchEvents();
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to register disaster event.");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this disaster record?")) return;
    try {
      await disasterService.delete(id);
      fetchEvents();
    } catch (err) {
      alert("Failed to delete disaster event.");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            <AlertTriangle className="h-6 w-6 text-amber-600" />
            Disaster & Environmental Emergency Planning
          </h1>
          <p className="text-sm text-slate-500">
            Active emergencies, monsoon flooding, cyclones, landslides, and disaster response planning for {selectedLocation?.name || "Selected Location"}.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-medium text-sm rounded-lg shadow-sm transition"
        >
          <Plus className="h-4 w-4" />
          Register Disaster Event
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-12 text-slate-500">Loading disaster records...</div>
      ) : events.length === 0 ? (
        <div className="bg-white border border-dashed border-slate-300 rounded-xl p-12 text-center">
          <ShieldAlert className="h-12 w-12 text-slate-400 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-800">No Disaster Events Logged</h3>
          <p className="text-sm text-slate-500 mt-1 max-w-md mx-auto">
            No active or planned natural calamities recorded for this jurisdiction. Register an event to model road blockage, shelter surge, and accumulation.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {events.map((ev) => (
            <div key={ev.id} className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 hover:border-amber-400 transition">
              <div className="flex items-start justify-between">
                <div>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                    ev.severity === "EXTREME" ? "bg-red-100 text-red-800" :
                    ev.severity === "HIGH" ? "bg-amber-100 text-amber-800" : "bg-blue-100 text-blue-800"
                  }`}>
                    {ev.severity} SEVERITY
                  </span>
                  <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700">
                    {ev.disaster_type}
                  </span>
                </div>
                <button
                  onClick={() => handleDelete(ev.id)}
                  className="text-slate-400 hover:text-red-600 p-1"
                  title="Delete event"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>

              <h3 className="text-lg font-bold text-slate-900 mt-3">{ev.name}</h3>
              <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                <Calendar className="h-3.5 w-3.5" />
                {ev.start_date} ({ev.duration_days} Days Duration)
              </p>

              <div className="mt-4 pt-3 border-t border-slate-100 grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-slate-400 block">Affected Pop</span>
                  <span className="font-semibold text-slate-700">{ev.affected_population?.toLocaleString()}</span>
                </div>
                <div>
                  <span className="text-slate-400 block">Shelter / Relocated</span>
                  <span className="font-semibold text-slate-700">{ev.temporary_population?.toLocaleString()}</span>
                </div>
                <div>
                  <span className="text-slate-400 block">Impacted Area</span>
                  <span className="font-semibold text-slate-700">{ev.affected_area_sqkm} sq km</span>
                </div>
                <div>
                  <span className="text-slate-400 block">Status</span>
                  <span className="font-semibold text-amber-700">{ev.status}</span>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                <span className="text-slate-400">Source: {ev.source}</span>
                <a
                  href={`/disaster-analysis?eventId=${ev.id}`}
                  className="text-amber-700 hover:text-amber-800 font-semibold inline-flex items-center gap-1"
                >
                  Analyze Impact &rarr;
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-amber-600" />
              Register Natural Calamity / Disaster Event
            </h2>

            <form onSubmit={handleCreate} className="space-y-4 text-sm">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Event Name</label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Disaster Type</label>
                  <select
                    value={formData.disaster_type}
                    onChange={(e) => setFormData({ ...formData, disaster_type: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500"
                  >
                    <option value="Flood">Flood / Inundation</option>
                    <option value="Flash Flood">Flash Flood</option>
                    <option value="Urban Flood">Urban Flood</option>
                    <option value="Cyclone">Cyclone / Gale Storm</option>
                    <option value="Landslide">Landslide / Debris Flow</option>
                    <option value="Drought">Drought</option>
                    <option value="Earthquake">Earthquake</option>
                    <option value="Tsunami">Tsunami / Coastal Surge</option>
                    <option value="Extreme Heat">Extreme Heatwave</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Start Date</label>
                  <input
                    type="date"
                    required
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Duration (Days)</label>
                  <input
                    type="number"
                    min="1"
                    max="90"
                    value={formData.duration_days}
                    onChange={(e) => setFormData({ ...formData, duration_days: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Severity</label>
                  <select
                    value={formData.severity}
                    onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500"
                  >
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                    <option value="EXTREME">EXTREME</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Warning Level</label>
                  <select
                    value={formData.warning_level}
                    onChange={(e) => setFormData({ ...formData, warning_level: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500"
                  >
                    <option value="GREEN">GREEN (Watch)</option>
                    <option value="YELLOW">YELLOW (Alert)</option>
                    <option value="ORANGE">ORANGE (Preparedness)</option>
                    <option value="RED">RED (Emergency Action)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Affected Area (sq km)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.affected_area_sqkm}
                    onChange={(e) => setFormData({ ...formData, affected_area_sqkm: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Affected Population</label>
                  <input
                    type="number"
                    value={formData.affected_population}
                    onChange={(e) => setFormData({ ...formData, affected_population: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-medium"
                >
                  Save & Register
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
