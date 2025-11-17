import React, { useState } from "react";
import AdminView from "./components/AdminView";
import StudentView from "./components/StudentView";
import TeacherView from "./components/TeacherView";
import "./App.css";
import logo from "./logo.png";

type View = "admin" | "student" | "teacher";

const App: React.FC = () => {
  const [view, setView] = useState<View>("admin");
  const [studentIdInput, setStudentIdInput] = useState<string>("1");

  return (
    <div className="App">
      <header className="App-header">

        {/* --- LOGO --- */}
        <div className="logo-container">
          <img
            src={logo}
            alt="App Logo"
            className="app-logo"
          />
        </div>

        <h1>Student Tracker Frontend</h1>

        {/* --- NAV TABS --- */}
        <nav className="nav-tabs">
          <button
            className={view === "admin" ? "active" : ""}
            onClick={() => setView("admin")}
          >
            Admin
          </button>

          <button
            className={view === "student" ? "active" : ""}
            onClick={() => setView("student")}
          >
            Student
          </button>

          <button
            className={view === "teacher" ? "active" : ""}
            onClick={() => setView("teacher")}
          >
            Teacher
          </button>
        </nav>
      </header>

      {/* --- PAGE CONTENT --- */}
      <main className="App-main">
        <p>Current view: {view}</p>

        {view === "admin" && <AdminView />}

        {view === "student" && (
          <div>
            <label htmlFor="studentIdInput">
              Student ID:&nbsp;
            </label>

            <input
              id="studentIdInput"
              value={studentIdInput}
              placeholder="Enter student ID"
              onChange={(e) => setStudentIdInput(e.target.value)}
            />

            <StudentView studentId={Number(studentIdInput) || 1} />
          </div>
        )}

        {view === "teacher" && <TeacherView />}
      </main>
    </div>
  );
};

export default App;