import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useLocation } from "../context/LocationContext";
import { useAuth } from "../context/AuthContext";
import { parameterService } from "../api/services";
import { Wrench, CheckCircle, ChevronRight, ChevronLeft, Save, AlertTriangle, ShieldAlert, Lock } from "lucide-react";

const STEPS = [
  "Location", "Habitation", "Population", "Households", "Infrastructure",
  "Waste Composition", "Waste Sources", "Industries & Health", "Floating Population",
  "Events & Festivals", "Historical Waste", "GIS Spatial", "Validation", "Final Ready"
];

export default function WizardPage() {
  const navigate = useNavigate();
  const { selectedLocation } = useLocation();
  const { user } = useAuth();
  const isViewer = user?.role === "VIEWER";

  const [currentStep, setCurrentStep] = useState(1);
  const [demoData, setDemoData] = useState({
    total_population: 25000,
    number_of_households: 5500,
    waste_per_capita_kg: 0.50,
    population_growth_rate: 2.0,
    floating_population: 2000,
    tourist_population: 1500,
  });
  const [saved, setSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Field validation rules
  const getStepValidationErrors = (step) => {
    const errors = {};
    if (step === 3) {
      if (demoData.total_population === undefined || demoData.total_population === "" || isNaN(demoData.total_population)) {
        errors.total_population = "Resident Population is required.";
      } else if (demoData.total_population < 100 || demoData.total_population > 20000000) {
        errors.total_population = "Population must be between 100 and 20,000,000 residents.";
      }

      if (demoData.population_growth_rate === undefined || demoData.population_growth_rate === "" || isNaN(demoData.population_growth_rate)) {
        errors.population_growth_rate = "Growth rate is required.";
      } else if (demoData.population_growth_rate < -5 || demoData.population_growth_rate > 15) {
        errors.population_growth_rate = "Growth rate must be between -5% and +15% per year.";
      }

      if (demoData.waste_per_capita_kg === undefined || demoData.waste_per_capita_kg === "" || isNaN(demoData.waste_per_capita_kg)) {
        errors.waste_per_capita_kg = "Per capita waste factor is required.";
      } else if (demoData.waste_per_capita_kg < 0.1 || demoData.waste_per_capita_kg > 3.5) {
        errors.waste_per_capita_kg = "Per capita factor must be between 0.10 kg and 3.50 kg/person/day.";
      }
    } else if (step === 4) {
      if (demoData.number_of_households === undefined || demoData.number_of_households === "" || isNaN(demoData.number_of_households)) {
        errors.number_of_households = "Total Households count is required.";
      } else if (demoData.number_of_households < 10 || demoData.number_of_households > 5000000) {
        errors.number_of_households = "Households count must be between 10 and 5,000,000.";
      }
    } else if (step === 9) {
      if (demoData.floating_population === undefined || demoData.floating_population === "" || isNaN(demoData.floating_population)) {
        errors.floating_population = "Floating Commuter Population is required.";
      } else if (demoData.floating_population < 0 || demoData.floating_population > 5000000) {
        errors.floating_population = "Floating population cannot be negative or exceed 5,000,000.";
      }

      if (demoData.tourist_population === undefined || demoData.tourist_population === "" || isNaN(demoData.tourist_population)) {
        errors.tourist_population = "Tourist Population is required.";
      } else if (demoData.tourist_population < 0 || demoData.tourist_population > 5000000) {
        errors.tourist_population = "Tourist population cannot be negative or exceed 5,000,000.";
      }
    }
    return errors;
  };

  const currentErrors = getStepValidationErrors(currentStep);
  const isValidStep = Object.keys(currentErrors).length === 0;

  const handleSaveDemography = async () => {
    if (!selectedLocation || !isValidStep) return;
    setIsSaving(true);
    try {
      await parameterService.saveDemography(selectedLocation.id, demoData);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      alert("Failed to save parameters.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="wizard-view">
      <div className="page-header">
        <div>
          <h2>Municipal Data Setup Wizard</h2>
          <p>Step-by-step verified parameter onboarding for urban local bodies & gram panchayats</p>
        </div>
      </div>

      {isViewer && (
        <div style={{ background: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#f87171', padding: '12px 16px', borderRadius: 8, display: 'flex', alignItems: 'center', gap: 10, fontSize: 13, fontWeight: 600, marginBottom: 16 }}>
          <Lock size={16} />
          <span><strong>Read-Only Mode:</strong> Your account is assigned the <em>Viewer</em> role. Parameter modification and saving are restricted to Field Operators and Administrators.</span>
        </div>
      )}

      {/* Step Indicator Bar */}
      <div className="wizard-steps-bar">
        {STEPS.map((s, idx) => (
          <button
            key={idx}
            className={`wizard-step-chip ${currentStep === idx + 1 ? "active" : currentStep > idx + 1 ? "done" : ""}`}
            onClick={() => setCurrentStep(idx + 1)}
          >
            {s}
          </button>
        ))}
      </div>

      <div className="wizard-content-card">
        <h3>Step {currentStep}: {STEPS[currentStep - 1]}</h3>

        {currentStep === 1 && (
          <div className="step-body" style={{ padding: "16px 0" }}>
            <p style={{ marginBottom: "6px" }}>Active Administrative Unit: <strong>{selectedLocation?.name}</strong></p>
            <p>Classification: {selectedLocation?.classification || "Town"} | State: {selectedLocation?.state || "Karnataka"}</p>
          </div>
        )}

        {currentStep === 3 && (
          <div className="step-form" style={{ marginTop: "16px" }}>
            <div className="form-group" style={{ marginBottom: "16px" }}>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "600", color: "#cbd5e1", marginBottom: "6px" }}>
                Total Resident Population *
              </label>
              <input
                type="number"
                value={demoData.total_population ?? ""}
                onChange={(e) => setDemoData({ ...demoData, total_population: e.target.value === "" ? "" : parseFloat(e.target.value) })}
                disabled={isViewer}
                style={{
                  width: "100%",
                  padding: "10px 14px",
                  background: "var(--bg-tertiary)",
                  border: `1px solid ${currentErrors.total_population ? "#ef4444" : "var(--border-color)"}`,
                  color: "#fff",
                  borderRadius: "6px",
                  outline: "none"
                }}
              />
              {currentErrors.total_population && (
                <span style={{ fontSize: "12px", color: "#f87171", display: "flex", alignItems: "center", gap: "4px", marginTop: "4px" }}>
                  <AlertTriangle size={14} /> {currentErrors.total_population}
                </span>
              )}
            </div>

            <div className="form-group" style={{ marginBottom: "16px" }}>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "600", color: "#cbd5e1", marginBottom: "6px" }}>
                Population Growth Rate (% / year) *
              </label>
              <input
                type="number"
                step="0.1"
                value={demoData.population_growth_rate ?? ""}
                onChange={(e) => setDemoData({ ...demoData, population_growth_rate: e.target.value === "" ? "" : parseFloat(e.target.value) })}
                disabled={isViewer}
                style={{
                  width: "100%",
                  padding: "10px 14px",
                  background: "var(--bg-tertiary)",
                  border: `1px solid ${currentErrors.population_growth_rate ? "#ef4444" : "var(--border-color)"}`,
                  color: "#fff",
                  borderRadius: "6px",
                  outline: "none"
                }}
              />
              {currentErrors.population_growth_rate && (
                <span style={{ fontSize: "12px", color: "#f87171", display: "flex", alignItems: "center", gap: "4px", marginTop: "4px" }}>
                  <AlertTriangle size={14} /> {currentErrors.population_growth_rate}
                </span>
              )}
            </div>

            <div className="form-group" style={{ marginBottom: "20px" }}>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "600", color: "#cbd5e1", marginBottom: "6px" }}>
                Per Capita Waste Factor (kg/person/day) *
              </label>
              <input
                type="number"
                step="0.01"
                value={demoData.waste_per_capita_kg ?? ""}
                onChange={(e) => setDemoData({ ...demoData, waste_per_capita_kg: e.target.value === "" ? "" : parseFloat(e.target.value) })}
                disabled={isViewer}
                style={{
                  width: "100%",
                  padding: "10px 14px",
                  background: "var(--bg-tertiary)",
                  border: `1px solid ${currentErrors.waste_per_capita_kg ? "#ef4444" : "var(--border-color)"}`,
                  color: "#fff",
                  borderRadius: "6px",
                  outline: "none"
                }}
              />
              {currentErrors.waste_per_capita_kg && (
                <span style={{ fontSize: "12px", color: "#f87171", display: "flex", alignItems: "center", gap: "4px", marginTop: "4px" }}>
                  <AlertTriangle size={14} /> {currentErrors.waste_per_capita_kg}
                </span>
              )}
            </div>

            <button
              className="save-btn"
              onClick={handleSaveDemography}
              disabled={!isValidStep || isSaving || isViewer}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "10px 20px",
                background: (isValidStep && !isViewer) ? "linear-gradient(135deg, #10b981 0%, #059669 100%)" : "#334155",
                color: (isValidStep && !isViewer) ? "#fff" : "#94a3b8",
                border: "none",
                borderRadius: "6px",
                fontWeight: "600",
                cursor: (isValidStep && !isViewer) ? "pointer" : "not-allowed",
                opacity: (isValidStep && !isViewer) ? 1 : 0.6
              }}
            >
              <Save size={16} /> {isSaving ? "Saving..." : isViewer ? "Read-Only Mode" : "Save Demography"}
            </button>
          </div>
        )}

        {currentStep === 4 && (
          <div className="step-form" style={{ marginTop: "16px" }}>
            <div className="form-group" style={{ marginBottom: "20px" }}>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "600", color: "#cbd5e1", marginBottom: "6px" }}>
                Total Number of Households *
              </label>
              <input
                type="number"
                value={demoData.number_of_households ?? ""}
                onChange={(e) => setDemoData({ ...demoData, number_of_households: e.target.value === "" ? "" : parseFloat(e.target.value) })}
                disabled={isViewer}
                style={{
                  width: "100%",
                  padding: "10px 14px",
                  background: "var(--bg-tertiary)",
                  border: `1px solid ${currentErrors.number_of_households ? "#ef4444" : "var(--border-color)"}`,
                  color: "#fff",
                  borderRadius: "6px",
                  outline: "none"
                }}
              />
              {currentErrors.number_of_households && (
                <span style={{ fontSize: "12px", color: "#f87171", display: "flex", alignItems: "center", gap: "4px", marginTop: "4px" }}>
                  <AlertTriangle size={14} /> {currentErrors.number_of_households}
                </span>
              )}
            </div>

            <button
              className="save-btn"
              onClick={handleSaveDemography}
              disabled={!isValidStep || isSaving || isViewer}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "10px 20px",
                background: (isValidStep && !isViewer) ? "linear-gradient(135deg, #10b981 0%, #059669 100%)" : "#334155",
                color: (isValidStep && !isViewer) ? "#fff" : "#94a3b8",
                border: "none",
                borderRadius: "6px",
                fontWeight: "600",
                cursor: (isValidStep && !isViewer) ? "pointer" : "not-allowed",
                opacity: (isValidStep && !isViewer) ? 1 : 0.6
              }}
            >
              <Save size={16} /> {isSaving ? "Saving..." : isViewer ? "Read-Only Mode" : "Save Household Statistics"}
            </button>
          </div>
        )}

        {currentStep === 9 && (
          <div className="step-form" style={{ marginTop: "16px" }}>
            <div className="form-group" style={{ marginBottom: "16px" }}>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "600", color: "#cbd5e1", marginBottom: "6px" }}>
                Floating Daily Commuter Population *
              </label>
              <input
                type="number"
                value={demoData.floating_population ?? ""}
                onChange={(e) => setDemoData({ ...demoData, floating_population: e.target.value === "" ? "" : parseFloat(e.target.value) })}
                disabled={isViewer}
                style={{
                  width: "100%",
                  padding: "10px 14px",
                  background: "var(--bg-tertiary)",
                  border: `1px solid ${currentErrors.floating_population ? "#ef4444" : "var(--border-color)"}`,
                  color: "#fff",
                  borderRadius: "6px",
                  outline: "none"
                }}
              />
              {currentErrors.floating_population && (
                <span style={{ fontSize: "12px", color: "#f87171", display: "flex", alignItems: "center", gap: "4px", marginTop: "4px" }}>
                  <AlertTriangle size={14} /> {currentErrors.floating_population}
                </span>
              )}
            </div>

            <div className="form-group" style={{ marginBottom: "20px" }}>
              <label style={{ display: "block", fontSize: "13px", fontWeight: "600", color: "#cbd5e1", marginBottom: "6px" }}>
                Seasonal / Tourist Population *
              </label>
              <input
                type="number"
                value={demoData.tourist_population ?? ""}
                onChange={(e) => setDemoData({ ...demoData, tourist_population: e.target.value === "" ? "" : parseFloat(e.target.value) })}
                disabled={isViewer}
                style={{
                  width: "100%",
                  padding: "10px 14px",
                  background: "var(--bg-tertiary)",
                  border: `1px solid ${currentErrors.tourist_population ? "#ef4444" : "var(--border-color)"}`,
                  color: "#fff",
                  borderRadius: "6px",
                  outline: "none"
                }}
              />
              {currentErrors.tourist_population && (
                <span style={{ fontSize: "12px", color: "#f87171", display: "flex", alignItems: "center", gap: "4px", marginTop: "4px" }}>
                  <AlertTriangle size={14} /> {currentErrors.tourist_population}
                </span>
              )}
            </div>

            <button
              className="save-btn"
              onClick={handleSaveDemography}
              disabled={!isValidStep || isSaving || isViewer}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "8px",
                padding: "10px 20px",
                background: (isValidStep && !isViewer) ? "linear-gradient(135deg, #10b981 0%, #059669 100%)" : "#334155",
                color: (isValidStep && !isViewer) ? "#fff" : "#94a3b8",
                border: "none",
                borderRadius: "6px",
                fontWeight: "600",
                cursor: (isValidStep && !isViewer) ? "pointer" : "not-allowed",
                opacity: (isValidStep && !isViewer) ? 1 : 0.6
              }}
            >
              <Save size={16} /> {isSaving ? "Saving..." : isViewer ? "Read-Only Mode" : "Save Floating Population"}
            </button>
          </div>
        )}

        {![1, 3, 4, 9].includes(currentStep) && (
          <div className="step-body" style={{ padding: "16px 0" }}>
            <p>Verified parameter inputs for <strong>{STEPS[currentStep - 1]}</strong> are active in the database.</p>
          </div>
        )}

        {saved && (
          <div className="save-toast" style={{ marginTop: "16px", padding: "10px 16px", borderRadius: "8px", background: "rgba(16, 185, 129, 0.15)", border: "1px solid #10b981", color: "#34d399", display: "inline-flex", alignItems: "center", gap: "8px", fontWeight: "600", fontSize: "13px" }}>
            <CheckCircle size={16} /> Saved!
          </div>
        )}

        {/* Global Step Navigation Bar */}
        <div className="wizard-nav-btns" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "24px", paddingTop: "16px", borderTop: "1px solid var(--border-color)" }}>
          <button
            disabled={currentStep === 1}
            onClick={() => setCurrentStep(currentStep - 1)}
            className="nav-btn-prev"
            style={{ opacity: currentStep === 1 ? 0.5 : 1, cursor: currentStep === 1 ? "not-allowed" : "pointer" }}
          >
            <ChevronLeft size={16} /> Previous Step
          </button>

          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "4px" }}>
            {currentStep < 14 ? (
              <button
                disabled={!isValidStep}
                onClick={() => isValidStep && setCurrentStep(currentStep + 1)}
                className="nav-btn-next"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "8px 18px",
                  background: isValidStep ? "var(--accent-emerald)" : "#334155",
                  color: isValidStep ? "#ffffff" : "#94a3b8",
                  border: "none",
                  borderRadius: "6px",
                  fontWeight: "600",
                  fontSize: "13px",
                  cursor: isValidStep ? "pointer" : "not-allowed",
                  opacity: isValidStep ? 1 : 0.6
                }}
              >
                Next Step <ChevronRight size={16} />
              </button>
            ) : (
              <button
                disabled={!isValidStep}
                onClick={() => isValidStep && navigate("/calculator")}
                className="nav-btn-next finish-btn"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "8px 18px",
                  background: isValidStep ? "linear-gradient(135deg, #10b981 0%, #059669 100%)" : "#334155",
                  color: isValidStep ? "#ffffff" : "#94a3b8",
                  border: "none",
                  borderRadius: "6px",
                  fontWeight: "600",
                  fontSize: "13px",
                  cursor: isValidStep ? "pointer" : "not-allowed",
                  opacity: isValidStep ? 1 : 0.6
                }}
              >
                Finish & Go to Calculator <ChevronRight size={16} />
              </button>
            )}

            {!isValidStep && (
              <span style={{ fontSize: "11px", color: "#f87171", display: "flex", alignItems: "center", gap: "4px" }}>
                <ShieldAlert size={13} /> Fix invalid fields above to unlock Next Step
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

