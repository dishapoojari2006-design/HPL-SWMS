import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useLocation } from "../context/LocationContext";
import { Shield, Lock, Mail, Eye, EyeOff, AlertCircle } from "lucide-react";
import logoImg from "../assets/swms_logo.jpg";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const { refreshLocations } = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      await refreshLocations();
      navigate("/");
    } catch (err) {
      const detail = err.response?.data?.detail || "";
      if (detail.toLowerCase().includes("deactivated") || detail.toLowerCase().includes("exist or has been")) {
        setError("This account has been deactivated. Please contact your administrator.");
      } else {
        setError(detail || "Authentication failed. Please verify credentials.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div style={{ display: "flex", justifyContent: "center", marginBottom: "12px" }}>
            <img
              src={logoImg}
              alt="SWMS Eco-Node Logo"
              style={{
                width: "64px",
                height: "64px",
                borderRadius: "14px",
                objectFit: "cover",
                boxShadow: "0 4px 16px rgba(16, 185, 129, 0.4)",
                border: "2px solid rgba(16, 185, 129, 0.5)"
              }}
            />
          </div>
          <h2>Smart Waste Management Simulator</h2>
          <p>National Municipal & Panchayat Planning Portal</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form" autoComplete="off">
          <div className="form-group">
            <label>Authorized Email Address</label>
            <div className="input-wrapper">
              <Mail size={16} className="input-icon" />
              <input
                type="email"
                required
                autoComplete="off"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="officer@swms.org"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Security Password</label>
            <div className="input-wrapper">
              <Lock size={16} className="input-icon" />
              <input
                type={showPassword ? "text" : "password"}
                required
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
              <button
                type="button"
                className="eye-toggle"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {error && (
            <div style={{ marginBottom: "12px", textAlign: "center" }}>
              <span style={{ fontSize: "11px", color: "#f87171", fontWeight: "500", display: "inline-flex", alignItems: "center", gap: "4px" }}>
                <AlertCircle size={13} /> {error}
              </span>
            </div>
          )}

          <button type="submit" className="login-submit-btn" disabled={loading}>
            {loading ? "Authenticating System Access..." : "Sign In to Simulator"}
          </button>
        </form>
      </div>
    </div>
  );
}
