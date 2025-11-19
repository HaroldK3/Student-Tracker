from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..db import get_db
from Backend.models import Student, Attendance, AttendanceCreate, StudentLocation, StudentLocationCreate

router = APIRouter(prefix="/student", tags=["Student"])


# ---------------------------------------------------------
# GET ONE STUDENT (PROFILE)
# ---------------------------------------------------------
@router.get("/profile/{student_id}", response_model=dict)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.StudentId == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    return {
        "StudentId": student.StudentId,
        "UniversityId": student.UniversityId,
        "FirstName": student.FirstName,
        "LastName": student.LastName,
        "Email": student.Email,
        "PhoneE164": student.PhoneE164,
        "Program": student.Program,
        "Year": student.Year,
        "Status": student.Status,
        "GPA": student.GPA,
        "CreatedAtUtc": student.CreatedAtUtc,
    }


# ---------------------------------------------------------
# UPDATE STUDENT (PROFILE)
# ---------------------------------------------------------
@router.put("/profile/{student_id}")
def update_student(student_id: int, payload: dict, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.StudentId == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    for key, value in payload.items():
        # only update fields that actually exist on the model
        if hasattr(student, key) and value is not None:
            setattr(student, key, value)

    db.commit()
    db.refresh(student)
    return {"detail": f"Student {student_id} updated."}

# ---------------------------------------------------------
# Checkin/location
# ---------------------------------------------------------
@router.post("/checkin/location", status_code=201)
def check_in_with_location(payload: AttendanceCreate, db: Session = Depends(get_db)):
    """
    Student sends StudentId + Lat + Lng (and optional Status).
    Creates an Attendance row with GPS coordinates.
    """
    student = (
        db.query(Student)
        .filter(Student.StudentId == payload.StudentId)
        .first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    status_value = payload.Status if payload.Status else "PRESENT"
    
    attendance = Attendance(
        StudentId=payload.StudentId,
        Status=status_value,
        Lat=payload.Lat,
        Lng=payload.Lng,
        CreatedAtUtc=datetime.utcnow(),
    )

    # Also insert into StudentLocations table for teacher map/locations
    location = StudentLocation(
        StudentId=payload.StudentId,
        Lat=payload.Lat if payload.Lat is not None else 0.0,
        Lng=payload.Lng if payload.Lng is not None else 0.0,
        CheckInUtc=datetime.utcnow(),
        CreatedAtUtc=datetime.utcnow(),
    )

    try:
        db.add(attendance)
        db.add(location)
        db.commit()
        db.refresh(attendance)
        db.refresh(location)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"attendance_id": attendance.AttendanceId, "location_id": location.StudentLocationId}