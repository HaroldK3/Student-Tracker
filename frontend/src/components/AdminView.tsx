import React, { useEffect, useState } from "react";
import api from "../api";
import "./AdminView.css";

type Role = "ADMIN" | "INSTRUCTOR" | "IT";

interface AdminUser {
  UserId?: number;
  FirstName: string;
  LastName: string;
  Email: string;
  Role: Role;
  IsActive?: boolean;
  CreatedAtUtc?: string;
}

const emptyForm: AdminUser = {
  FirstName: "",
  LastName: "",
  Email: "",
  Role: "INSTRUCTOR",
};

const AdminView: React.FC = () => {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [form, setForm] = useState<AdminUser>(emptyForm);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string>("");

  // Load users from /admin/users on mount
  const loadUsers = async () => {
    try {
      setLoading(true);
      setError("");
      const res = await api.get<AdminUser[]>("/admin/users");
      setUsers(res.data);
    } catch (e: any) {
      console.error(e);
      setError("Failed to load users.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      // backend expects something like { FirstName, LastName, Email, Role }
      const payload = {
        FirstName: form.FirstName,
        LastName: form.LastName,
        Email: form.Email,
        Role: form.Role,  // ADMIN / INSTRUCTOR / IT
      };

      await api.post("/admin/users/create_user", payload);

      setForm(emptyForm);
      await loadUsers();
    } catch (err: any) {
      console.error("Create user failed:", err);
      
      //Try to pull the error message from FastAPI
      const detail =
      err?.response?.data?.detail ||
      err?.message ||

      "Unknown server error.";
      setError(`Failed to create user: ${detail}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="card">
      <h2>Admin View</h2>

      {error && <p className="error-text">{error}</p>}
      <form onSubmit={handleSubmit} className="admin-form">
        <h3>Create User</h3>
        <div className="admin-form-fields">
          <input
            type="text"
            name="FirstName"
            placeholder="First name"
            value={form.FirstName}
            onChange={handleChange}
            required
          />
          <input
            type="text"
            name="LastName"
            placeholder="Last name"
            value={form.LastName}
            onChange={handleChange}
            required
          />
          <input
            type="email"
            name="Email"
            placeholder="Email"
            value={form.Email}
            onChange={handleChange}
            required
          />
          <label>
            Role:
            <select
              name="Role"
              value={form.Role}
              onChange={handleChange}
              aria-label="User role"
            >
              <option value="ADMIN">ADMIN</option>
              <option value="INSTRUCTOR">INSTRUCTOR</option>
              <option value="IT">IT</option>
            </select>
          </label>
          <button type="submit" disabled={submitting}>
            {submitting ? "Creating..." : "Create user"}
          </button>
        </div>
      </form>

      <h3>Existing Users</h3>
      {loading && <p>Loading users...</p>}

      {!loading && users.length === 0 && <p>No users found.</p>}

      {!loading && users.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>UserId</th>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Active</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.UserId ?? u.Email}>
                <td>{u.UserId}</td>
                <td>
                  {u.FirstName} {u.LastName}
                </td>
                <td>{u.Email}</td>
                <td>{u.Role}</td>
                <td>{u.IsActive ? "Yes" : "No"}</td>
                <td>
                  {u.CreatedAtUtc
                    ? new Date(u.CreatedAtUtc).toLocaleString()
                    : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
};

export default AdminView;