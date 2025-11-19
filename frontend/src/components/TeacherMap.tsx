import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import api from '../api';
import 'leaflet/dist/leaflet.css';

export default function TeacherMap() {
  const [locs, setLocs] = useState<any[]>([]);

  useEffect(() => {
    api.get('/teacher/locations/today').then(r => setLocs(r.data.value || r.data)).catch(console.error);
  }, []);

  if (!locs.length) return <div>No check-ins yet.</div>;

  const center = [locs[0].Lat, locs[0].Lng];

  return (
    <MapContainer center={center as [number, number]} zoom={13} style={{ height: 400 }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {locs.map(l => (
        <Marker key={l.StudentId + l.CheckInTime} position={[l.Lat, l.Lng]}>
          <Popup>
            {l.FirstName} {l.LastName}<br />
            {new Date(l.CheckInTime).toLocaleTimeString()}
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
