import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Shield, Lock, Mail, Eye, EyeOff, AlertCircle } from "lucide-react";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState("admin@swms.org");
  const [password, setPassword] = useState("Password123!");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Authentication failed. Please verify credentials.");
    } finally {
      setLoading(false);
    }
  };

  const quickLogin = (eMail, pwd) => {
    setEmail(eMail);
    setPassword(pwd);
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="login-logo">SWMS</div>
          <h2>Smart Waste Management Simulator</h2>
          <p>National Municipal & Panchayat Planning Portal</p>
        </div>

        {error && (
          <div className="error-banner">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label>Authorized Email Address</label>
            <div className="input-wrapper">
              <Mail size={16} className="input-icon" />
              <input
                type="email"
                required
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

          <button type="submit" className="login-submit-btn" disabled={loading}>
            {loading ? "Authenticating System Access..." : "Sign In to Simulator"}
          </button>
        </form>

        <div className="quick-roles">
          <span className="quick-title">Quick Role Preview (Click to Populate):</span>
          <div className="role-chips">
            <button type="button" onClick={() => quickLogin("admin@swms.org", "Password123!")}>
              Super Admin
            </button>
            <button type="button" onClick={() => quickLogin("municipal@swms.org", "Password123!")}>
              Municipal Comm.
            </button>
            <button type="button" onClick={() => quickLogin("panchayat@swms.org", "Password123!")}>
              Panchayat Officer
            </button>
            <button type="button" onClick={() => quickLogin("planner@swms.org", "Password123!")}>
              Urban Planner
            </button>
            <button type="button" onClick={() => quickLogin("viewer@swms.org", "Password123!")}>
              Citizen Viewer
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
