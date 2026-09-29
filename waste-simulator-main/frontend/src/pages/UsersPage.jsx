import React, { useState, useEffect } from "react";
import { userService } from "../api/services";
import { Users, UserPlus, Shield, Check, X } from "lucide-react";

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    userService.list()
      .then((res) => setUsers(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="users-view">
      <div className="page-header">
        <div>
          <h2>Role-Based Access Control & User Directory</h2>
          <p>Manage municipal authorities, planners, and field data officers</p>
        </div>
      </div>

      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Authority Type</th>
            <th>Organization</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td><strong>{u.name}</strong></td>
              <td>{u.email}</td>
              <td><span className="badge-blue">{u.role}</span></td>
              <td>{u.authority_type}</td>
              <td>{u.organization || "State Directorate"}</td>
              <td><span className="badge-green">{u.active ? "Active" : "Inactive"}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
