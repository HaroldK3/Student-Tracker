import React, { useEffect, useState } from "react";
import api from "../api";

interface StudentViewProps {
  studentId: number;
}

interface StudentProfile {
  StudentId: number;
  UniversityId: string;
  FirstName: string;
  LastName: string;
  Email: string;
  PhoneE164?: string | null;
  Program: string;
  Year: string;
  Status: string;
  GPA?: number | null;
  CreatedAtUtc: string;
}

const StudentView: React.FC<StudentViewProps> = ({ studentId }) => {
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const loadProfile = async () => {
      try {
        setError("");
        setProfile(null);
        const res = await api.get<StudentProfile>(`/student/profile/${studentId}`);
        setProfile(res.data);
      } catch (e: any) {
        console.error(e);
        setError("Failed to load student profile.");
      }
    };

    if (studentId) {
      loadProfile();
    }
  }, [studentId]);

  return (
    <div className="card">
      <h2>Student View</h2>
      <p>Student ID from App: {studentId}</p>

      {error && <p className="error-text">{error}</p>}
      {!error && !profile && <p>Loading profile...</p>}

      {profile && (
        <>
          <h3>Profile</h3>
          <p>
            <strong>Name:</strong> {profile.FirstName} {profile.LastName}
          </p>
          <p>
            <strong>University ID:</strong> {profile.UniversityId}
          </p>
          <p>
            <strong>Email:</strong> {profile.Email}
          </p>
          <p>
            <strong>Phone:</strong> {profile.PhoneE164 || "—"}
          </p>
          <p>
            <strong>Program:</strong> {profile.Program}
          </p>
          <p>
            <strong>Year:</strong> {profile.Year}
          </p>
          <p>
            <strong>Status:</strong> {profile.Status}
          </p>
          <p>
            <strong>GPA:</strong> {profile.GPA ?? "N/A"}
          </p>
          <p>
            <strong>Created At:</strong>{" "}
            {new Date(profile.CreatedAtUtc).toLocaleString()}
          </p>
        </>
      )}
    </div>
  );
};

export default StudentView;