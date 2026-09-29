import React, { useState, useEffect } from "react";
import { useLocation } from "../context/LocationContext";
import { wasteService } from "../api/services";
import { Calculator, CheckCircle, Scale, Layers, AlertCircle } from "lucide-react";

export default function CalculatorPage() {
  const { selectedLocation } = useLocation();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedLocation) return;
    setLoading(true);
    wasteService.calculateComprehensive(selectedLocation.id)
      .then((res) => setResults(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [selectedLocation]);

  if (!selectedLocation) return <div className="page-loading">Please select an administrative location.</div>;
  if (loading || !results) return <div className="page-loading">Computing Methods A through H...</div>;

  const rec = results.reconciliation;

  return (
    <div className="calculator-view">
      <div className="page-header">
        <div>
          <h2>Methods A–H Waste Calculation & Cross-Reconciliation</h2>
          <p>Transparent multi-model estimation with automated deviation scoring</p>
        </div>
        <div className="reconciled-badge">
          <CheckCircle size={16} />
          <span>Selected Official Estimate: <strong>{rec?.selected_estimate_tonnes} T/day</strong></span>
        </div>
      </div>

      <div className="reconcile-card">
        <div className="rec-header">
          <Scale size={20} className="text-emerald-500" />
          <div>
            <h3>Official Reconciliation Rationale</h3>
            <p>{rec?.reconciliation_reason}</p>
          </div>
        </div>
      </div>

      {/* Methods A - H Grid */}
      <div className="methods-grid">
        <div className="method-box">
          <div className="method-title">
            <span className="badge-method">Method A</span>
            <h4>Person-Based Model</h4>
          </div>
          <p className="formula">Pop ({results.demography?.total_population}) x Rate ({results.demography?.waste_per_capita_kg || 0.5} kg)</p>
          <div className="method-val">{results.method_a?.daily_tonnes} <span className="unit">T/day</span></div>
          <div className="method-kg">({results.method_a?.daily_kg} kg/day)</div>
        </div>

        <div className="method-box">
          <div className="method-title">
            <span className="badge-method">Method B</span>
            <h4>Household Model</h4>
          </div>
          <p className="formula">Households ({results.demography?.number_of_households}) x HH Rate (2.27 kg)</p>
          <div className="method-val">{results.method_b?.daily_tonnes} <span className="unit">T/day</span></div>
          <div className="method-kg">({results.method_b?.daily_kg} kg/day)</div>
        </div>

        <div className="method-box">
          <div className="method-title">
            <span className="badge-method">Method C</span>
            <h4>Measured Weighbridge</h4>
          </div>
          <p className="formula">Verified physical weighbridge logs</p>
          <div className="method-val">{results.method_c ? results.method_c.daily_tonnes : "N/A"} <span className="unit">T/day</span></div>
          <div className="method-kg">Status: {results.method_c ? results.method_c.confidence : "No weighbridge"}</div>
        </div>

        <div className="method-box">
          <div className="method-title">
            <span className="badge-method">Method D</span>
            <h4>Industrial Sources</h4>
          </div>
          <p className="formula">Worker count & industrial categories</p>
          <div className="method-val">{results.method_d?.daily_tonnes} <span className="unit">T/day</span></div>
          <div className="method-kg">({results.method_d?.daily_kg} kg/day)</div>
        </div>

        <div className="method-box">
          <div className="method-title">
            <span className="badge-method">Method E</span>
            <h4>Hospital / Health</h4>
          </div>
          <p className="formula">Active bed count & occupancy rate</p>
          <div className="method-val">{results.method_e?.daily_tonnes} <span className="unit">T/day</span></div>
          <div className="method-kg">({results.method_e?.daily_kg} kg/day)</div>
        </div>

        <div className="method-box">
          <div className="method-title">
            <span className="badge-method">Method F</span>
            <h4>Institutions</h4>
          </div>
          <p className="formula">Students & staff headcount</p>
          <div className="method-val">{results.method_f?.daily_tonnes} <span className="unit">T/day</span></div>
          <div className="method-kg">({results.method_f?.daily_kg} kg/day)</div>
        </div>

        <div className="method-box">
          <div className="method-title">
            <span className="badge-method">Method G</span>
            <h4>Hotels / Tourism</h4>
          </div>
          <p className="formula">Room count & occupancy rate</p>
          <div className="method-val">{results.method_g?.daily_tonnes} <span className="unit">T/day</span></div>
          <div className="method-kg">({results.method_g?.daily_kg} kg/day)</div>
        </div>

        <div className="method-box">
          <div className="method-title">
            <span className="badge-method">Method H</span>
            <h4>Market & Vendors</h4>
          </div>
          <p className="formula">Vendor count & market volume</p>
          <div className="method-val">{results.method_h?.daily_tonnes} <span className="unit">T/day</span></div>
          <div className="method-kg">({results.method_h?.daily_kg} kg/day)</div>
        </div>
      </div>

      {/* Deviations Table */}
      <div className="section-card">
        <div className="chart-header">
          <h3>Method Variance & Deviation Analysis</h3>
          <span className="subtext">Discrepancy compared against the official baseline</span>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Method Name</th>
              <th>Estimated Quantity</th>
              <th>Deviation (Tonnes)</th>
              <th>Deviation (%)</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {rec?.deviations && Object.entries(rec.deviations).map(([k, v]) => (
              <tr key={k}>
                <td><strong>{k}</strong></td>
                <td>{v.tonnes} T/day</td>
                <td className={v.difference_tonnes > 0 ? "text-amber-500" : v.difference_tonnes < 0 ? "text-blue-500" : "text-emerald-500"}>
                  {v.difference_tonnes > 0 ? `+${v.difference_tonnes}` : v.difference_tonnes} T
                </td>
                <td>{v.difference_pct}%</td>
                <td>
                  <span className={Math.abs(v.difference_pct) <= 10 ? "badge-green" : "badge-yellow"}>
                    {Math.abs(v.difference_pct) <= 10 ? "High Agreement" : "Variance Detected"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
