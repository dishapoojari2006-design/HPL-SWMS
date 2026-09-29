import React, { useState, useEffect } from "react";
import { useLocation } from "../context/LocationContext";
import { dataQualityService } from "../api/services";
import { CheckCircle2, AlertTriangle, XCircle, ShieldCheck } from "lucide-react";

export default function DataQualityPage() {
  const { selectedLocation } = useLocation();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedLocation) return;
    setLoading(true);
    dataQualityService.getReport(selectedLocation.id)
      .then((res) => setReport(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [selectedLocation]);

  if (!selectedLocation) return <div className="page-loading">Please select an administrative location.</div>;
  if (loading || !report) return <div className="page-loading">Auditing data quality checklist...</div>;

  return (
    <div className="data-quality-view">
      <div className="page-header">
        <div>
          <h2>Data Quality & Completeness Audit</h2>
          <p>10-point audit checklist ensuring planning integrity before calculation</p>
        </div>

        <div className="score-badge">
          <ShieldCheck size={20} />
          <span>Overall Completeness: <strong>{report.completeness_percent}%</strong></span>
        </div>
      </div>

      <div className="checklist-card">
        <table className="data-table">
          <thead>
            <tr>
              <th>Audit Field / Parameter</th>
              <th>Criticality</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {report.checklist && report.checklist.map((item, idx) => (
              <tr key={idx}>
                <td><strong>{item.field}</strong></td>
                <td>
                  <span className={item.critical ? "badge-red" : "badge-blue"}>
                    {item.critical ? "MANDATORY" : "OPTIONAL"}
                  </span>
                </td>
                <td>
                  {item.status ? (
                    <span className="status-good"><CheckCircle2 size={16} /> Complete</span>
                  ) : (
                    <span className="status-bad"><XCircle size={16} /> Incomplete</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
