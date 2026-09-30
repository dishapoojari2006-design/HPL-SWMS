import React, { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { LocationProvider } from "./context/LocationContext";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import ChatbotDrawer from "./components/ChatbotDrawer";

// Pages
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import CalculatorPage from "./pages/CalculatorPage";
import HistoricalWastePage from "./pages/HistoricalWastePage";
import ForecastPage from "./pages/ForecastPage";
import SimulationPage from "./pages/SimulationPage";
import GISPage from "./pages/GISPage";
import DataQualityPage from "./pages/DataQualityPage";
import WizardPage from "./pages/WizardPage";
import ReportsPage from "./pages/ReportsPage";
import UsersPage from "./pages/UsersPage";
import AuditLogsPage from "./pages/AuditLogsPage";

const ProtectedLayout = () => {
  const { user, hasRole } = useAuth();
  const [chatOpen, setChatOpen] = useState(false);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="app-shell">
      <Navbar onOpenChat={() => setChatOpen(true)} />
      <div className="app-body">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/calculator" element={<CalculatorPage />} />
            <Route path="/history" element={<HistoricalWastePage />} />
            <Route path="/forecast" element={<ForecastPage />} />
            <Route path="/simulation" element={<SimulationPage />} />
            <Route path="/gis" element={<GISPage />} />
            <Route path="/data-quality" element={<DataQualityPage />} />
            <Route
              path="/wizard"
              element={
                hasRole("SUPER_ADMIN", "ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY", "PLANNER", "OPERATOR") ? (
                  <WizardPage />
                ) : (
                  <Navigate to="/" replace />
                )
              }
            />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/users" element={<UsersPage />} />
            <Route path="/audit-logs" element={<AuditLogsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
      <ChatbotDrawer isOpen={chatOpen} onClose={() => setChatOpen(false)} />
    </div>
  );
};

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <LocationProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/*" element={<ProtectedLayout />} />
          </Routes>
        </LocationProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
