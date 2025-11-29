import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import reportWebVitals from "./reportWebVitals";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);

// 🚫 Removed <React.StrictMode> to avoid double-mounting Leaflet maps
root.render(<App />);

// Optional perf reporting
reportWebVitals();
