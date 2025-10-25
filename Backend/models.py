from datetime import date
import time
from fastapi import Body, FastAPI, Depends, Request, Response, status, Query, Path, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional
import sqlite3

class User(BaseModel):
    UserId: int
    FirstName: str
    LastName: str
    Email: str
    Role: str
    CreatedAtUTC: time
    IsActive: bool

class Student(BaseModel):
    StudentId: int
    UniversityId: int
    FirstName: str
    LastName: str
    Email: str
    PhoneE164: str
    Program: str
    Year: str
    Status: str
    CreatedAtUTC: time

class Positions(BaseModel):
    PositionId: int
    Title: str
    Company: str
    SiteLocation: str
    SupervisorName: str
    SupervisorEmail: str

class Cohorts(BaseModel):
    CohortId: int
    CohortName: str
    Term: str
    InstructorUserId: int
    CreatedAtUTC: time

class StudentAssignments(BaseModel):
    AssignmentId: int
    StudentId: int
    PositionId: int
    CohortId: int
    StartDate: str
    EndDate: str
    CreatedAtUTC: time

class Attendance(BaseModel):
    AttendanceId: int
    AssignmentId: int
    AttendanceDate: str
    AttendanceTime: str
    Status: str
    SetByUserId: int
    Note: str
    CreatedAtUTC: time

