/* ===== 1) Create DB ===== */
IF DB_ID('StudentTracker') IS NULL
BEGIN
  CREATE DATABASE StudentTracker;
END
GO
USE StudentTracker;
GO

/* ===== 2) Schemas (optional) ===== */
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'st')
    EXEC('CREATE SCHEMA st');
GO

/* ===== 3) Tables ===== */

/* Users: Admins/Instructors/IT */
IF OBJECT_ID('st.Users') IS NOT NULL DROP TABLE st.Users;
GO
CREATE TABLE st.Users
(
    UserId           INT IDENTITY(1,1) PRIMARY KEY,
    FirstName        NVARCHAR(100)   NOT NULL,
    LastName         NVARCHAR(100)   NOT NULL,
    Email            NVARCHAR(256)   NOT NULL UNIQUE,
    Role             VARCHAR(20)     NOT NULL
        CONSTRAINT CK_Users_Role CHECK (Role IN ('ADMIN','INSTRUCTOR','IT')),
    CreatedAtUtc     DATETIME2(3)    NOT NULL DEFAULT SYSUTCDATETIME(),
    IsActive         BIT             NOT NULL DEFAULT 1
);
GO

/* Students (no parents in scope) */
IF OBJECT_ID('st.Students') IS NOT NULL DROP TABLE st.Students;
GO
CREATE TABLE st.Students
(
    StudentId        INT IDENTITY(1,1) PRIMARY KEY,
    UniversityId     NVARCHAR(20)     NOT NULL UNIQUE,
    FirstName        NVARCHAR(100)    NOT NULL,
    LastName         NVARCHAR(100)    NOT NULL,
    Email            NVARCHAR(256)    NOT NULL UNIQUE,
    PhoneE164        NVARCHAR(20)     NULL,         -- e.g., +14255550123
    Program          NVARCHAR(120)    NULL,
    [Year]           NVARCHAR(20)     NULL,         -- Freshman/Sophomore/Junior/Senior/Grad
    Status           VARCHAR(20)      NOT NULL DEFAULT 'Active'
        CONSTRAINT CK_Students_Status CHECK (Status IN ('Active','Inactive','OnLeave')),
    CreatedAtUtc     DATETIME2(3)     NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

/* Internship/placement positions (for roster by job) */
IF OBJECT_ID('st.Positions') IS NOT NULL DROP TABLE st.Positions;
GO
CREATE TABLE st.Positions
(
    PositionId       INT IDENTITY(1,1) PRIMARY KEY,
    Title            NVARCHAR(120)    NOT NULL,
    Company          NVARCHAR(120)    NOT NULL,
    SiteLocation     NVARCHAR(120)    NULL,
    SupervisorName   NVARCHAR(120)    NULL,
    SupervisorEmail  NVARCHAR(256)    NULL,
    TermStart        DATE             NULL,
    TermEnd          DATE             NULL,
    CreatedAtUtc     DATETIME2(3)     NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

/* Cohorts (optional grouping by instructor/section/term) */
IF OBJECT_ID('st.Cohorts') IS NOT NULL DROP TABLE st.Cohorts;
GO
CREATE TABLE st.Cohorts
(
    CohortId         INT IDENTITY(1,1) PRIMARY KEY,
    CohortName       NVARCHAR(120)    NOT NULL,
    Term             NVARCHAR(40)     NOT NULL,  -- e.g., Spring 2025
    InstructorUserId INT              NOT NULL
        CONSTRAINT FK_Cohorts_Instructor
        REFERENCES st.Users(UserId),
    CreatedAtUtc     DATETIME2(3)     NOT NULL DEFAULT SYSUTCDATETIME()
);
GO

/* Link students to positions (and optionally a cohort) */
IF OBJECT_ID('st.StudentAssignments') IS NOT NULL DROP TABLE st.StudentAssignments;
GO
CREATE TABLE st.StudentAssignments
(
    AssignmentId     INT IDENTITY(1,1) PRIMARY KEY,
    StudentId        INT              NOT NULL
        CONSTRAINT FK_Assignments_Student
        REFERENCES st.Students(StudentId),
    PositionId       INT              NOT NULL
        CONSTRAINT FK_Assignments_Position
        REFERENCES st.Positions(PositionId),
    CohortId         INT              NULL
        CONSTRAINT FK_Assignments_Cohort
        REFERENCES st.Cohorts(CohortId),
    StartDate        DATE             NOT NULL,
    EndDate          DATE             NULL,
    CreatedAtUtc     DATETIME2(3)     NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT UQ_Assignments UNIQUE (StudentId, PositionId, StartDate)
);
GO
CREATE INDEX IX_Assignments_ByCohort ON st.StudentAssignments (CohortId);
CREATE INDEX IX_Assignments_ByPosition ON st.StudentAssignments (PositionId, StudentId);
GO

/* Daily attendance (core) */
IF OBJECT_ID('st.Attendance') IS NOT NULL DROP TABLE st.Attendance;
GO
CREATE TABLE st.Attendance
(
    AttendanceId     BIGINT IDENTITY(1,1) PRIMARY KEY,
    StudentId        INT              NOT NULL
        CONSTRAINT FK_Attendance_Student
        REFERENCES st.Students(StudentId),
    PositionId       INT              NOT NULL
        CONSTRAINT FK_Attendance_Position
        REFERENCES st.Positions(PositionId),
    AttendanceDate   DATE             NOT NULL,        -- e.g., 2025-02-03
    AttendanceTime   TIME(0)          NULL,            -- optional (check-in time)
    Status           VARCHAR(10)      NOT NULL
        CONSTRAINT CK_Attendance_Status CHECK (Status IN ('PRESENT','ABSENT','TARDY')),
    SetByUserId      INT              NOT NULL
        CONSTRAINT FK_Attendance_SetBy
        REFERENCES st.Users(UserId),
    Note             NVARCHAR(4000)   NULL,
    CreatedAtUtc     DATETIME2(3)     NOT NULL DEFAULT SYSUTCDATETIME(),
    /* one row per student/position/day */
    CONSTRAINT UQ_Attendance_StudentPosDay UNIQUE (StudentId, PositionId, AttendanceDate)
);
GO
CREATE INDEX IX_Attendance_StudentDate  ON st.Attendance (StudentId, AttendanceDate);
CREATE INDEX IX_Attendance_PositionDate ON st.Attendance (PositionId, AttendanceDate);
GO

/* ===== 4) Seed data (sample) ===== */

-- Users
INSERT INTO st.Users (FirstName, LastName, Email, Role)
VALUES
('Avery','Nguyen','avery.nguyen@univ.edu','ADMIN'),
('Jordan','Lee','jordan.lee@univ.edu','INSTRUCTOR'),
('Samira','Patel','samira.patel@univ.edu','INSTRUCTOR');

-- Students
INSERT INTO st.Students (UniversityId, FirstName, LastName, Email, PhoneE164, Program, [Year])
VALUES
('90012345','Lena','Chen','lena.chen@univ.edu','+14255550101','BS Computer Science','Junior'),
('90012346','Marco','Diaz','marco.diaz@univ.edu','+14255550102','BS Information Systems','Senior'),
('90012347','Nia','Owens','nia.owens@univ.edu','+14255550103','BS Data Science','Junior');

-- Positions
INSERT INTO st.Positions (Title, Company, SiteLocation, SupervisorName, SupervisorEmail, TermStart, TermEnd)
VALUES
('Software Intern','Acme Tech','Seattle WA','Kim Park','kim.park@acmetech.com','2025-01-13','2025-05-02'),
('Data Analyst Intern','North Analytics','Nashville TN','Chris Hall','chris.hall@northanalytics.com','2025-01-13','2025-05-02');

-- Cohorts
INSERT INTO st.Cohorts (CohortName, Term, InstructorUserId)
VALUES
('CS Internship Section A','Spring 2025', 2),   -- Jordan Lee
('CS Internship Section B','Spring 2025', 3);   -- Samira Patel

-- StudentAssignments
INSERT INTO st.StudentAssignments (StudentId, PositionId, CohortId, StartDate, EndDate)
VALUES
(1, 1, 1, '2025-01-13', '2025-05-02'),
(2, 1, 1, '2025-01-13', '2025-05-02'),
(3, 2, 1, '2025-01-13', '2025-05-02');

-- Attendance (example day)
INSERT INTO st.Attendance (StudentId, PositionId, AttendanceDate, AttendanceTime, Status, SetByUserId, Note)
VALUES
(1,1,'2025-02-03','09:00','PRESENT',2,NULL),
(2,1,'2025-02-03','09:00','ABSENT',2,'No show by 9am'),
(3,2,'2025-02-03','09:12','TARDY',2,'Arrived 09:12');
GO

/* ===== 5) Helper view: today's roster for a position ===== */
IF OBJECT_ID('st.v_TodaysRosterByPosition') IS NOT NULL DROP VIEW st.v_TodaysRosterByPosition;
GO
CREATE VIEW st.v_TodaysRosterByPosition
AS
SELECT
    p.PositionId,
    p.Title,
    s.StudentId,
    s.FirstName,
    s.LastName,
    a.AttendanceDate,
    a.Status,
    a.AttendanceTime
FROM st.Positions p
JOIN st.StudentAssignments sa ON sa.PositionId = p.PositionId
JOIN st.Students s           ON s.StudentId = sa.StudentId
LEFT JOIN st.Attendance a    ON a.StudentId = s.StudentId
                            AND a.PositionId = p.PositionId
                            AND a.AttendanceDate = CONVERT(date, SYSUTCDATETIME());
GO