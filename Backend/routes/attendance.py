from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, relationship
from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey
from ..db import get_db, Base
from Backend.models import Student

# router setup
router = APIRouter(prefix="/attendance", tags=["Attendance"])

# -----------------------------------------------------------------------------
# Local Attendance model (since it's not in Backend/models.py right now)
# -----------------------------------------------------------------------------
class Attendance(Base):
    __tablename__ = "Attendance"

    AttendanceId = Column(Integer, primary_key=True, index=True)
    StudentId = Column(Integer, ForeignKey("Students.StudentId"), nullable=False)
    CheckInUtc = Column(DateTime, default=datetime.utcnow)
    CheckOutUtc = Column(DateTime, nullable=True)
    IsApproved = Column(Boolean, default=False)

    student = relationship("Student")


# -----------------------------------------------------------------------------
# ENDPOINTS
# -----------------------------------------------------------------------------


@router.post("/checkin")
def check_in(payload: dict, db: Session = Depends(get_db)):
    """
    Create/check in an attendance record for a student.
    Expects: { "StudentId": 1 }
    """
    student_id = payload.get("StudentId")
    if not student_id:
        raise HTTPException(status_code=400, detail="StudentId is required.")

    # make sure student exists
    student = db.query(Student).filter(Student.StudentId == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    record = Attendance(
        StudentId=student_id,
        CheckInUtc=datetime.utcnow(),
        CheckOutUtc=None,
        IsApproved=False,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "AttendanceId": record.AttendanceId,
        "StudentId": record.StudentId,
        "CheckInUtc": record.CheckInUtc,
        "CheckOutUtc": record.CheckOutUtc,
        "IsApproved": record.IsApproved,
    }


@router.put("/checkout/{attendance_id}")
def check_out(attendance_id: int, db: Session = Depends(get_db)):
    """
    Sets the checkout time for an existing attendance record.
    """
    record = db.query(Attendance).filter(Attendance.AttendanceId == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found.")

    record.CheckOutUtc = datetime.utcnow()
    db.commit()
    db.refresh(record)

    return {
        "AttendanceId": record.AttendanceId,
        "StudentId": record.StudentId,
        "CheckInUtc": record.CheckInUtc,
        "CheckOutUtc": record.CheckOutUtc,
        "IsApproved": record.IsApproved,
    }


@router.put("/approve/{attendance_id}")
def approve(attendance_id: int, db: Session = Depends(get_db)):
    """
    Admin/teacher approval of an attendance record.
    """
    record = db.query(Attendance).filter(Attendance.AttendanceId == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found.")

    record.IsApproved = True
    db.commit()
    db.refresh(record)

    return {
        "AttendanceId": record.AttendanceId,
        "StudentId": record.StudentId,
        "CheckInUtc": record.CheckInUtc,
        "CheckOutUtc": record.CheckOutUtc,
        "IsApproved": record.IsApproved,
    }


@router.get("/student/{student_id}")
def get_student_attendance(student_id: int, db: Session = Depends(get_db)):
    """
    Get all attendance records for a given student.
    """
    records = db.query(Attendance).filter(Attendance.StudentId == student_id).all()
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
