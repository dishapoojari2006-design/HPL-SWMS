import React, { useState, useEffect } from "react";
import { userService } from "../api/services";
import { useAuth } from "../context/AuthContext";
import { Users, UserPlus, Shield, Check, X, Edit2, Power, AlertCircle, RefreshCw, Trash2 } from "lucide-react";

const ROLES = [
  "SUPER_ADMIN",
  "MUNICIPAL_AUTHORITY",
  "PANCHAYAT_AUTHORITY",
  "PLANNER",
  "DATA_ENTRY",
  "VIEWER"
];

const AUTHORITY_TYPES = ["MUNICIPALITY", "PANCHAYAT", "STATE", "OTHER"];

export default function UsersPage() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const triggerNotification = (msg, isError = false) => {
    if (isError) {
      setError(typeof msg === "string" ? msg : JSON.stringify(msg));
      setSuccess(null);
      setTimeout(() => setError(null), 2000);
    } else {
      setSuccess(msg);
      setError(null);
      setTimeout(() => setSuccess(null), 2000);
    }
  };

  // New user form state
  const [showAddModal, setShowAddModal] = useState(false);
  const [emailError, setEmailError] = useState(null);
  const [passwordError, setPasswordError] = useState(null);
  const [newUser, setNewUser] = useState({
    name: "",
    email: "",
    password: "",
    phone: "",
    role: "VIEWER",
    authority_type: "OTHER",
    organization: ""
  });

  const resetAddUserForm = () => {
    setNewUser({
      name: "",
      email: "",
      password: "",
      phone: "",
      role: "VIEWER",
      authority_type: "OTHER",
      organization: ""
    });
    setEmailError(null);
    setPasswordError(null);
  };

  const openAddModal = () => {
    resetAddUserForm();
    setShowAddModal(true);
  };
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Updating ID state
  const [updatingId, setUpdatingId] = useState(null);

  // Edit User modal state
  const [editingUser, setEditingUser] = useState(null);
  const [editFormData, setEditFormData] = useState({
    name: "",
    email: "",
    phone: "",
    role: "VIEWER",
    authority_type: "OTHER",
    organization: "",
    active: true
  });

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await userService.list();
      setUsers(res.data);
    } catch (err) {
      console.error("Failed to fetch users:", err);
      triggerNotification(err.response?.data?.detail || "Failed to load users list", true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const openEditModal = (u) => {
    setEditingUser(u);
    setEditFormData({
      name: u.name || "",
      email: u.email || "",
      phone: u.phone || "",
      role: u.role || "VIEWER",
      authority_type: u.authority_type || "OTHER",
      organization: u.organization || "",
      active: u.active ?? true
    });
  };

  const handleEditRoleChange = (newRole) => {
    let suggestedAuth = editFormData.authority_type;
    if (newRole === "MUNICIPAL_AUTHORITY") suggestedAuth = "MUNICIPALITY";
    else if (newRole === "PANCHAYAT_AUTHORITY") suggestedAuth = "PANCHAYAT";
    else if (newRole === "SUPER_ADMIN") suggestedAuth = "ADMINISTRATOR";

    setEditFormData(prev => ({
      ...prev,
      role: newRole,
      authority_type: suggestedAuth
    }));
  };

  const handleSaveUserEdit = async (e) => {
    e.preventDefault();
    if (!editingUser) return;
    setUpdatingId(editingUser.id);
    try {
      const res = await userService.update(editingUser.id, editFormData);
      setUsers(users.map(u => u.id === editingUser.id ? res.data : u));
      triggerNotification(`User "${res.data.name}" updated successfully!`);
      setEditingUser(null);
    } catch (err) {
      console.error("Failed to update user:", err);
      triggerNotification(err.response?.data?.detail || "Failed to update user details", true);
    } finally {
      setUpdatingId(null);
    }
  };

  const handleDeleteUser = async (userToDelete) => {
    if (userToDelete.id === currentUser?.id) {
      triggerNotification("You cannot delete your own admin account.", true);
      return;
    }
    const confirmed = window.confirm(`Are you sure you want to permanently delete user "${userToDelete.name}" (${userToDelete.email})? This action cannot be undone.`);
    if (!confirmed) return;

    setUpdatingId(userToDelete.id);
    try {
      await userService.delete(userToDelete.id);
      setUsers(users.filter(u => u.id !== userToDelete.id));
      triggerNotification(`User "${userToDelete.name}" deleted successfully.`);
      if (editingUser?.id === userToDelete.id) {
        setEditingUser(null);
      }
    } catch (err) {
      console.error("Failed to delete user:", err);
      triggerNotification(err.response?.data?.detail || "Failed to delete user account.", true);
    } finally {
      setUpdatingId(null);
    }
  };

  const validatePassword = (password) => {
    const pwd = password || "";
    if (pwd.length < 10 || pwd.length > 13) {
      return "Password must be between 10 and 13 characters long.";
    }
    if (!/[A-Z]/.test(pwd)) {
      return "Password must contain at least 1 uppercase letter.";
    }
    if (!/[a-z]/.test(pwd)) {
      return "Password must contain at least 1 lowercase letter.";
    }
    if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pwd)) {
      return "Password must contain at least 1 special character.";
    }
    return null;
  };

  const handleAddUserSubmit = async (e) => {
    e.preventDefault();

    // Email format validation with strict TLD check
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|org|net|in|gov|edu|co|io|dev|me|info|biz|ac\.in|gov\.in)$/i;
    if (!newUser.email || !emailRegex.test(newUser.email.trim().toLowerCase())) {
      setEmailError("Please enter a valid email address with a recognized domain (e.g. .com, .org, .in).");
      return;
    }
    setEmailError(null);

    // Password validation
    const pwdErr = validatePassword(newUser.password);
    if (pwdErr) {
      setPasswordError(pwdErr);
      return;
    }
    setPasswordError(null);

    setIsSubmitting(true);
    try {
      await userService.create(newUser);
      triggerNotification("New user created successfully!");
      setShowAddModal(false);
      setNewUser({
        name: "",
        email: "",
        password: "",
        phone: "",
        role: "VIEWER",
        authority_type: "OTHER",
        organization: ""
      });
      fetchUsers();
    } catch (err) {
      console.error("Failed to create user:", err);
      triggerNotification(err.response?.data?.detail || "Failed to create user", true);
    } finally {
      setIsSubmitting(false);
    }
  };

  const isAdmin = currentUser?.role === "SUPER_ADMIN";

  return (
    <div className="users-view">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <div>
          <h2><Users style={{ display: "inline", marginRight: "8px", verticalAlign: "middle" }} /> User Management & Access Control</h2>
          <p>Manage municipal authorities, planners, role permissions, and account activation statuses</p>
        </div>
        <div style={{ display: "flex", gap: "10px" }}>
          <button
            onClick={fetchUsers}
            disabled={loading}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "6px",
              padding: "8px 16px",
              background: "var(--bg-tertiary)",
              color: "var(--text-primary)",
              border: "1px solid var(--border-color)",
              borderRadius: "8px",
              fontWeight: "600",
              fontSize: "13px",
              cursor: loading ? "not-allowed" : "pointer",
              transition: "all 0.2s ease",
              boxShadow: "0 2px 6px rgba(0,0,0,0.2)"
            }}
          >
            <RefreshCw size={15} className={loading ? "spin" : ""} /> Refresh
          </button>
          {isAdmin && (
            <button
              onClick={openAddModal}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                padding: "8px 18px",
                background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                color: "#ffffff",
                border: "none",
                borderRadius: "8px",
                fontWeight: "600",
                fontSize: "13px",
                cursor: "pointer",
                boxShadow: "0 4px 14px rgba(16, 185, 129, 0.35)",
                transition: "all 0.2s ease"
              }}
            >
              <UserPlus size={16} /> Add New User
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div style={{ padding: "40px", textAlign: "center", color: "var(--text-muted)" }}>Loading directory...</div>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Authority Type</th>
              <th>Organization</th>
              <th>Status</th>
              {isAdmin && <th>Actions</th>}
            </tr>
          </thead>
          <tbody>
            {users.map((u) => {
              const isSelf = u.id === currentUser?.id;
              return (
                <tr key={u.id}>
                  <td><strong>{u.name} {isSelf && <span style={{ fontSize: "11px", color: "var(--accent-emerald)", marginLeft: "4px" }}>(You)</span>}</strong></td>
                  <td>{u.email}</td>
                  <td><span className="badge-blue">{u.role}</span></td>
                  <td>{u.authority_type}</td>
                  <td>{u.organization || "State Directorate"}</td>
                  <td>
                    <span className={u.active ? "badge-green" : "badge-red"} style={{ background: u.active ? "rgba(16, 185, 129, 0.15)" : "rgba(239, 68, 68, 0.15)", color: u.active ? "var(--accent-emerald)" : "var(--accent-red)", padding: "4px 8px", borderRadius: "12px", fontSize: "12px", fontWeight: "600" }}>
                      {u.active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  {isAdmin && (
                    <td>
                      <div style={{ display: "flex", gap: "8px" }}>
                        <button
                          onClick={() => openEditModal(u)}
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "6px",
                            padding: "5px 12px",
                            fontSize: "12px",
                            fontWeight: "600",
                            cursor: "pointer",
                            background: "rgba(59, 130, 246, 0.12)",
                            color: "#60a5fa",
                            border: "1px solid rgba(59, 130, 246, 0.3)",
                            borderRadius: "6px",
                            transition: "all 0.15s ease"
                          }}
                        >
                          <Edit2 size={13} />
                          Edit
                        </button>
                        <button
                          disabled={isSelf || updatingId === u.id}
                          onClick={() => handleDeleteUser(u)}
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "6px",
                            padding: "5px 12px",
                            fontSize: "12px",
                            fontWeight: "600",
                            cursor: isSelf ? "not-allowed" : "pointer",
                            opacity: isSelf ? 0.4 : 1,
                            background: "rgba(239, 68, 68, 0.12)",
                            color: "#f87171",
                            border: "1px solid rgba(239, 68, 68, 0.3)",
                            borderRadius: "6px",
                            transition: "all 0.15s ease"
                          }}
                        >
                          <Trash2 size={13} />
                          Delete
                        </button>
                      </div>
                    </td>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      )}

      {/* Edit User Modal */}
      {editingUser && (
        <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(0, 0, 0, 0.7)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
          <div style={{ background: "var(--bg-secondary)", padding: "24px", borderRadius: "12px", width: "480px", maxWidth: "95%", border: "1px solid var(--border-color)", maxHeight: "90vh", overflowY: "auto" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
              <h3 style={{ margin: 0, display: "flex", alignItems: "center", gap: "8px" }}><Edit2 size={20} /> Edit User Parameters</h3>
              <button onClick={() => setEditingUser(null)} style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer" }}><X size={20} /></button>
            </div>

            <form onSubmit={handleSaveUserEdit}>
              <div style={{ marginBottom: "12px" }}>
                <label style={{ display: "block", fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>Full Name</label>
                <input
                  type="text"
                  required
                  value={editFormData.name}
                  onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
                  style={{ width: "100%", padding: "8px 12px", background: "var(--bg-tertiary)", border: "1px solid var(--border-color)", color: "#fff", borderRadius: "6px" }}
                />
              </div>

              <div style={{ marginBottom: "12px" }}>
                <label style={{ display: "block", fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>Email Address</label>
                <input
                  type="email"
                  required
                  value={editFormData.email}
                  onChange={(e) => setEditFormData({ ...editFormData, email: e.target.value })}
                  style={{ width: "100%", padding: "8px 12px", background: "var(--bg-tertiary)", border: "1px solid var(--border-color)", color: "#fff", borderRadius: "6px" }}
                />
              </div>

              <div style={{ marginBottom: "12px" }}>
                <label style={{ display: "block", fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>Phone Number</label>
                <input
                  type="text"
                  value={editFormData.phone}
                  onChange={(e) => setEditFormData({ ...editFormData, phone: e.target.value })}
                  style={{ width: "100%", padding: "8px 12px", background: "var(--bg-tertiary)", border: "1px solid var(--border-color)", color: "#fff", borderRadius: "6px" }}
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "12px" }}>
                <div>
                  <label style={{ display: "block", fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>Role</label>
                  <select
                    value={editFormData.role}
                    onChange={(e) => handleEditRoleChange(e.target.value)}
                    style={{ width: "100%", padding: "8px 12px", background: "var(--bg-tertiary)", border: "1px solid var(--border-color)", color: "#fff", borderRadius: "6px" }}
                  >
                    {ROLES.map((r) => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label style={{ display: "block", fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>Authority Type</label>
                  <select
                    value={editFormData.authority_type}
                    onChange={(e) => setEditFormData({ ...editFormData, authority_type: e.target.value })}
                    style={{ width: "100%", padding: "8px 12px", background: "var(--bg-tertiary)", border: "1px solid var(--border-color)", color: "#fff", borderRadius: "6px" }}
                  >
                    {["MUNICIPALITY", "PANCHAYAT", "ADMINISTRATOR", "PLANNING_BOARD", "FIELD_OFFICE", "STATE", "PUBLIC", "OTHER"].map((a) => (
                      <option key={a} value={a}>{a}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div style={{ marginBottom: "12px" }}>
                <label style={{ display: "block", fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>Organization</label>
                <input
                  type="text"
                  placeholder="e.g. City Council / Directorate"
                  value={editFormData.organization}
                  onChange={(e) => setEditFormData({ ...editFormData, organization: e.target.value })}
                  style={{ width: "100%", padding: "8px 12px", background: "var(--bg-tertiary)", border: "1px solid var(--border-color)", color: "#fff", borderRadius: "6px" }}
                />
              </div>

              <div style={{ marginBottom: "20px" }}>
                <label style={{ display: "block", fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>Account Status</label>
                <select
                  value={editFormData.active ? "true" : "false"}
                  disabled={editingUser.id === currentUser?.id}
                  onChange={(e) => setEditFormData({ ...editFormData, active: e.target.value === "true" })}
                  style={{ width: "100%", padding: "8px 12px", background: "var(--bg-tertiary)", border: "1px solid var(--border-color)", color: "#fff", borderRadius: "6px" }}
                >
                  <option value="true">Active</option>
                  <option value="false">Inactive</option>
                </select>
                {editingUser.id === currentUser?.id && (
                  <span style={{ fontSize: "11px", color: "var(--accent-amber)", display: "block", marginTop: "4px" }}>You cannot deactivate your own active admin account.</span>
                )}
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
                <button type="button" className="btn-secondary" onClick={() => setEditingUser(null)} disabled={updatingId === editingUser.id}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={updatingId === editingUser.id}>
                  {updatingId === editingUser.id ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Floating Toast Notification (Disappears in 2 sec) */}
      <div style={{ position: "fixed", bottom: "24px", right: "24px", zIndex: 2000, display: "flex", flexDirection: "column", gap: "10px" }}>
        {error && (
          <div style={{ padding: "12px 20px", borderRadius: "8px", background: "#7f1d1d", border: "1px solid #ef4444", color: "#fca5a5", display: "flex", alignItems: "center", gap: "10px", boxShadow: "0 10px 25px rgba(0,0,0,0.5)", animation: "fadeIn 0.2s ease" }}>
            <AlertCircle size={18} />
            <span style={{ fontSize: "13px", fontWeight: "500" }}>{typeof error === "string" ? error : JSON.stringify(error)}</span>
          </div>
        )}

        {success && (
          <div style={{ padding: "12px 20px", borderRadius: "8px", background: "#064e3b", border: "1px solid #10b981", color: "#6ee7b7", display: "flex", alignItems: "center", gap: "10px", boxShadow: "0 10px 25px rgba(0,0,0,0.5)", animation: "fadeIn 0.2s ease" }}>
            <Check size={18} />
            <span style={{ fontSize: "13px", fontWeight: "500" }}>{success}</span>
          </div>
        )}
      </div>

      {showAddModal && (
        <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(0, 0, 0, 0.7)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}>
          <div style={{ background: "var(--bg-secondary)", padding: "24px", borderRadius: "12px", width: "450px", maxWidth: "90%", border: "1px solid var(--border-color)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
              <h3 style={{ margin: 0, display: "flex", alignItems: "center", gap: "8px" }}><UserPlus size={20} /> Create New User</h3>
              <button onClick={() => { setShowAddModal(false); resetAddUserForm(); }} style={{ background: "transparent", border: "none", color: "var(--text-muted)", cursor: "pointer" }}><X size={20} /></button>
            </div>

            <form onSubmit={handleAddUserSubmit}>
              <div style={{ marginBottom: "12px" }}>
                <label style={{ display: "block", fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>Full Name *</label>
                <input
                  type="text"
                  required
                  value={newUser.name}
                  onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                  style={{ width: "100%", padding: "8px 12px", background: "var(--bg-tertiary)", border: "1px solid var(--border-color)", color: "#fff", borderRadius: "6px" }}
                />
              </div>

              <div style={{ marginBottom: "12px" }}>
                <label style={{ display: "block", fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>Email Address *</label>
                <input
                  type="email"
                  required
                  autoComplete="off"
                  placeholder="username@gmail.com"
                  value={newUser.email}
                  onChange={(e) => {
                    const val = e.target.value;
                    setNewUser({ ...newUser, email: val });
                    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|org|net|in|gov|edu|co|io|dev|me|info|biz|ac\.in|gov\.in)$/i;
                    if (val && !emailRegex.test(val.trim().toLowerCase())) {
                      setEmailError("Please enter a valid email address with a recognized domain (e.g. .com, .org, .in).");
                    } else {
                      setEmailError(null);
                    }
                  }}
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    background: "var(--bg-tertiary)",
                    border: `1px solid ${emailError ? "#ef4444" : "var(--border-color)"}`,
                    color: "#fff",
                    borderRadius: "6px"
                  }}
                />
                {emailError && (
                  <span style={{ fontSize: "11px", color: "#f87171", display: "block", marginTop: "4px", fontWeight: "500" }}>
                    {emailError}
                  </span>
                )}
              </div>

              <div style={{ marginBottom: "12px" }}>
                <label style={{ display: "block", fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>Password *</label>
                <input
                  type="password"
                  required
                  autoComplete="new-password"
                  minLength={10}
                  maxLength={13}
                  placeholder="e.g. Password@12"
                  value={newUser.password}
                  onChange={(e) => {
                    const val = e.target.value;
                    setNewUser({ ...newUser, password: val });
                    if (!validatePassword(val)) {
                      setPasswordError(null);
                    }
                  }}
                  onBlur={(e) => {
                    const err = validatePassword(e.target.value);
                    setPasswordError(err);
                  }}
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    background: "var(--bg-tertiary)",
                    border: `1px solid ${passwordError ? "#ef4444" : "var(--border-color)"}`,
                    color: "#fff",
                    borderRadius: "6px"
                  }}
                />
                {passwordError ? (
                  <span style={{ fontSize: "11px", color: "#f87171", display: "block", marginTop: "4px", fontWeight: "500" }}>
                    {passwordError}
                  </span>
                ) : (
                  <span style={{ fontSize: "11px", color: "var(--text-muted)", display: "block", marginTop: "4px" }}>
                    10-13 characters, with at least 1 uppercase letter, 1 lowercase letter, and 1 special character.
                  </span>
                )}
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "12px" }}>
                <div>
                  <label style={{ display: "block", fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>Role</label>
                  <select
                    value={newUser.role}
                    onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                    style={{ width: "100%", padding: "8px 12px", background: "var(--bg-tertiary)", border: "1px solid var(--border-color)", color: "#fff", borderRadius: "6px" }}
                  >
                    {ROLES.map((r) => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label style={{ display: "block", fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>Authority Type</label>
                  <select
                    value={newUser.authority_type}
                    onChange={(e) => setNewUser({ ...newUser, authority_type: e.target.value })}
                    style={{ width: "100%", padding: "8px 12px", background: "var(--bg-tertiary)", border: "1px solid var(--border-color)", color: "#fff", borderRadius: "6px" }}
                  >
                    {AUTHORITY_TYPES.map((a) => (
                      <option key={a} value={a}>{a}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div style={{ marginBottom: "20px" }}>
                <label style={{ display: "block", fontSize: "12px", color: "var(--text-muted)", marginBottom: "4px" }}>Organization</label>
                <input
                  type="text"
                  placeholder="e.g. City Council / Directorate"
                  value={newUser.organization}
                  onChange={(e) => setNewUser({ ...newUser, organization: e.target.value })}
                  style={{ width: "100%", padding: "8px 12px", background: "var(--bg-tertiary)", border: "1px solid var(--border-color)", color: "#fff", borderRadius: "6px" }}
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
                <button type="button" className="btn-secondary" onClick={() => { setShowAddModal(false); resetAddUserForm(); }} disabled={isSubmitting}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={isSubmitting}>
                  {isSubmitting ? "Creating..." : "Create User"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

