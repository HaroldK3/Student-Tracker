// src/components/StudentView.tsx
import React, { useEffect, useState } from "react";
import api from "../api";
import "./StudentView.css";

interface StudentViewProps {
  studentId: number;
}

interface StudentProfile {
  StudentId: number;
  UniversityId: number;
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
  const [checkinMessage, setCheckinMessage] = useState<string>("");

  // ---- Load student profile from backend ----
  useEffect(() => {
    const loadProfile = async () => {
      try {
        setError("");
        setProfile(null);

        // matches Backend.routes.admin: /admin/student/{student_id}
        const res = await api.get<StudentProfile>(`/admin/student/${studentId}`);
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

  // ---- Location check-in ----
  const handleLocationCheckIn = async () => {
    setCheckinMessage("");

    if (!navigator.geolocation) {
      setCheckinMessage("Geolocation is not supported in this browser.");
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords;
        try {
          await api.post("/student/checkin/location", {
            StudentId: studentId,
            Status: "PRESENT",
            Lat: latitude,
            Lng: longitude,
          });
          setCheckinMessage("Check-in saved with your current location ✅");
        } catch (err: any) {
          console.error(err);
          setCheckinMessage("Failed to send check-in to the server.");
        }
      },
      (geoErr: GeolocationPositionError) => {
        console.error(geoErr);
        setCheckinMessage(
          "Could not get your location. Please allow location access."
        );
      }
    );
  };

  return (
    <section className="card student-card">
      <header className="student-header">
        <h2 className="student-title">Student View</h2>
        <p className="student-subtitle">
          Student ID from App: <span className="student-id">{studentId}</span>
        </p>
      </header>

      {error && <p className="error-text">{error}</p>}
      {!error && !profile && <p>Loading profile...</p>}

      {profile && (
        <div className="student-section">
          <h3 className="student-section-title">Profile</h3>

          <dl className="student-fields">
            <div className="student-field">
              <dt>Name:</dt>
              <dd>
                {profile.FirstName} {profile.LastName}
              </dd>
            </div>
            <div className="student-field">
              <dt>University ID:</dt>
              <dd>{profile.UniversityId}</dd>
            </div>
            <div className="student-field">
              <dt>Email:</dt>
              <dd>{profile.Email}</dd>
            </div>
            <div className="student-field">
              <dt>Phone:</dt>
              <dd>{profile.PhoneE164 || "—"}</dd>
            </div>
            <div className="student-field">
              <dt>Program:</dt>
              <dd>{profile.Program}</dd>
            </div>
            <div className="student-field">
              <dt>Year:</dt>
              <dd>{profile.Year}</dd>
            </div>
            <div className="student-field">
              <dt>Status:</dt>
              <dd>{profile.Status}</dd>
            </div>
            <div className="student-field">
              <dt>GPA:</dt>
              <dd>{profile.GPA ?? "N/A"}</dd>
            </div>
            <div className="student-field">
              <dt>Created At:</dt>
              <dd>{new Date(profile.CreatedAtUtc).toLocaleString()}</dd>
            </div>
          </dl>
        </div>
      )}

      <div className="student-section">
        <h3 className="student-section-title">Location Check-in</h3>
        <button
          className="student-checkin-btn"
          onClick={handleLocationCheckIn}
        >
          Check in at my current location
        </button>
        {checkinMessage && (
          <p className="info-text student-checkin-message">
            {checkinMessage}
          </p>
        )}
      </div>
    </section>
  );
};

export default StudentView;
