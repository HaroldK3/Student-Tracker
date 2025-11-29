// src/components/AdminView.tsx
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

interface AdminStudent {
  StudentId?: number;
  UniversityId: string;
  FirstName: string;
  LastName: string;
  Email: string;
  Program?: string;
  Year?: string;
  Status?: string;
  CreatedAtUtc?: string;
}

const emptyUserForm: AdminUser = {
  FirstName: "",
  LastName: "",
  Email: "",
  Role: "INSTRUCTOR",
};

const emptyStudentForm: AdminStudent = {
  UniversityId: "",
  FirstName: "",
  LastName: "",
  Email: "",
  Program: "",
  Year: "",
  Status: "Active",
};

const AdminView: React.FC = () => {
  // ---------- USER STATE ----------
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [userForm, setUserForm] = useState<AdminUser>(emptyUserForm);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [userSubmitting, setUserSubmitting] = useState(false);
  const [deletingUserId, setDeletingUserId] = useState<number | null>(null);

  const [editingUserId, setEditingUserId] = useState<number | null>(null);
  const [editUserForm, setEditUserForm] = useState<Partial<AdminUser>>({});

  // ---------- STUDENT STATE ----------
  const [students, setStudents] = useState<AdminStudent[]>([]);
  const [studentForm, setStudentForm] =
    useState<AdminStudent>(emptyStudentForm);
  const [loadingStudents, setLoadingStudents] = useState(false);
  const [studentSubmitting, setStudentSubmitting] = useState(false);
  const [deletingStudentId, setDeletingStudentId] = useState<number | null>(
    null
  );

  const [editingStudentId, setEditingStudentId] = useState<number | null>(null);
  const [editStudentForm, setEditStudentForm] =
    useState<Partial<AdminStudent>>({});

  // ---------- ERRORS ----------
  const [userError, setUserError] = useState<string>("");
  const [studentError, setStudentError] = useState<string>("");

  // ================== LOADERS ==================

  const loadUsers = async () => {
    try {
      setLoadingUsers(true);
      setUserError("");
      const res = await api.get<AdminUser[]>("/admin/users");
      setUsers(res.data);
    } catch (e: any) {
      console.error(e);
      const detail =
        e?.response?.data?.detail || e?.message || "Unknown server error.";
      setUserError(`Failed to load users: ${detail}`);
    } finally {
      setLoadingUsers(false);
    }
  };

  const loadStudents = async () => {
    try {
      setLoadingStudents(true);
      setStudentError("");
      const res = await api.get<AdminStudent[]>("/admin/students");
      setStudents(res.data || []);
    } catch (e: any) {
      console.error(e);
      const detail =
        e?.response?.data?.detail || e?.message || "Unknown server error.";
      setStudentError(`Failed to load students: ${detail}`);
    } finally {
      setLoadingStudents(false);
    }
  };

  useEffect(() => {
    loadUsers();
    loadStudents();
  }, []);

  // ================== USER HANDLERS ==================

  const handleUserChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setUserForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleEditUserChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setEditUserForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setUserSubmitting(true);
    setUserError("");

    try {
      const payload = {
        FirstName: userForm.FirstName,
        LastName: userForm.LastName,
        Email: userForm.Email,
        Role: userForm.Role,
      };

      await api.post("/admin/users/create_user", payload);
      setUserForm(emptyUserForm);
      await loadUsers();
    } catch (err: any) {
      console.error("Create user failed:", err);
      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        "Unknown server error.";
      setUserError(`Failed to create user: ${detail}`);
    } finally {
      setUserSubmitting(false);
    }
  };

  const startEditingUser = (u: AdminUser) => {
    if (!u.UserId) return;
    setEditingUserId(u.UserId);
    setEditUserForm({
      FirstName: u.FirstName,
      LastName: u.LastName,
      Email: u.Email,
      Role: u.Role,
    });
  };

  const cancelEditingUser = () => {
    setEditingUserId(null);
    setEditUserForm({});
  };

  const handleSaveUser = async (userId: number) => {
    try {
      setUserError("");

      const payload: Partial<AdminUser> = {
        FirstName: editUserForm.FirstName,
        LastName: editUserForm.LastName,
        Email: editUserForm.Email,
        Role: editUserForm.Role,
      };

      await api.put(`/admin/users/${userId}`, payload);

      // Update local list
      setUsers((prev) =>
        prev.map((u) =>
          u.UserId === userId
            ? {
                ...u,
                ...payload,
              }
            : u
        )
      );

      cancelEditingUser();
    } catch (err: any) {
      console.error("Update user failed:", err);
      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        "Unknown server error.";
      setUserError(`Failed to update user: ${detail}`);
    }
  };

  const handleDeleteUser = async (userId?: number) => {
    if (!userId) return;

    const confirmed = window.confirm(
      "Are you sure you want to permanently delete this user?"
    );
    if (!confirmed) return;

    try {
      setUserError("");
      setDeletingUserId(userId);
      await api.delete(`/admin/users/${userId}`);

      setUsers((prev) => prev.filter((u) => u.UserId !== userId));
    } catch (err: any) {
      console.error("Delete user failed:", err);
      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        "Unknown server error.";
      setUserError(`Failed to delete user: ${detail}`);
    } finally {
      setDeletingUserId(null);
    }
  };

  // ================== STUDENT HANDLERS ==================

  const handleStudentChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setStudentForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleCreateStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    setStudentSubmitting(true);
    setStudentError("");

    try {
      const payload = {
        UniversityId: studentForm.UniversityId,
        FirstName: studentForm.FirstName,
        LastName: studentForm.LastName,
        Email: studentForm.Email,
        Program: studentForm.Program,
        Year: studentForm.Year,
        Status: studentForm.Status || "Active",
      };

      await api.post("/admin/students", payload);

      setStudentForm(emptyStudentForm);
      await loadStudents();
    } catch (err: any) {
      console.error("Create student failed:", err);
      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        "Unknown server error.";
      setStudentError(`Failed to create student: ${detail}`);
    } finally {
      setStudentSubmitting(false);
    }
  };

  const handleEditStudentChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setEditStudentForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const startEditingStudent = (s: AdminStudent) => {
    if (!s.StudentId) return;
    setEditingStudentId(s.StudentId);
    setEditStudentForm({
      UniversityId: s.UniversityId,
      FirstName: s.FirstName,
      LastName: s.LastName,
      Email: s.Email,
      Program: s.Program,
      Year: s.Year,
      Status: s.Status ?? "Active",
    });
  };

  const cancelEditingStudent = () => {
    setEditingStudentId(null);
    setEditStudentForm({});
  };

  const handleSaveStudent = async (studentId: number) => {
    try {
      setStudentError("");

      const payload: Partial<AdminStudent> = {
        UniversityId: editStudentForm.UniversityId,
        FirstName: editStudentForm.FirstName,
        LastName: editStudentForm.LastName,
        Email: editStudentForm.Email,
        Program: editStudentForm.Program,
        Year: editStudentForm.Year,
        Status: editStudentForm.Status,
      };

      await api.put(`/admin/students/${studentId}`, payload);

      setStudents((prev) =>
        prev.map((s) =>
          s.StudentId === studentId
            ? {
                ...s,
                ...payload,
              }
            : s
        )
      );

      cancelEditingStudent();
    } catch (err: any) {
      console.error("Update student failed:", err);
      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        "Unknown server error.";
      setStudentError(`Failed to update student: ${detail}`);
    }
  };

  const handleDeleteStudent = async (studentId?: number) => {
    if (!studentId) return;

    const confirmed = window.confirm(
      "Are you sure you want to permanently delete this student?"
    );
    if (!confirmed) return;

    try {
      setStudentError("");
      setDeletingStudentId(studentId);

      // IMPORTANT: backend route is singular: /admin/student/{id}
      await api.delete(`/admin/student/${studentId}`);

      setStudents((prev) =>
        prev.filter((s) => s.StudentId !== studentId)
      );
    } catch (err: any) {
      console.error("Delete student failed:", err);
      const detail =
        err?.response?.data?.detail ||
        err?.message ||
        "Unknown server error.";
      setStudentError(`Failed to delete student: ${detail}`);
    } finally {
      setDeletingStudentId(null);
    }
  };

  // ================== RENDER ==================

  return (
    <section className="admin-card">
      <h2 className="admin-title">Admin View</h2>

      {/* ---------- USER ERRORS ---------- */}
      {userError && <p className="error-text">{userError}</p>}

      {/* ---------- CREATE USER ---------- */}
      <form onSubmit={handleCreateUser} className="admin-form">
        <h3 className="section-title">Create User</h3>
        <div className="admin-form-fields">
          <input
            type="text"
            name="FirstName"
            placeholder="First name"
            value={userForm.FirstName}
            onChange={handleUserChange}
            required
          />
          <input
            type="text"
            name="LastName"
            placeholder="Last name"
            value={userForm.LastName}
            onChange={handleUserChange}
            required
          />
          <input
            type="email"
            name="Email"
            placeholder="Email"
            value={userForm.Email}
            onChange={handleUserChange}
            required
          />
          <label className="role-label">
            Role:
            <select
              name="Role"
              value={userForm.Role}
              onChange={handleUserChange}
              aria-label="User role"
            >
              <option value="ADMIN">ADMIN</option>
              <option value="INSTRUCTOR">INSTRUCTOR</option>
              <option value="IT">IT</option>
            </select>
          </label>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={userSubmitting}
          >
            {userSubmitting ? "Creating..." : "Create user"}
          </button>
        </div>
      </form>

      {/* ---------- EXISTING USERS ---------- */}
      <div className="admin-table-wrapper">
        <h3 className="section-title">Existing Users</h3>

        {loadingUsers && <p>Loading users...</p>}
        {!loadingUsers && users.length === 0 && <p>No users found.</p>}

        {!loadingUsers && users.length > 0 && (
          <table className="data-table">
            <thead>
              <tr>
                <th>UserId</th>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Active</th>
                <th>Created</th>
                <th className="actions-col">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => {
                const isEditing = editingUserId === u.UserId;
                return (
                  <tr key={u.UserId ?? u.Email}>
                    <td>{u.UserId}</td>
                    <td>
                      {isEditing ? (
                        <>
                          <input
                            type="text"
                            name="FirstName"
                            value={editUserForm.FirstName ?? ""}
                            onChange={handleEditUserChange}
                            placeholder="First name"
                            className="admin-inline-input"
                          />
                          <input
                            type="text"
                            name="LastName"
                            value={editUserForm.LastName ?? ""}
                            onChange={handleEditUserChange}
                            placeholder="Last name"
                            className="admin-inline-input"
                          />
                        </>
                      ) : (
                        <>
                          {u.FirstName} {u.LastName}
                        </>
                      )}
                    </td>
                    <td>
                      {isEditing ? (
                        <input
                          type="email"
                          name="Email"
                          value={editUserForm.Email ?? ""}
                          onChange={handleEditUserChange}
                          placeholder="Email"
                          className="admin-inline-input"
                        />
                      ) : (
                        u.Email
                      )}
                    </td>
                    <td>
                      {isEditing ? (
                        <select
                          name="Role"
                          value={editUserForm.Role ?? u.Role}
                          onChange={handleEditUserChange}
                          className="admin-inline-input"
                        >
                          <option value="ADMIN">ADMIN</option>
                          <option value="INSTRUCTOR">INSTRUCTOR</option>
                          <option value="IT">IT</option>
                        </select>
                      ) : (
                        u.Role
                      )}
                    </td>
                    <td>{u.IsActive ? "Yes" : "No"}</td>
                    <td>
                      {u.CreatedAtUtc
                        ? new Date(u.CreatedAtUtc).toLocaleString()
                        : "—"}
                    </td>
                    <td className="actions-col">
                      <div className="admin-actions">
                        {isEditing ? (
                          <>
                            <button
                              className="btn btn-primary btn-small"
                              type="button"
                              onClick={() =>
                                u.UserId && handleSaveUser(u.UserId)
                              }
                            >
                              Save
                            </button>
                            <button
                              className="btn btn-secondary btn-small"
                              type="button"
                              onClick={cancelEditingUser}
                            >
                              Cancel
                            </button>
                          </>
                        ) : (
                          <>
                            <button
                              className="btn btn-primary btn-small"
                              type="button"
                              onClick={() => startEditingUser(u)}
                            >
                              Edit
                            </button>
                            <button
                              className="btn btn-delete btn-small"
                              type="button"
                              disabled={deletingUserId === u.UserId}
                              onClick={() => handleDeleteUser(u.UserId)}
                            >
                              {deletingUserId === u.UserId
                                ? "Deleting..."
                                : "Delete"}
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* ---------- STUDENT ERRORS ---------- */}
      {studentError && <p className="error-text">{studentError}</p>}

      {/* ---------- CREATE STUDENT ---------- */}
      <form onSubmit={handleCreateStudent} className="admin-form">
        <h3 className="section-title">Create Student</h3>
        <div className="admin-form-fields">
          <input
            type="text"
            name="UniversityId"
            placeholder="University ID"
            value={studentForm.UniversityId}
            onChange={handleStudentChange}
            required
          />
          <input
            type="text"
            name="FirstName"
            placeholder="First name"
            value={studentForm.FirstName}
            onChange={handleStudentChange}
            required
          />
          <input
            type="text"
            name="LastName"
            placeholder="Last name"
            value={studentForm.LastName}
            onChange={handleStudentChange}
            required
          />
          <input
            type="email"
            name="Email"
            placeholder="Email"
            value={studentForm.Email}
            onChange={handleStudentChange}
            required
          />
          <input
            type="text"
            name="Program"
            placeholder="Program (e.g. BS CS)"
            value={studentForm.Program ?? ""}
            onChange={handleStudentChange}
          />
          <input
            type="text"
            name="Year"
            placeholder="Year (e.g. Junior)"
            value={studentForm.Year ?? ""}
            onChange={handleStudentChange}
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={studentSubmitting}
          >
            {studentSubmitting ? "Creating..." : "Create student"}
          </button>
        </div>
      </form>

      {/* ---------- EXISTING STUDENTS ---------- */}
      <div className="admin-table-wrapper">
        <h3 className="section-title">Existing Students</h3>

        {loadingStudents && <p>Loading students...</p>}
        {!loadingStudents && students.length === 0 && (
          <p>No students found.</p>
        )}

        {!loadingStudents && students.length > 0 && (
          <table className="data-table">
            <thead>
              <tr>
                <th>StudentId</th>
                <th>Name</th>
                <th>Email</th>
                <th>UniversityId</th>
                <th>Program / Year</th>
                <th>Status</th>
                <th className="actions-col">Actions</th>
              </tr>
            </thead>
            <tbody>
              {students.map((s) => {
                const isEditing = editingStudentId === s.StudentId;
                return (
                  <tr key={s.StudentId ?? s.Email}>
                    <td>{s.StudentId}</td>
                    <td>
                      {isEditing ? (
                        <>
                          <input
                            className="admin-inline-input"
                            type="text"
                            name="FirstName"
                            value={editStudentForm.FirstName ?? ""}
                            onChange={handleEditStudentChange}
                            placeholder="First name"
                          />
                          <input
                            className="admin-inline-input"
                            type="text"
                            name="LastName"
                            value={editStudentForm.LastName ?? ""}
                            onChange={handleEditStudentChange}
                            placeholder="Last name"
                          />
                        </>
                      ) : (
                        <>
                          {s.FirstName} {s.LastName}
                        </>
                      )}
                    </td>
                    <td>
                      {isEditing ? (
                        <input
                          className="admin-inline-input"
                          type="email"
                          name="Email"
                          value={editStudentForm.Email ?? ""}
                          onChange={handleEditStudentChange}
                          placeholder="Email"
                        />
                      ) : (
                        s.Email
                      )}
                    </td>
                    <td>
                      {isEditing ? (
                        <input
                          className="admin-inline-input"
                          type="text"
                          name="UniversityId"
                          value={editStudentForm.UniversityId ?? ""}
                          onChange={handleEditStudentChange}
                          placeholder="University ID"
                        />
                      ) : (
                        s.UniversityId
                      )}
                    </td>
                    <td>
                      {isEditing ? (
                        <>
                          <input
                            className="admin-inline-input"
                            type="text"
                            name="Program"
                            value={editStudentForm.Program ?? ""}
                            onChange={handleEditStudentChange}
                            placeholder="Program"
                          />
                          <input
                            className="admin-inline-input"
                            type="text"
                            name="Year"
                            value={editStudentForm.Year ?? ""}
                            onChange={handleEditStudentChange}
                            placeholder="Year"
                          />
                        </>
                      ) : (
                        <>
                          {s.Program || "-"} / {s.Year || "-"}
                        </>
                      )}
                    </td>
                    <td>
                      {isEditing ? (
                        <select
                          className="admin-inline-input"
                          name="Status"
                          value={editStudentForm.Status ?? s.Status ?? "Active"}
                          onChange={handleEditStudentChange}
                        >
                          <option value="Active">Active</option>
                          <option value="Inactive">Inactive</option>
                          <option value="OnLeave">OnLeave</option>
                          <option value="Gone">Gone</option>
                        </select>
                      ) : (
                        s.Status || "Active"
                      )}
                    </td>
                    <td className="actions-col">
                      <div className="admin-actions">
                        {isEditing ? (
                          <>
                            <button
                              className="btn btn-primary btn-small"
                              type="button"
                              onClick={() =>
                                s.StudentId && handleSaveStudent(s.StudentId)
                              }
                            >
                              Save
                            </button>
                            <button
                              className="btn btn-secondary btn-small"
                              type="button"
                              onClick={cancelEditingStudent}
                            >
                              Cancel
                            </button>
                          </>
                        ) : (
                          <>
                            <button
                              className="btn btn-primary btn-small"
                              type="button"
                              onClick={() => startEditingStudent(s)}
                            >
                              Edit
                            </button>
                            <button
                              className="btn btn-delete btn-small"
                              type="button"
                              disabled={deletingStudentId === s.StudentId}
                              onClick={() => handleDeleteStudent(s.StudentId)}
                            >
                              {deletingStudentId === s.StudentId
                                ? "Deleting..."
                                : "Delete"}
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
};

export default AdminView;
