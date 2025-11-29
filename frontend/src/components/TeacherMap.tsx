// src/components/TeacherMap.tsx
import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import api from "../api";
import "leaflet/dist/leaflet.css";

interface StudentLocation {
  StudentId: number;
  FirstName: string;
  LastName: string;
  Lat: number;
  Lng: number;
  CheckInTime: string;
}

const TeacherMap: React.FC = () => {
  const [locs, setLocs] = useState<StudentLocation[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<StudentLocation[]>("/teacher/locations/today")
      .then((res) => {
        const data = Array.isArray(res.data)
          ? res.data
          : (res.data as any).value || [];
        setLocs(data);
      })
      .catch((err) => {
        console.error("Failed to load map locations:", err);
        setError("Failed to load map locations.");
      });
  }, []);

  if (error) {
    return <p className="error-text">{error}</p>;
  }

  if (!locs.length) {
    return <p className="teacher-muted">No check-ins yet.</p>;
  }

  const center: [number, number] = [locs[0].Lat, locs[0].Lng];

  return (
    <div className="teacher-map-shell">
      <MapContainer
        center={center}
        zoom={13}
        scrollWheelZoom={false}
        className="teacher-map-inner"
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {locs.map((l) => (
          <Marker key={`${l.StudentId}-${l.CheckInTime}`} position={[l.Lat, l.Lng]}>
            <Popup>
              {l.FirstName} {l.LastName}
              <br />
              {new Date(l.CheckInTime).toLocaleTimeString()}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default TeacherMap;
