# Student-Tracker Database (SQL Server)

## What this is
Minimum viable schema + seed data for the Student Tracker app:
- Users (ADMIN/INSTRUCTOR/IT)
- Students (university-only)
- Positions (intern/placement)
- Cohorts (optional groups by instructor/term)
- StudentAssignments (student → position/cohort)
- Attendance (PRESENT/ABSENT/TARDY, one per student/position/day)

## How to create/update the DB

### Option A: SSMS
1. Open `db/sql/01_create_studenttracker.sql` in SSMS.
2. Press **Execute**. It creates DB `StudentTracker` and all tables + seed data.

### Option B: sqlcmd (Windows)
```bat
sqlcmd -S . -E -i "db\sql\01_create_studenttracker.sql"