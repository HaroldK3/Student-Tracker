USE StudentTracker;

SELECT s.name AS SchemaName
FROM sys.schemas s
WHERE s.name = 'st';

SELECT SCHEMA_NAME(t.schema_id) AS SchemaName, t.name AS TableName
FROM sys.tables t
WHERE SCHEMA_NAME(t.schema_id) = 'st'
ORDER BY t.name;

EXEC sp_help 'st.Users';
EXEC sp_help 'st.Students';
EXEC sp_help 'st.Positions';
EXEC sp_help 'st.Cohorts';
EXEC sp_help 'st.StudentAssignments';
EXEC sp_help 'st.Attendance';

-- Users
SELECT * FROM st.Users ORDER BY UserId;

-- Students
SELECT * FROM st.Students ORDER BY StudentId;

-- Positions
SELECT * FROM st.Positions ORDER BY PositionId;

-- Cohorts
SELECT * FROM st.Cohorts ORDER BY CohortId;

-- Assignments
SELECT * FROM st.StudentAssignments ORDER BY AssignmentId;

-- Attendance
SELECT * FROM st.Attendance ORDER BY AttendanceId;

-- Today’s roster by position (1)
SELECT
  s.StudentId, s.FirstName, s.LastName,
  a.AttendanceDate, a.Status, a.AttendanceTime
FROM st.StudentAssignments sa
JOIN st.Students s ON s.StudentId = sa.StudentId
LEFT JOIN st.Attendance a
  ON a.StudentId = s.StudentId
 AND a.PositionId = sa.PositionId
 AND a.AttendanceDate = CONVERT(date, SYSUTCDATETIME())
WHERE sa.PositionId = 1
ORDER BY s.LastName, s.FirstName;