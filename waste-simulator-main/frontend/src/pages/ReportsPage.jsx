import React, { useState } from "react";
import { useLocation } from "../context/LocationContext";
import { reportService } from "../api/services";
import { FileSpreadsheet, Download, FileText, CheckCircle } from "lucide-react";

export default function ReportsPage() {
  const { selectedLocation } = useLocation();
  const [reportType, setReportType] = useState("EXECUTIVE_SUMMARY");
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (!selectedLocation) return;
    setLoading(true);
    try {
      const res = await reportService.generate(selectedLocation.id, {
        report_type: reportType,
        title: `${selectedLocation.name} - ${reportType} Waste Management Plan`,
      });
      setReport(res.data);
    } catch (err) {
      alert("Failed to generate report.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reports-view">
      <div className="page-header">
        <div>
          <h2>Official Reports & Regulatory Submissions</h2>
          <p>Generate SWM Rules 2016 compliance summaries and municipal master plans</p>
        </div>
      </div>

      <div className="report-gen-card">
        <div className="form-group">
          <label>Select Report Format</label>
          <select value={reportType} onChange={(e) => setReportType(e.target.value)} className="select-pill">
            <option value="EXECUTIVE_SUMMARY">Executive Municipal Summary</option>
            <option value="STATUTORY_COMPLIANCE">SWM Rules 2016 Statutory Compliance Audit</option>
            <option value="LONG_TERM_MASTER_PLAN">20-Year Infrastructure Action Master Plan</option>
          </select>
        </div>
        <button onClick={handleGenerate} className="gen-btn" disabled={loading}>
          <FileText size={16} /> {loading ? "Generating Report..." : "Generate Official Report"}
        </button>
      </div>

      {report && (
        <div className="generated-report-card">
          <div className="report-header">
            <h3>{report.title}</h3>
            <span className="badge-green">Generated Successfully</span>
          </div>
          <div className="report-content">
            <h4>Executive Summary</h4>
            <p>{report.content?.executive_summary}</p>
            <h4>Official Reconciled Waste Generation</h4>
            <p><strong>{report.content?.reconciled_generation?.selected_estimate_tonnes} Tonnes/day</strong> ({report.content?.reconciled_generation?.selected_method})</p>
            <h4>Deficit & Breach Assessment</h4>
            <p>{JSON.stringify(report.content?.capacity_deficits, null, 2)}</p>
          </div>
        </div>
      )}
    </div>
  );
}
