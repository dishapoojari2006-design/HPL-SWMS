import React, { useState, useEffect } from "react";
import { useLocationContext } from "../context/LocationContext";
import { shelterService } from "../api/services";
import { Home, Plus, Trash2 } from "lucide-react";

export default function EmergencySheltersPage() {
  const { selectedLocationId, selectedLocation } = useLocationContext();
  const [shelters, setShelters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const [formData, setFormData] = useState({
    name: "Taluk Community Relief Center",
    shelter_code: "SHELTER-01",
    capacity_persons: 500,
    current_population: 350,
    waste_per_person_kg_day: 0.50,
    status: "ACTIVE",
    source: "Taluk Relief Officer",
    notes: ""
  });

  const fetchShelters = async () => {
    if (!selectedLocationId) return;
    setLoading(true);
    try {
      const res = await shelterService.list(selectedLocationId);
      setShelters(res.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShelters();
  }, [selectedLocationId]);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await shelterService.create({
        ...formData,
        location_id: selectedLocationId,
        capacity_persons: parseInt(formData.capacity_persons, 10),
        current_population: parseInt(formData.current_population, 10),
        waste_per_person_kg_day: parseFloat(formData.waste_per_person_kg_day)
      });
      setShowModal(false);
      fetchShelters();
    } catch (err) {
      alert("Failed to register emergency shelter.");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this shelter record?")) return;
    try {
      await shelterService.delete(id);
      fetchShelters();
    } catch (err) {
      alert("Failed to delete shelter.");
    }
  };

  const totalShelterPop = shelters.reduce((sum, s) => sum + (s.current_population || 0), 0);
  const totalShelterWasteKg = shelters.reduce((sum, s) => sum + ((s.current_population || 0) * (s.waste_per_person_kg_day || 0.5)), 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 flex items-center gap-2">
            <Home className="h-6 w-6 text-amber-600" />
            Emergency Shelters & Relief Camps
          </h1>
          <p className="text-sm text-slate-500">
            Designated disaster shelters, population intake, and temporary camp waste generation for {selectedLocation?.name || "Selected Location"}.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-medium text-sm rounded-lg shadow-sm transition"
        >
          <Plus className="h-4 w-4" />
          Add Emergency Shelter
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 block">Total Active Shelters</span>
          <span className="text-2xl font-bold text-slate-900 mt-1 block">{shelters.length}</span>
          <span className="text-xs text-slate-400">Designated relief centers</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 block">Current Shelter Population</span>
          <span className="text-2xl font-bold text-amber-600 mt-1 block">{totalShelterPop.toLocaleString()}</span>
          <span className="text-xs text-slate-400">Temporarily accommodated persons</span>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 block">Daily Shelter Waste</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-2xl font-bold text-slate-900">{(totalShelterWasteKg / 1000).toFixed(2)}</span>
            <span className="text-xs text-slate-500">Tonnes/day</span>
          </div>
          <span className="text-xs text-slate-400">Calculated without double-counting</span>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200">
          <h3 className="text-sm font-bold text-slate-900">Designated Shelters List</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-slate-100 text-slate-700 font-semibold border-b border-slate-200">
              <tr>
                <th className="p-3">Shelter Name</th>
                <th className="p-3">Code</th>
                <th className="p-3">Capacity</th>
                <th className="p-3">Current Pop</th>
                <th className="p-3">Rate (kg/person/day)</th>
                <th className="p-3">Daily Waste (kg)</th>
                <th className="p-3">Status</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {shelters.length === 0 ? (
                <tr>
                  <td colSpan="8" className="text-center py-8 text-slate-400">
                    No emergency shelters recorded for this jurisdiction.
                  </td>
                </tr>
              ) : (
                shelters.map((sh) => (
                  <tr key={sh.id} className="hover:bg-slate-50">
                    <td className="p-3 font-semibold text-slate-900">{sh.name}</td>
                    <td className="p-3 text-slate-500">{sh.shelter_code || "—"}</td>
                    <td className="p-3">{sh.capacity_persons}</td>
                    <td className="p-3 font-medium text-amber-700">{sh.current_population}</td>
                    <td className="p-3">{sh.waste_per_person_kg_day} kg</td>
                    <td className="p-3 font-semibold">
                      {(sh.current_population * sh.waste_per_person_kg_day).toFixed(1)} kg
                    </td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded text-xs font-semibold bg-green-100 text-green-800">
                        {sh.status}
                      </span>
                    </td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => handleDelete(sh.id)}
                        className="text-slate-400 hover:text-red-600"
                        title="Delete shelter"
                      >
                        <Trash2 className="h-4 w-4 inline" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
              <Home className="h-5 w-5 text-amber-600" />
              Add Emergency Shelter / Relief Camp
            </h2>

            <form onSubmit={handleCreate} className="space-y-4 text-sm">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Shelter Name</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Shelter Code</label>
                  <input
                    type="text"
                    value={formData.shelter_code}
                    onChange={(e) => setFormData({ ...formData, shelter_code: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Status</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                  >
                    <option value="ACTIVE">ACTIVE</option>
                    <option value="STANDBY">STANDBY</option>
                    <option value="CLOSED">CLOSED</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Capacity (Persons)</label>
                  <input
                    type="number"
                    value={formData.capacity_persons}
                    onChange={(e) => setFormData({ ...formData, capacity_persons: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Current Population</label>
                  <input
                    type="number"
                    value={formData.current_population}
                    onChange={(e) => setFormData({ ...formData, current_population: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Waste per Person (kg/day)</label>
                <input
                  type="number"
                  step="0.05"
                  value={formData.waste_per_person_kg_day}
                  onChange={(e) => setFormData({ ...formData, waste_per_person_kg_day: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
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
                  Add Shelter
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
