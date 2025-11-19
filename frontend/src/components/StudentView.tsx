// src/components/StudentView.tsx
import React, { useEffect, useState } from "react";
import api from "../api";

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

      <hr />

      <h3>Location Check-in</h3>
      <button onClick={handleLocationCheckIn}>
        Check in at my current location
      </button>
      {checkinMessage && <p className="info-text">{checkinMessage}</p>}
    </div>
  );
};

export default StudentView;