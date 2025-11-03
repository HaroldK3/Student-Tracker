from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from Backend.models import Attendance, AttendanceOut, AttendanceCreate
from typing import List

router = APIRouter(prefix="/attendance", tags=["Attendance"])


# student check-in (timeclock)
@router.post("/checkin", response_model=AttendanceOut, status_code=201)
def check_in(data: AttendanceCreate, db: Session = Depends(get_db)):
    # verify student exists if your AttendanceCreate has StudentId
    attendance = Attendance(
        StudentId=data.StudentId,
        CheckInUtc=data.CheckInUtc or datetime.utcnow().isoformat(),
        CheckOutUtc=None,
        IsApproved=False
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


# student check-out
@router.put("/checkout/{attendance_id}", response_model=AttendanceOut)
def check_out(attendance_id: int, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.AttendanceId == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found.")

    attendance.CheckOutUtc = datetime.utcnow().isoformat()
    db.commit()
    db.refresh(attendance)
    return attendance


# get all attendance for a student
@router.get("/student/{student_id}", response_model=List[AttendanceOut])
def get_student_attendance(student_id: int, db: Session = Depends(get_db)):
    records = db.query(Attendance).filter(Attendance.StudentId == student_id).all()
    return records


# approve an attendance record (for teacher/admin)
@router.put("/approve/{attendance_id}", response_model=AttendanceOut)
def approve_attendance(attendance_id: int, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.AttendanceId == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found.")

    attendance.IsApproved = True
    db.commit()
    db.refresh(attendance)
    return attendance
