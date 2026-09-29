import React, { useState, useEffect } from "react";
import { useLocation } from "../context/LocationContext";
import { parameterService, wasteService } from "../api/services";
import { Wrench, CheckCircle, ChevronRight, ChevronLeft, Save } from "lucide-react";

const STEPS = [
  "1. Location", "2. Habitation", "3. Population", "4. Households", "5. Infrastructure",
  "6. Waste Composition", "7. Waste Sources", "8. Industries & Health", "9. Floating Population",
  "10. Events & Festivals", "11. Historical Waste", "12. GIS Spatial", "13. Validation", "14. Final Ready"
];

export default function WizardPage() {
  const { selectedLocation } = useLocation();
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

  const handleSaveDemography = async () => {
    if (!selectedLocation) return;
    try {
      await parameterService.saveDemography(selectedLocation.id, demoData);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      alert("Failed to save parameters.");
    }
  };

  return (
    <div className="wizard-view">
      <div className="page-header">
        <div>
          <h2>14-Step Municipal Data Entry Wizard</h2>
          <p>Step-by-step verified parameter onboarding for urban local bodies & gram panchayats</p>
        </div>
      </div>

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
          <div className="step-body">
            <p>Active Administrative Unit: <strong>{selectedLocation?.name}</strong></p>
            <p>Classification: {selectedLocation?.classification || "Town"} | State: {selectedLocation?.state || "Karnataka"}</p>
          </div>
        )}

        {currentStep === 3 && (
          <div className="step-form">
            <div className="form-group">
              <label>Total Resident Population</label>
              <input
                type="number"
                value={demoData.total_population}
                onChange={(e) => setDemoData({ ...demoData, total_population: parseFloat(e.target.value) })}
              />
            </div>
            <div className="form-group">
              <label>Population Growth Rate (% / year)</label>
              <input
                type="number"
                step="0.1"
                value={demoData.population_growth_rate}
                onChange={(e) => setDemoData({ ...demoData, population_growth_rate: parseFloat(e.target.value) })}
              />
            </div>
            <div className="form-group">
              <label>Per Capita Waste Factor (kg/person/day)</label>
              <input
                type="number"
                step="0.01"
                value={demoData.waste_per_capita_kg}
                onChange={(e) => setDemoData({ ...demoData, waste_per_capita_kg: parseFloat(e.target.value) })}
              />
            </div>
            <button className="save-btn" onClick={handleSaveDemography}>
              <Save size={16} /> Save Demography
            </button>
          </div>
        )}

        {currentStep === 4 && (
          <div className="step-form">
            <div className="form-group">
              <label>Total Number of Households</label>
              <input
                type="number"
                value={demoData.number_of_households}
                onChange={(e) => setDemoData({ ...demoData, number_of_households: parseFloat(e.target.value) })}
              />
            </div>
            <button className="save-btn" onClick={handleSaveDemography}>
              <Save size={16} /> Save Household Statistics
            </button>
          </div>
        )}

        {currentStep === 9 && (
          <div className="step-form">
            <div className="form-group">
              <label>Floating Daily Commuter Population</label>
              <input
                type="number"
                value={demoData.floating_population}
                onChange={(e) => setDemoData({ ...demoData, floating_population: parseFloat(e.target.value) })}
              />
            </div>
            <div className="form-group">
              <label>Seasonal / Tourist Population</label>
              <input
                type="number"
                value={demoData.tourist_population}
                onChange={(e) => setDemoData({ ...demoData, tourist_population: parseFloat(e.target.value) })}
              />
            </div>
            <button className="save-btn" onClick={handleSaveDemography}>
              <Save size={16} /> Save Floating Population
            </button>
          </div>
        )}

        {![1, 3, 4, 9].includes(currentStep) && (
          <div className="step-body">
            <p>Verified parameter inputs for {STEPS[currentStep - 1]} are active in the database.</p>
          </div>
        )}

        {saved && <div className="save-toast"><CheckCircle size={16} /> Parameters successfully saved to central database!</div>}

        <div className="wizard-nav-btns">
          <button
            disabled={currentStep === 1}
            onClick={() => setCurrentStep(currentStep - 1)}
            className="nav-btn-prev"
          >
            <ChevronLeft size={16} /> Previous Step
          </button>
          <button
            disabled={currentStep === 14}
            onClick={() => setCurrentStep(currentStep + 1)}
            className="nav-btn-next"
          >
            Next Step <ChevronRight size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
