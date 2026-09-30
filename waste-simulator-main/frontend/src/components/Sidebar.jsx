import React from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  LayoutDashboard,
  Calculator,
  History,
  TrendingUp,
  Sliders,
  Map,
  FileSpreadsheet,
  CheckCircle2,
  Users,
  ScrollText,
  Building2,
  Layers,
  Wrench
} from "lucide-react";

export default function Sidebar() {
  const { hasRole } = useAuth();

  return (
    <aside className="sidebar">
      <div className="sidebar-group">
        <div className="group-title">EXECUTIVE OVERVIEW</div>
        <NavLink to="/" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
          <LayoutDashboard size={18} />
          <span>Dashboard</span>
        </NavLink>
        <NavLink to="/gis" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
          <Map size={18} />
          <span>GIS Spatial Viewer</span>
        </NavLink>
        <NavLink to="/data-quality" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
          <CheckCircle2 size={18} />
          <span>Data Quality Audit</span>
        </NavLink>
      </div>

      <div className="sidebar-group">
        <div className="group-title">PLANNING & DATA ENTRY</div>
        {hasRole("SUPER_ADMIN", "ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER", "OPERATOR") && (
          <NavLink to="/wizard" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
            <Wrench size={18} />
            <span>Data Setup Wizard</span>
          </NavLink>
        )}
        <NavLink to="/calculator" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
          <Calculator size={18} />
          <span>Methods A–H Calculator</span>
        </NavLink>
      </div>

      <div className="sidebar-group">
        <div className="group-title">ANALYTICS & FORECASTING</div>
        <NavLink to="/history" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
          <History size={18} />
          <span>Historical Time Series</span>
        </NavLink>
        <NavLink to="/forecast" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
          <TrendingUp size={18} />
          <span>Time-Series Forecast</span>
        </NavLink>
        <NavLink to="/simulation" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
          <Sliders size={18} />
          <span>20-Yr Simulation</span>
        </NavLink>
      </div>

      <div className="sidebar-group">
        <div className="group-title">GOVERNANCE & REPORTS</div>
        <NavLink to="/reports" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
          <FileSpreadsheet size={18} />
          <span>Reports & Compliance</span>
        </NavLink>
        {hasRole("SUPER_ADMIN") && (
          <NavLink to="/users" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
            <Users size={18} />
            <span>User Management</span>
          </NavLink>
        )}
        {hasRole("SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY") && (
          <NavLink to="/audit-logs" className={({ isActive }) => `sidebar-link ${isActive ? "active" : ""}`}>
            <ScrollText size={18} />
            <span>Audit Logs</span>
          </NavLink>
        )}
      </div>
    </aside>
  );
}
