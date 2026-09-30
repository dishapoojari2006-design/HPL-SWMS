import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { auditService } from "../api/services";
import { ScrollText, Filter, Lock } from "lucide-react";

export default function AuditLogsPage() {
  const { hasRole } = useAuth();
  const canViewLogs = hasRole("SUPER_ADMIN", "MUNICIPAL_AUTHORITY", "PANCHAYAT_AUTHORITY");
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!canViewLogs) return;
    setLoading(true);
    auditService.list(100)
      .then((res) => setLogs(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [canViewLogs]);

  if (!canViewLogs) {
    return (
      <div className="audit-view">
        <div className="page-header">
          <div>
            <h2>Audit Trail</h2>
            <p>Security & compliance log of all data modifications and calculations</p>
          </div>
        </div>
        <div style={{ background: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#ef4444', padding: '32px', borderRadius: 12, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: 12, margin: '30px 0' }}>
          <Lock size={36} />
          <h3 style={{ fontSize: 18, fontWeight: 700, color: '#f8fafc' }}>Restricted Administrative Access</h3>
          <p style={{ maxWidth: 520, fontSize: 14, color: '#cbd5e1' }}>
            System Audit Logs contain sensitive security trails and user activity logs. Access is strictly restricted to <strong>Super Admin</strong> and <strong>Municipal / Panchayat Authority</strong> accounts.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="audit-view">
      <div className="page-header">
        <div>
          <h2> Audit Trail</h2>
          <p>Security & compliance log of all data modifications and calculations</p>
        </div>
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>User</th>
            <th>Action</th>
            <th>Module</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id}>
              <td>{new Date(log.timestamp).toLocaleString()}</td>
              <td><strong>{log.user_name || "System"}</strong></td>
              <td><span className="badge-blue">{log.action}</span></td>
              <td><span className="badge-green">{log.module}</span></td>
              <td><pre className="text-xs">{JSON.stringify(log.details)}</pre></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
