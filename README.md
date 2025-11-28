🎓 PathMate // Student-Tracker

A cross-platform internship management system built with Python + React.

PathMate is a cross-platform student internship tracking system designed to help universities and organizations monitor student placements, verify location-based check-ins, and maintain accurate progress logs.
This repository includes a React frontend created using Create React App.

🚀 Key Features
📍 Location-Verified Check-ins

GPS/IP-based validation to confirm students are at their assigned internship sites.

Ensures integrity and attendance accountability.

⏱️ Hours & Progress Tracking

Track hours, milestones, and daily activities.

View detailed timesheets and progress summaries.

👥 Multi-Role Access

Dedicated dashboards for students, staff, and administrators.

Role-based permissions for secure and streamlined access.

📝 Feedback & Evaluation

Supervisors can submit evaluations and performance reviews.

Supports academic grading and compliance tracking.

📊 Analytics & Reports

Auto-generated reports for attendance and overall performance.

Exportable for academic credit or institutional reporting.

🔐 Secure Access

Authentication & authorization layers.

Protects student and organizational data.

🧰 Tech Stack
Layer	Technology
Frontend	React (Create React App) / Kivy / React Native
Backend	FastAPI
Database	SQLite
Geolocation	iPapi API
Deployment	GitHub Actions
🧪 React Frontend – Getting Started

This frontend was bootstrapped with Create React App.

📦 Available Scripts

In the project directory, you can run:

npm start

Runs the app in development mode.
Open http://localhost:3000
 in your browser.
Automatically reloads when changes are made.

npm test

Launches the interactive test runner.
See official CRA documentation on testing.

npm run build

Builds the app for production in the build folder.
Includes optimizations, minification, and hashed filenames.

npm run eject

⚠️ One-way operation — cannot be undone!

Copies configuration files (Webpack, Babel, ESLint, etc.) directly into your project so you can fully customize them.

📚 Learn More

Create React App Docs — https://facebook.github.io/create-react-app/docs/getting-started

React Documentation — https://reactjs.org

FastAPI Documentation — https://fastapi.tiangolo.com

🗓️ Development Phases
Sprint 1: Planning & Setup

Focus: Requirements, environment, wireframes, schema, branding.
Deliverables:

User stories (INVEST)

Figma wireframes or sketches

Database ERD

App name & logo

Repository structure + dependencies

Sprint 2: Implementation & Testing

Focus: Core feature coding & integration.
Deliverables:

Backend endpoints + API integration

Student & admin dashboards

Authentication & geolocation functionality

Working prototype demo

Testing & debugging

🧩 Known Issues / Future Improvements

(Section intentionally left open to update as development continues.)

👩‍💻 Authors

Kaylee Harold
Palwasha Newell
Robert Freschi
Jorge Nunez
Toby Crabtree
East Tennessee State University

📚 Student Intern Tracker / PathMate Project

“Track progress. Build accountability. Empower student success.”

======================================================================
                      Running the program
======================================================================

Running the Backend and Frontend
1. Start the Backend (FastAPI)
Open PowerShell and run: Set-Location to root of folder (not backend folder) then run
".\.venv\Scripts\Activate.ps1"
"python -m uvicorn Backend.main:app --host 127.0.0.1 --port 8002 --log-level info"

The backend will be available at http://127.0.0.1:8002/docs

2. Start the Frontend (React)
Open a new PowerShell window and run:
Set-Location to frontend
"npm install"
"npm start"

The frontend will open at http://localhost:3000

