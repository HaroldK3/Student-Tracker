import React, { useEffect, useState } from "react";
import api from "../api";

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

const TeacherView: React.FC = () => {
  const [students, setStudents] = useState<TeacherStudent[]>([]);
  const [loadingStudents, setLoadingStudents] = useState(false);
  const [studentsError, setStudentsError] = useState("");

  const [selectedStudent, setSelectedStudent] = useState<TeacherStudent | null>(
    null
  );

  const [checkins, setCheckins] = useState<CheckIn[]>([]);
  const [loadingCheckins, setLoadingCheckins] = useState(false);
  const [checkinsError, setCheckinsError] = useState("");

  const [feedbackText, setFeedbackText] = useState("");
  const [feedbackStatus, setFeedbackStatus] = useState("");

  useEffect(() => {
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

    loadStudents();
  }, []);

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
    <div className="card">
      <h2>Teacher View</h2>
      <p>View your students, check their recent check-ins, and send feedback.</p>

      <h3>Students</h3>
      {loadingStudents && <p>Loading students...</p>}
      {studentsError && <p className="error-text">{studentsError}</p>}

      {!loadingStudents && students.length === 0 && !studentsError && (
        <p>No students found.</p>
      )}

      {students.length > 0 && (
        <table>
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
                  <button onClick={() => handleSelectStudent(s)}>
                    Select
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {selectedStudent && (
        <>
          <hr />
          <h3>
            Selected Student: {selectedStudent.FirstName}{" "}
            {selectedStudent.LastName} (ID {selectedStudent.StudentId})
          </h3>

          <div className="teacher-section">
            <h4>Send Feedback</h4>
            <label htmlFor="feedback-textarea">Feedback for student</label>
            <textarea
              id="feedback-textarea"
              rows={3}
              className="teacher-feedback-textarea"
              placeholder="Write feedback for this student..."
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
            />
            <br />
            <button onClick={handleSendFeedback}>Send feedback</button>
            {feedbackStatus && <p>{feedbackStatus}</p>}
          </div>

          <div className="teacher-section">
            <h4>Recent Check-ins</h4>
            {loadingCheckins && <p>Loading check-ins...</p>}
            {checkinsError && <p className="error-text">{checkinsError}</p>}

            {!loadingCheckins && checkins.length === 0 && !checkinsError && (
              <p>No check-ins found for this student.</p>
            )}

            {checkins.length > 0 && (
              <table>
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
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default TeacherView;