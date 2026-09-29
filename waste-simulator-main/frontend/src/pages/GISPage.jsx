import React, { useState, useEffect } from "react";
import { useLocation } from "../context/LocationContext";
import { gisService } from "../api/services";
import { Map, Layers, CheckCircle2, AlertCircle, RefreshCw } from "lucide-react";
import { MapContainer, TileLayer, Marker, Popup, Polygon, CircleMarker } from "react-leaflet";
import "leaflet/dist/leaflet.css";

export default function GISPage() {
  const { selectedLocation } = useLocation();
  const [layers, setLayers] = useState(null);
  const [enrichment, setEnrichment] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadGIS = () => {
    if (!selectedLocation) return;
    setLoading(true);
    Promise.all([
      gisService.getLayers(selectedLocation.id),
      gisService.enrich(selectedLocation.id),
    ])
      .then(([lRes, eRes]) => {
        setLayers(lRes.data);
        setEnrichment(eRes.data);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadGIS();
  }, [selectedLocation]);

  if (!selectedLocation) return <div className="page-loading">Please select an administrative location.</div>;

  const lat = selectedLocation.latitude || 13.3409;
  const lng = selectedLocation.longitude || 74.7421;

  return (
    <div className="gis-view">
      <div className="page-header">
        <div>
          <h2>GIS Geospatial & Boundary Visualizer</h2>
          <p>Interactive spatial mapping with PostGIS boundary integration</p>
        </div>
        <button onClick={loadGIS} className="refresh-btn">
          <RefreshCw size={16} /> Reload GIS Layers
        </button>
      </div>

      {/* GIS Enrichment Honest Status Card */}
      <div className="reconcile-card">
        <div className="rec-header">
          {enrichment?.enrichment_status === "ENRICHED" ? (
            <CheckCircle2 size={20} className="text-emerald-500" />
          ) : (
            <AlertCircle size={20} className="text-amber-500" />
          )}
          <div>
            <h3>Geospatial Data Status: <strong>{enrichment?.enrichment_status || "UNAVAILABLE"}</strong></h3>
            <p>{enrichment?.notes || "GIS enrichment layers retrieved."}</p>
            <span className="subtext">Spatial Source: {enrichment?.source || "Local ULB Spatial Index"}</span>
          </div>
        </div>
      </div>

      {/* Leaflet Map Display */}
      <div className="map-wrapper">
        <MapContainer center={[lat, lng]} zoom={13} style={{ height: "550px", width: "100%", borderRadius: "10px" }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Location Center Marker */}
          <CircleMarker center={[lat, lng]} radius={10} pathOptions={{ color: "#10b981", fillColor: "#10b981", fillOpacity: 0.8 }}>
            <Popup>
              <strong>{selectedLocation.name}</strong><br />
              Type: {selectedLocation.location_type}<br />
              Terrain: {selectedLocation.terrain || "Plain"}
            </Popup>
          </CircleMarker>

          {/* Render Features from GeoJSON */}
          {layers?.features && layers.features.map((f, idx) => {
            if (f.geometry?.type === "Point") {
              const coords = f.geometry.coordinates;
              const isFacility = f.properties?.layer === "FACILITIES";
              return (
                <CircleMarker
                  key={idx}
                  center={[coords[1], coords[0]]}
                  radius={isFacility ? 8 : 6}
                  pathOptions={{
                    color: isFacility ? "#3b82f6" : "#f59e0b",
                    fillColor: isFacility ? "#3b82f6" : "#f59e0b",
                    fillOpacity: 0.7,
                  }}
                >
                  <Popup>
                    <strong>{f.properties?.name}</strong><br />
                    Layer: {f.properties?.layer}<br />
                    {f.properties?.capacity_kg_day && `Capacity: ${f.properties.capacity_kg_day} kg/day`}
                  </Popup>
                </CircleMarker>
              );
            }
            return null;
          })}
        </MapContainer>
      </div>
    </div>
  );
}
