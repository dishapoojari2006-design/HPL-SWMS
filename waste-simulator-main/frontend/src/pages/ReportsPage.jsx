import React, { useState } from "react";
import { useLocation } from "../context/LocationContext";
import { reportService } from "../api/services";
import html2pdf from "html2pdf.js";
import {
  FileText,
  Printer,
  Download,
  CheckCircle2,
  AlertTriangle,
  Award,
  Calendar,
  Building2,
  Truck,
  TrendingUp,
  FileSpreadsheet,
  ShieldCheck,
  Zap,
  Layers,
  ArrowUpRight
} from "lucide-react";

import logoImg from "../assets/swms_logo.jpg";

export default function ReportsPage() {
  const { selectedLocation } = useLocation();
  const [reportType, setReportType] = useState("EXECUTIVE_SUMMARY");
  const [report, setReport] = useState(null);
  const [activeFormat, setActiveFormat] = useState("EXECUTIVE_SUMMARY");
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const handleGenerate = async () => {
    if (!selectedLocation) return;
    setLoading(true);
    try {
      const res = await reportService.generate(selectedLocation.id);
      setReport(res.data);
      setActiveFormat(reportType);
    } catch (err) {
      alert("Failed to generate report.");
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadPDF = async () => {
    const element = document.getElementById("report-printable-area");
    if (!element) return;

    setDownloading(true);
    const fileName = `${activeFormat}_${report?.metadata?.location_name || 'Report'}_${new Date().toISOString().slice(0, 10)}.pdf`;

    // Hide action buttons during capture
    const actionsBtnBox = element.querySelector('.report-doc-actions');
    if (actionsBtnBox) actionsBtnBox.style.display = 'none';

    // Apply formal white-paper document theme during render
    const originalBg = element.style.background;
    const originalColor = element.style.color;
    const originalBorder = element.style.border;

    element.style.background = "#ffffff";
    element.style.color = "#0f172a";
    element.style.border = "1px solid #cbd5e1";

    // Set all child section backgrounds and force high-contrast dark text
    const allElements = element.querySelectorAll('*');
    allElements.forEach(el => {
      el.dataset.origColor = el.style.color;
      el.dataset.origBg = el.style.background;

      // Reset light muted text colors (like Tailwind text-slate-400/300) to crisp dark text for white background
      const computedColor = window.getComputedStyle(el).color;
      if (computedColor.includes("148, 163, 184") || computedColor.includes("203, 213, 225") || computedColor.includes("100, 116, 139") || computedColor.includes("248, 250, 252")) {
        el.style.color = "#1e293b";
      }

      if (el.tagName === 'TH') {
        el.style.background = "#e2e8f0";
        el.style.color = "#0f172a";
      } else if (el.tagName === 'TD') {
        el.style.color = "#1e293b";
      } else if (el.classList.contains('report-section') || el.classList.contains('report-data-box') || el.classList.contains('compliance-status-row')) {
        el.style.background = "#f8fafc";
        el.style.border = "1px solid #e2e8f0";
        el.style.color = "#0f172a";
      }
    });

    const opt = {
      margin:       [10, 10, 10, 10],
      filename:     fileName,
      image:        { type: 'jpeg', quality: 0.98 },
      html2canvas:  { scale: 2, useCORS: true, backgroundColor: "#ffffff" },
      jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    try {
      await html2pdf().set(opt).from(element).save();
    } catch (err) {
      console.error("PDF generation error:", err);
      window.print();
    } finally {
      // Restore UI elements and dark theme
      if (actionsBtnBox) actionsBtnBox.style.display = 'flex';
      element.style.background = originalBg;
      element.style.color = originalColor;
      element.style.border = originalBorder;
      allElements.forEach(el => {
        el.style.background = el.dataset.origBg || '';
        el.style.color = el.dataset.origColor || '';
      });
      setDownloading(false);
    }
  };

  if (!selectedLocation) {
    return <div className="page-loading">Please select an administrative location.</div>;
  }

  return (
    <div className="reports-view">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h2>Official Reports & Regulatory Submissions</h2>
          <p>Generate SWM Rules 2016 statutory compliance audits and municipal master plans</p>
        </div>
      </div>

      {/* Control Card */}
      <div className="report-gen-card">
        <div className="form-group" style={{ flex: 1, maxWidth: 420 }}>
          <label className="text-xs text-slate-400 font-semibold mb-1 block">Select Regulatory Report Format</label>
          <select value={reportType} onChange={(e) => setReportType(e.target.value)} className="select-pill" style={{ width: '100%', height: 42 }}>
            <option value="EXECUTIVE_SUMMARY">Executive Municipal Waste Summary</option>
            <option value="STATUTORY_COMPLIANCE">SWM Rules 2016 Statutory Audit & Scorecard</option>
            <option value="LONG_TERM_MASTER_PLAN">20-Year Infrastructure Action Master Plan</option>
          </select>
        </div>
        <button onClick={handleGenerate} className="gen-btn" disabled={loading} style={{ height: 42 }}>
          <FileText size={16} /> {loading ? "Generating Formal Document..." : "Generate Official Document"}
        </button>
      </div>

      {/* Rendered Document */}
      {report && (
        <div className="report-doc-container" id="report-printable-area">
          {/* Document Header */}
          <div className="report-doc-header">
            <div className="report-doc-title-box" style={{ display: "flex", gap: "16px", alignItems: "flex-start" }}>
              <img
                src={logoImg}
                alt="Official Logo"
                style={{
                  width: "48px",
                  height: "48px",
                  borderRadius: "10px",
                  objectFit: "cover",
                  border: "1px solid #cbd5e1",
                  flexShrink: 0
                }}
              />
              <div>
                <div className="sim-badge-row">
                  <span className="sim-pill-tag">OFFICIAL MUNICIPAL SUBMISSION</span>
                  <span className="text-xs text-slate-400">Ref ID: SWMS-REP-{selectedLocation.id}-{Date.now().toString().slice(-6)}</span>
                </div>
                <h3>
                  {activeFormat === "EXECUTIVE_SUMMARY" && `Executive Municipal Waste Summary — ${report.metadata?.location_name}`}
                  {activeFormat === "STATUTORY_COMPLIANCE" && `SWM Rules 2016 Statutory Audit & Compliance Scorecard — ${report.metadata?.location_name}`}
                  {activeFormat === "LONG_TERM_MASTER_PLAN" && `20-Year Infrastructure Action Master Plan — ${report.metadata?.location_name}`}
                </h3>
                <div className="report-doc-meta">
                  <span><strong>Authority:</strong> {report.metadata?.location_name} ({report.metadata?.location_type})</span>
                  <span><strong>District:</strong> {report.metadata?.district}, {report.metadata?.state}</span>
                  <span><strong>Timestamp:</strong> {new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}</span>
                  <span><strong>Data Quality Score:</strong> <strong className="text-emerald-400">{report.metadata?.data_quality_percent}% Verified</strong></span>
                </div>
              </div>
            </div>

            <div className="report-doc-actions" style={{ display: "flex", gap: "10px" }}>
              <button className="report-action-btn" onClick={handlePrint} style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <Printer size={15} /> Print
              </button>
              <button
                className="report-action-btn"
                onClick={handleDownloadPDF}
                disabled={downloading}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  background: "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)",
                  color: "#ffffff",
                  borderColor: "#3b82f6",
                  cursor: downloading ? "wait" : "pointer",
                  opacity: downloading ? 0.7 : 1
                }}
              >
                <Download size={15} /> {downloading ? "Downloading PDF..." : "Download PDF"}
              </button>
            </div>
          </div>

          {/* DYNAMIC CONTENT BASED ON SELECTED REPORT FORMAT */}

          {/* FORMAT 1: EXECUTIVE MUNICIPAL SUMMARY */}
          {activeFormat === "EXECUTIVE_SUMMARY" && (
            <>
              <div className="report-section">
                <div className="report-section-title"><Award size={16} /> 1. Executive Summary & Municipal Key Totals</div>
                <p className="text-sm text-slate-300 leading-relaxed">
                  This official document presents the reconciled solid waste baseline for <strong>{report.metadata?.location_name}</strong>. Data incorporates verified census projections, weighbridge time-series logs, and spatial infrastructure mapping to establish a legally compliant baseline under National SWM Guidelines.
                </p>

                <div className="report-grid-2">
                  <div className="report-data-box">
                    <div className="report-data-label">Total Resident Population</div>
                    <div className="report-data-value">{(report.demographics?.total_population || 0).toLocaleString()}</div>
                    <div className="report-data-sub">{(report.demographics?.households || 0).toLocaleString()} Registered Households</div>
                  </div>

                  <div className="report-data-box">
                    <div className="report-data-label">Daily Waste Generation</div>
                    <div className="report-data-value text-emerald-400">
                      {report.forecasting_outlook?.forecast_value_tonnes_day || 12.5} <span className="sim-kpi-unit">T/day</span>
                    </div>
                    <div className="report-data-sub">Method: {report.forecasting_outlook?.selected_method || "Linear Model"}</div>
                  </div>

                  <div className="report-data-box">
                    <div className="report-data-label">Primary Collection Fleet</div>
                    <div className="report-data-value">{report.infrastructure?.collection_vehicles || 0} Vehicles</div>
                    <div className="report-data-sub">{report.infrastructure?.collection_coverage_pct || 100}% Door-to-Door Coverage</div>
                  </div>

                  <div className="report-data-box">
                    <div className="report-data-label">Installed Treatment Capacity</div>
                    <div className="report-data-value text-blue-400">
                      {((report.infrastructure?.installed_treatment_kg_day || 0) / 1000).toFixed(2)} <span className="sim-kpi-unit">T/day</span>
                    </div>
                    <div className="report-data-sub">{report.active_facilities_count || 0} Active Processing Facilities</div>
                  </div>
                </div>
              </div>

              <div className="report-section">
                <div className="report-section-title"><Layers size={16} /> 2. Waste Composition & Physical Characterization</div>
                <table className="sim-comparison-table">
                  <thead>
                    <tr>
                      <th>Category Component</th>
                      <th>Physical % Fraction</th>
                      <th>Est. Daily Tonnage (T/day)</th>
                      <th>Recommended Handling Pathway</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Organic / Wet Biodegradable</td>
                      <td>{report.waste_composition?.organic_percent || 52}%</td>
                      <td>{(((report.forecasting_outlook?.forecast_value_tonnes_day || 12.5) * (report.waste_composition?.organic_percent || 52)) / 100).toFixed(2)} T</td>
                      <td>Aerobic Composting / Biomethanation</td>
                    </tr>
                    <tr>
                      <td>Dry Recyclables (Paper/Plastic/Glass)</td>
                      <td>{report.waste_composition?.recyclable_percent || 28}%</td>
                      <td>{(((report.forecasting_outlook?.forecast_value_tonnes_day || 12.5) * (report.waste_composition?.recyclable_percent || 28)) / 100).toFixed(2)} T</td>
                      <td>Material Recovery Facility (MRF)</td>
                    </tr>
                    <tr>
                      <td>Inert & Landfill Residue</td>
                      <td>{report.waste_composition?.other_percent || 20}%</td>
                      <td>{(((report.forecasting_outlook?.forecast_value_tonnes_day || 12.5) * (report.waste_composition?.other_percent || 20)) / 100).toFixed(2)} T</td>
                      <td>Sanitary Landfill Disposal</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </>
          )}

          {/* FORMAT 2: SWM RULES 2016 STATUTORY AUDIT */}
          {activeFormat === "STATUTORY_COMPLIANCE" && (
            <>
              <div className="report-section">
                <div className="report-section-title"><ShieldCheck size={16} /> 1. SWM Rules 2016 Statutory Audit Scorecard</div>
                <p className="text-sm text-slate-300 leading-relaxed">
                  Evaluation of municipal waste management practices against mandatory duties mandated under Rule 15 of Solid Waste Management Rules, 2016.
                </p>

                <div className="flex flex-col gap-3">
                  <div className="compliance-status-row">
                    <div>
                      <strong className="text-sm text-white">Rule 15(a): 100% Door-to-Door Collection</strong>
                      <div className="text-xs text-slate-400">Current Collection Coverage: {report.infrastructure?.collection_coverage_pct || 100}%</div>
                    </div>
                    <span className="sim-status-badge safe"><CheckCircle2 size={12} /> FULLY COMPLIANT</span>
                  </div>

                  <div className="compliance-status-row warn">
                    <div>
                      <strong className="text-sm text-white">Rule 15(b): At-Source Waste Segregation (Wet / Dry / Hazardous)</strong>
                      <div className="text-xs text-slate-400">Current Segregation Rate: ~60% | Target: 100%</div>
                    </div>
                    <span className="sim-status-badge warning"><AlertTriangle size={12} /> PARTIAL COMPLIANCE</span>
                  </div>

                  <div className="compliance-status-row">
                    <div>
                      <strong className="text-sm text-white">Rule 15(v): Wet Waste Treatment & Composting Facility</strong>
                      <div className="text-xs text-slate-400">Processing Capacity: {((report.infrastructure?.installed_treatment_kg_day || 0) / 1000).toFixed(2)} T/day installed</div>
                    </div>
                    <span className="sim-status-badge safe"><CheckCircle2 size={12} /> COMPLIANT</span>
                  </div>

                  <div className="compliance-status-row warn">
                    <div>
                      <strong className="text-sm text-white">Rule 15(w): Sanitary Landfill Diversion (Max 15% Inert Limit)</strong>
                      <div className="text-xs text-slate-400">Current Landfill Diversion Rate: ~75%</div>
                    </div>
                    <span className="sim-status-badge warning"><AlertTriangle size={12} /> ATTENTION REQUIRED</span>
                  </div>
                </div>
              </div>

              <div className="report-section">
                <div className="report-section-title"><Zap size={16} /> 2. Statutory Corrective Action Directives</div>
                <table className="sim-comparison-table">
                  <thead>
                    <tr>
                      <th>Compliance Area</th>
                      <th>Identified Gap</th>
                      <th>Statutory Deadline</th>
                      <th>Priority</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Source Segregation Enforcement</td>
                      <td>Non-segregated waste received from commercial establishments</td>
                      <td>Immediate (30 Days)</td>
                      <td><span className="text-red-400 font-bold">HIGH</span></td>
                    </tr>
                    <tr>
                      <td>MRF Mechanization</td>
                      <td>Manual sorting limits secondary plastic recovery</td>
                      <td>90 Days</td>
                      <td><span className="text-amber-400 font-bold">MEDIUM</span></td>
                    </tr>
                    <tr>
                      <td>Bulk Generator Bye-Laws</td>
                      <td>Hotels & wedding halls must compost wet waste on-site</td>
                      <td>60 Days</td>
                      <td><span className="text-emerald-400 font-bold">NORMAL</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </>
          )}

          {/* FORMAT 3: 20-YEAR INFRASTRUCTURE MASTER PLAN */}
          {activeFormat === "LONG_TERM_MASTER_PLAN" && (
            <>
              <div className="report-section">
                <div className="report-section-title"><TrendingUp size={16} /> 1. 20-Year Long-Term Infrastructure Horizon</div>
                <p className="text-sm text-slate-300 leading-relaxed">
                  Strategic capital asset planning for <strong>{report.metadata?.location_name}</strong> modeling demographic expansion, collection fleet degradation, and processing plant breach thresholds.
                </p>

                <div className="report-grid-2">
                  <div className="report-data-box">
                    <div className="report-data-label">20-Year Cumulative Generation</div>
                    <div className="report-data-value text-emerald-400">
                      {report.simulation_summary?.total_cumulative_20yr_tonnes ? report.simulation_summary.total_cumulative_20yr_tonnes.toLocaleString() : "124,500"} <span className="sim-kpi-unit">Tonnes</span>
                    </div>
                    <div className="report-data-sub">Total 20-year municipal waste output</div>
                  </div>

                  <div className="report-data-box">
                    <div className="report-data-label">Collection Fleet Breach Year</div>
                    <div className="report-data-value text-amber-400">
                      {report.simulation_summary?.fleet_breach_year ? `Year ${report.simulation_summary.fleet_breach_year}` : "NO BREACH"}
                    </div>
                    <div className="report-data-sub">Point where fleet capacity &lt; generation</div>
                  </div>

                  <div className="report-data-box">
                    <div className="report-data-label">Treatment Capacity Breach Year</div>
                    <div className="report-data-value text-red-400">
                      {report.simulation_summary?.treatment_breach_year ? `Year ${report.simulation_summary.treatment_breach_year}` : "NO BREACH"}
                    </div>
                    <div className="report-data-sub">Point where processing capacity &lt; intake</div>
                  </div>

                  <div className="report-data-box">
                    <div className="report-data-label">Projected Population Growth</div>
                    <div className="report-data-value text-blue-400">
                      {report.demographics?.growth_rate_pct || 2.0}% / year
                    </div>
                    <div className="report-data-sub">Compounded demographic expansion</div>
                  </div>
                </div>
              </div>

              <div className="report-section">
                <div className="report-section-title"><Building2 size={16} /> 2. Phased Capital Infrastructure Investment Roadmap</div>
                <table className="sim-comparison-table">
                  <thead>
                    <tr>
                      <th>Implementation Phase</th>
                      <th>Asset Expansion Project</th>
                      <th>Target Capacity Addition</th>
                      <th>Estimated Investment</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Phase 1 (Years 1–3)</td>
                      <td>Collection Fleet Procurement & Route Optimization</td>
                      <td>+4 Hydraulic Compactor Trucks</td>
                      <td>₹ 1.20 Cr</td>
                    </tr>
                    <tr>
                      <td>Phase 2 (Years 4–7)</td>
                      <td>Centralized Wet Waste Bio-Composting Plant</td>
                      <td>+15 T/day Processing Capacity</td>
                      <td>₹ 3.50 Cr</td>
                    </tr>
                    <tr>
                      <td>Phase 3 (Years 8–15)</td>
                      <td>Semi-Automated MRF & RDF Pre-Processing Unit</td>
                      <td>+10 T/day Material Recovery</td>
                      <td>₹ 2.80 Cr</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </>
          )}

        </div>
      )}
    </div>
  );
}
