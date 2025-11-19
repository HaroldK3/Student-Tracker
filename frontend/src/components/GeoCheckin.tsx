import React, { useState } from 'react';
import api from '../api';

export default function GeoCheckin({ studentId }: { studentId: number }) {
  const [status, setStatus] = useState<string | null>(null);

  const checkIn = () => {
    if (!navigator.geolocation) {
      setStatus('Geolocation not supported.');
      return;
    }
    setStatus('Getting location…');
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        try {
          const resp = await api.post('/student/checkin/location', { StudentId: studentId, Lat: lat, Lng: lng });
          setStatus(`Checked in!`);
        } catch (err) {
          setStatus('Server error.');
        }
      },
      (err) => setStatus(`Location error: ${err.message}`),
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  return (
    <div>
      <button onClick={checkIn}>Check In (Use My Location)</button>
      {status && <div>{status}</div>}
    </div>
  );
}
