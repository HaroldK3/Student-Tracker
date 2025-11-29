// src/components/TeacherView.tsx
import React, { useEffect, useState } from "react";
import api from "../api";
import TeacherMap from "./TeacherMap";
import "./TeacherView.css";

interface TeacherStudent {
  StudentId: number;
  UniversityId: number;
  FirstName: string;
  LastName: string;
  Email: string;
  Program?: string;
  Year?: string;
  Status?: string;
}

interface CheckIn {
  CheckInId: number;
  StudentId: number;
  CheckInTime: string;
  Approved?: number | boolean;
  [key: string]: any;
}

interface StudentLocation {
  StudentId: number;
  FirstName: string;
  LastName: string;
  Lat: number;
  Lng: number;
  CheckInTime: string;
}

const TeacherView: React.FC = () => {
  const [students, setStudents] = useState<TeacherStudent[]>([]);
  const [loadingStudents, setLoadingStudents] = useState(false);
  const [studentsError, setStudentsError] = useState("");

  const [selectedStudent, setSelectedStudent] =
    useState<TeacherStudent | null>(null);

  const [checkins, setCheckins] = useState<CheckIn[]>([]);
  const [loadingCheckins, setLoadingCheckins] = useState(false);
  const [checkinsError, setCheckinsError] = useState("");

  const [feedbackText, setFeedbackText] = useState("");
  const [feedbackStatus, setFeedbackStatus] = useState("");

  // locations (without map)
  const [locations, setLocations] = useState<StudentLocation[]>([]);
  const [loadingLocations, setLoadingLocations] = useState(false);
  const [locationsError, setLocationsError] = useState("");

  // ---- Load students list ----
  const loadStudents = async () => {
    setLoadingStudents(true);
    setStudentsError("");
    try {
      const resp = await api.get<TeacherStudent[]>("/teacher/students");
      setStudents(resp.data || []);
    } catch (err: any) {
      console.error("Failed to load students:", err);
      const detail =
        err?.response?.data?.detail || err?.message || "Unknown error";
      setStudentsError(`Failed to load students: ${detail}`);
    } finally {
      setLoadingStudents(false);
    }
  };

  useEffect(() => {
    loadStudents();
  }, []);

  // ---- Load today's locations ----
  const loadLocations = async () => {
    setLoadingLocations(true);
    setLocationsError("");
    try {
      const resp = await api.get<StudentLocation[]>("/teacher/locations/today");
      setLocations(resp.data || []);
    } catch (err: any) {
      console.error("Failed to load locations:", err);
      const detail =
        err?.response?.data?.detail || err?.message || "Unknown error";
      setLocationsError(`Failed to load locations: ${detail}`);
    } finally {
      setLoadingLocations(false);
    }
  };

  useEffect(() => {
    loadLocations();
  }, []);

  // ---- Check-ins for a selected student ----
  const loadCheckIns = async (student: TeacherStudent) => {
    setLoadingCheckins(true);
    setCheckinsError("");
    try {
      const resp = await api.get<{ checkins: CheckIn[] }>(
        `/teacher/check_in/${student.StudentId}`
      );
      setCheckins(resp.data?.checkins || []);
    } catch (err: any) {
      console.error("Failed to load check-ins:", err);
      const detail =
        err?.response?.data?.detail || err?.message || "Unknown error";
      setCheckinsError(`Failed to load check-ins: ${detail}`);
      setCheckins([]);
    } finally {
      setLoadingCheckins(false);
    }
  };

  const handleSelectStudent = (student: TeacherStudent) => {
    setSelectedStudent(student);
    setFeedbackText("");
    setFeedbackStatus("");
    loadCheckIns(student);
  };

  const handleSendFeedback = async () => {
    if (!selectedStudent) return;
    if (!feedbackText.trim()) {
      setFeedbackStatus("Please enter some feedback text first.");
      return;
    }

    setFeedbackStatus("Sending feedback...");
    try {
      await api.post(
        `/teacher/feedback/student/${selectedStudent.StudentId}`,
        null,
        {
          params: { feedback: feedbackText },
        }
      );
      setFeedbackStatus("Feedback sent ✅");
      setFeedbackText("");
    } catch (err: any) {
      console.error("Failed to send feedback:", err);
      const detail =
        err?.response?.data?.detail || err?.message || "Unknown error";
      setFeedbackStatus(`Failed to send feedback: ${detail}`);
    }
  };

  const handleApproveCheckIn = async (checkinId: number) => {
    try {
      await api.put(`/teacher/check_in/${checkinId}/approve`);
      if (selectedStudent) {
        await loadCheckIns(selectedStudent);
      }
    } catch (err: any) {
      console.error("Failed to approve check-in:", err);
      const detail =
        err?.response?.data?.detail || err?.message || "Unknown error";
      setCheckinsError(`Failed to approve check-in: ${detail}`);
    }
  };

  return (
    <section className="card teacher-card">
      {/* Header */}
      <header className="teacher-header">
        <h2 className="teacher-title">Teacher View</h2>
        <p className="teacher-subtitle">
          View your students, check their recent check-ins, and send feedback.
        </p>
      </header>

      {/* -------- LOCATIONS (TABLE) -------- */}
      <div className="teacher-section">
        <div className="teacher-section-header">
          <h3 className="teacher-section-title">Student Locations (Today)</h3>
          <button className="btn btn-secondary" onClick={loadLocations}>
            Refresh locations
          </button>
        </div>

        {loadingLocations && <p>Loading locations...</p>}
        {locationsError && <p className="error-text">{locationsError}</p>}

        {!loadingLocations && locations.length === 0 && !locationsError && (
          <p className="teacher-muted">No location check-ins yet today.</p>
        )}

        {locations.length > 0 && (
          <div className="teacher-table-wrapper">
            <table className="teacher-table teacher-locations-table">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Latitude</th>
                  <th>Longitude</th>
                  <th>Time</th>
                  <th>Map</th>
                </tr>
              </thead>
              <tbody>
                {locations.map((loc) => (
                  <tr key={`${loc.StudentId}-${loc.CheckInTime}`}>
                    <td>
                      {loc.FirstName} {loc.LastName} (ID {loc.StudentId})
                    </td>
                    <td>{loc.Lat.toFixed(5)}</td>
                    <td>{loc.Lng.toFixed(5)}</td>
                    <td>{new Date(loc.CheckInTime).toLocaleTimeString()}</td>
                    <td>
                      <a
                        href={`https://www.google.com/maps?q=${loc.Lat},${loc.Lng}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        View on map
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* -------- STUDENT TABLE SECTION -------- */}
      <div className="teacher-section">
        <h3 className="teacher-section-title">Students</h3>

        {loadingStudents && <p>Loading students...</p>}
        {studentsError && <p className="error-text">{studentsError}</p>}

        {!loadingStudents && students.length === 0 && !studentsError && (
          <p className="teacher-muted">No students found.</p>
        )}

        {students.length > 0 && (
          <div className="teacher-table-wrapper">
            <table className="teacher-table teacher-students-table">
              <thead>
                <tr>
                  <th>StudentId</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Program / Year</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {students.map((s) => (
                  <tr key={s.StudentId}>
                    <td>{s.StudentId}</td>
                    <td>
                      {s.FirstName} {s.LastName}
                    </td>
                    <td>{s.Email}</td>
                    <td>
                      {s.Program || "-"} / {s.Year || "-"}
                    </td>
                    <td>{s.Status || "-"}</td>
                    <td>
                      <button
                        className="btn btn-primary btn-small"
                        onClick={() => handleSelectStudent(s)}
                      >
                        Select
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* -------- SELECTED STUDENT DETAILS -------- */}
      {selectedStudent && (
        <>
          <div className="teacher-section">
            <h3 className="teacher-section-title">
              Selected Student: {selectedStudent.FirstName}{" "}
              {selectedStudent.LastName} (ID {selectedStudent.StudentId})
            </h3>

            <div className="teacher-feedback">
              <h4 className="teacher-subsection-title">Send Feedback</h4>
              <label className="teacher-label" htmlFor="feedback-textarea">
                Feedback for student
              </label>
              <textarea
                id="feedback-textarea"
                rows={3}
                className="teacher-feedback-textarea"
                placeholder="Write feedback for this student..."
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
              />
              <div className="teacher-feedback-actions">
                <button className="btn btn-primary" onClick={handleSendFeedback}>
                  Send feedback
                </button>
              </div>
              {feedbackStatus && (
                <p className="teacher-feedback-status">{feedbackStatus}</p>
              )}
            </div>
          </div>

          <div className="teacher-section">
            <h4 className="teacher-subsection-title">Recent Check-ins</h4>

            {loadingCheckins && <p>Loading check-ins...</p>}
            {checkinsError && <p className="error-text">{checkinsError}</p>}

            {!loadingCheckins && checkins.length === 0 && !checkinsError && (
              <p className="teacher-muted">
                No check-ins found for this student.
              </p>
            )}

            {checkins.length > 0 && (
              <div className="teacher-table-wrapper">
                <table className="teacher-table teacher-checkins-table">
                  <thead>
                    <tr>
                      <th>CheckInId</th>
                      <th>Time</th>
                      <th>Approved</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {checkins.map((c) => (
                      <tr key={c.CheckInId}>
                        <td>{c.CheckInId}</td>
                        <td>{c.CheckInTime}</td>
                        <td>
                          {c.Approved === 1 || c.Approved === true
                            ? "Yes"
                            : "No"}
                        </td>
                        <td>
                          {!(c.Approved === 1 || c.Approved === true) && (
                            <button
                              className="btn btn-secondary btn-small"
                              onClick={() => handleApproveCheckIn(c.CheckInId)}
                            >
                              Approve
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}

      {/* -------- MAP SECTION -------- */}
      <div className="teacher-section">
        <h3 className="teacher-section-title">Today's Student Locations</h3>
        <TeacherMap />
      </div>
    </section>
  );
};

export default TeacherView;
