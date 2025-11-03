from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..db import get_db
from Backend.models import Student

from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from Backend.db import Base

# Temporary in-file table until Attendance is formally added
class Attendance(Base):
    __tablename__ = "Attendance"

    AttendanceId = Column(Integer, primary_key=True, index=True)
    StudentId = Column(Integer, ForeignKey("Students.StudentId"))
    CheckInUtc = Column(DateTime, default=datetime.utcnow)
    CheckOutUtc = Column(DateTime, nullable=True)
    IsApproved = Column(Boolean, default=False)

    student = relationship("Student", backref="AttendanceRecords")


router = APIRouter(prefix="/attendance", tags=["Attendance"])


# =============================
# STUDENT CHECK-IN
# =============================
@router.post("/checkin", status_code=201)
def check_in(data: dict, db: Session = Depends(get_db)):
    student_id = data.get("StudentId")
    student = db.query(Student).filter(Student.StudentId == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    attendance = Attendance(StudentId=student_id, CheckInUtc=datetime.utcnow())
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return {"detail": f"Student ID {student_id} checked in successfully."}


# =============================
# STUDENT CHECK-OUT
# =============================
@router.put("/checkout/{attendance_id}")
def check_out(attendance_id: int, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.AttendanceId == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found.")

    attendance.CheckOutUtc = datetime.utcnow()
    db.commit()
    db.refresh(attendance)
    return {"detail": f"Attendance ID {attendance_id} checked out successfully."}


# =============================
# GET ATTENDANCE BY STUDENT
# =============================
@router.get("/student/{student_id}")
def get_student_attendance(student_id: int, db: Session = Depends(get_db)):
    records = db.query(Attendance).filter(Attendance.StudentId == student_id).all()
    if not records:
        raise HTTPException(status_code=404, detail="No attendance records found for this student.")
    return [
        {
            "AttendanceId": r.AttendanceId,
            "StudentId": r.StudentId,
            "CheckInUtc": r.CheckInUtc,
            "CheckOutUtc": r.CheckOutUtc,
            "IsApproved": r.IsApproved,
        }
        for r in records
    ]


# =============================
# APPROVE ATTENDANCE RECORD
# =============================
@router.put("/approve/{attendance_id}")
def approve_attendance(attendance_id: int, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.AttendanceId == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found.")
    attendance.IsApproved = True
    db.commit()
    db.refresh(attendance)
    return {"detail": f"Attendance ID {attendance_id} approved successfully."}
