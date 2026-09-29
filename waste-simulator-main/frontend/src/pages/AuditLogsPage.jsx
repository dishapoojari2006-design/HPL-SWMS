import React, { useState, useEffect } from "react";
import { auditService } from "../api/services";
import { ScrollText, Filter } from "lucide-react";

export default function AuditLogsPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    auditService.list(100)
      .then((res) => setLogs(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="audit-view">
      <div className="page-header">
        <div>
          <h2>Immutable System Audit Trail</h2>
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
