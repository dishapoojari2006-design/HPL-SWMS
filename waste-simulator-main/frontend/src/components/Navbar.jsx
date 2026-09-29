import React from "react";
import { useAuth } from "../context/AuthContext";
import { useLocation } from "../context/LocationContext";
import { Shield, MapPin, LogOut, User, Activity } from "lucide-react";

export default function Navbar({ onOpenChat }) {
  const { user, logout } = useAuth();
  const { locations, selectedLocation, selectLocationById } = useLocation();

  return (
    <header className="navbar">
      <div className="nav-left">
        <div className="logo-brand">
          <div className="logo-icon">SWMS</div>
          <div className="brand-meta">
            <h1>Smart Waste Management Simulator</h1>
            <span>National Decision-Support & Planning Platform</span>
          </div>
        </div>
      </div>

      <div className="nav-center">
        <div className="location-select-bar">
          <MapPin size={16} className="text-emerald-500" />
          <span className="loc-label">Active Planning Unit:</span>
          <select
            value={selectedLocation ? selectedLocation.id : ""}
            onChange={(e) => selectLocationById(e.target.value)}
            className="location-dropdown"
          >
            {locations.map((loc) => (
              <option key={loc.id} value={loc.id}>
                {loc.name} ({loc.location_type || "ULB"}) - {loc.district || "District"}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="nav-right">
        <button className="chat-btn" onClick={onOpenChat} title="Ask AI Planning Assistant">
          <Activity size={16} />
          <span>AI Assistant</span>
        </button>

        <div className="user-profile-badge">
          <Shield size={14} className="role-icon" />
          <div className="user-text">
            <span className="uname">{user?.name || "Officer"}</span>
            <span className="urole">{user?.role}</span>
          </div>
        </div>

        <button className="logout-btn" onClick={logout} title="Sign Out">
          <LogOut size={16} />
        </button>
      </div>
    </header>
  );
}
