from datetime import datetime, date, time
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from ..db import get_db                   
from Backend.models import User, UserOut, UserCreate, UserUpdate 
from Backend.models import StudentOut, StudentCreate, Student, Attendance, StudentLocationOut, StudentLocation       
from typing import List
from Backend.db import engine

router = APIRouter(prefix="/teacher", tags=["Teacher"])

## Get the students in a position


## Get a student
@router.get("/students", response_model=list[StudentOut])
def get_students(status: str = "Active", db: Session = Depends(get_db)):
    students = db.query(Student).filter(Student.Status.ilike(status)).all() ## Status can be called to allow filtering between
    return students 

## post feeback for a student
@router.post("/feedback/student/{student_id}")
def post_feedback_for_student(student_id: int, feedback: str, db: Session = Depends(get_db)):
    try:
        db.execute(
            text("""
                INSERT INTO Feedback (TargetType, TargetId, FeedbackText, CreatedAtUtc)
                VALUES ('STUDENT', :student_id, :feedback, :created)
            """),
            {"student_id": student_id, "feedback": feedback, "created": datetime.utcnow()}
        )
        db.commit()
        return {"message": f"Feedback for student {student_id} saved."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

## post feedback for a position
@router.post("/feedback/position/{position_id}")
def post_feedback_for_position(position_id: int, feedback: str, db: Session = Depends(get_db)):
    try:
        db.execute(
            text("""
                INSERT INTO Feedback (TargetType, TargetId, FeedbackText, CreatedAtUtc)
                VALUES ('POSITION', :position_id, :feedback, :created)
            """),
            {"position_id": position_id, "feedback": feedback, "created": datetime.utcnow()}
        )
        db.commit()
        return {"message": f"Feedback for position {position_id} saved."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

## get a time punch
@router.get("/time_punch/{student_id}")
def get_time_punch(student_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT * FROM TimePunches WHERE StudentId = :sid ORDER BY PunchTime DESC"),
        {"sid": student_id}
    ).fetchall()
    return {"punches": [dict(row._mapping) for row in result]}

## get a time clock
@router.get("/time_clock")
def get_time_clock(db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT * FROM TimePunches WHERE ClockOutTime IS NULL")
    ).fetchall()
    return {"active_punches": [dict(row._mapping) for row in result]}

## Get attendance sheet for specified time
@router.get("/attendance/{date}")
def get_attendance_sheet(date: str, db: Session = Depends(get_db)):
    # Use the Attendance model's CheckInUtc to filter by date
    try:
        qdate = datetime.fromisoformat(date).date()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format YYYY-MM-DD")

    start = datetime.combine(qdate, time.min)
    end = datetime.combine(qdate, time.max)

    rows = (
        db.query(Attendance)
        .filter(Attendance.CheckInUtc >= start, Attendance.CheckInUtc <= end)
        .all()
    )

    return {"attendance": [
        {
            "AttendanceId": r.AttendanceId,
            "StudentId": r.StudentId,
            "CheckInUtc": r.CheckInUtc,
            "CheckOutUtc": r.CheckOutUtc,
            "IsApproved": r.IsApproved,
            "Lat": r.Lat,
            "Lng": r.Lng,
        }
        for r in rows
    ]}

## post attendance sheet
@router.post("/attendance")
def post_attendance_sheet(data: dict, db: Session = Depends(get_db)):
    try:
        for record in data.get("students", []):
            att = Attendance(
                StudentId=record["StudentId"],
                Status=record.get("Status", "PRESENT"),
                CheckInUtc=datetime.fromisoformat(data.get("Date")) if data.get("Date") else datetime.utcnow(),
            )
            db.add(att)
        db.commit()
        return {"message": "Attendance sheet saved successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

## update an attendance sheet 
@router.put("/attendance/{attendance_id}")
def update_attendance(attendance_id: int, status: str, db: Session = Depends(get_db)):
    try:
        record = db.query(Attendance).filter(Attendance.AttendanceId == attendance_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Attendance record not found.")
        record.Status = status
        db.commit()
        return {"message": f"Attendance record {attendance_id} updated."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

## get a check in
@router.get("/check_in/{student_id}")
def get_check_in(student_id: int, db: Session = Depends(get_db)):
    # Return attendance records for the student (most recent first)
    rows = (
        db.query(Attendance)
        .filter(Attendance.StudentId == student_id)
        .order_by(Attendance.CheckInUtc.desc())
        .all()
    )
    return {"checkins": [
        {
            "CheckInId": r.AttendanceId,
            "StudentId": r.StudentId,
            "CheckInTime": r.CheckInUtc,
            "Approved": r.IsApproved,
        }
        for r in rows
    ]}

## approve a check in
@router.put("/check_in/{checkin_id}/approve")
def approve_check_in(checkin_id: int, db: Session = Depends(get_db)):
    try:
        record = db.query(Attendance).filter(Attendance.AttendanceId == checkin_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Check-in not found.")
        record.IsApproved = True
        db.commit()
        return {"message": f"Check-in {checkin_id} approved."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

## upload a resource
@router.post("/upload_resource")
def upload_resource(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        file_location = f"uploads/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        db.execute(
            text("""
                INSERT INTO Resources (FileName, FilePath, UploadedAtUtc)
                VALUES (:name, :path, :uploaded)
            """),
            {"name": file.filename, "path": file_location, "uploaded": datetime.utcnow()}
        )
        db.commit()
        return {"message": f"Resource '{file.filename}' uploaded successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    ## get locations of students
@router.get("/locations/today", response_model=list[StudentLocationOut])
def get_today_locations(db: Session = Depends(get_db)):
    """
    Returns latest attendance entries with location for today,
    joined with student names, for the map view.
    """
    today: date = datetime.utcnow().date()
    start_of_day = datetime.combine(today, time.min)
    end_of_day = datetime.combine(today, time.max)

    # Check the actual Attendance table schema — older DBs may not have Lat/Lng/StudentId
    try:
        with engine.connect() as conn:
            res = conn.execute("PRAGMA table_info('Attendance')")
            cols = [row[1] for row in res.fetchall()]
    except Exception:
        cols = []

    required = {"StudentId", "Lat", "Lng", "CreatedAtUtc"}
    if not required.issubset(set(cols)):
        # Attendance table lacks location columns — try StudentLocations table instead
        try:
            rows = (
                db.query(
                    StudentLocation.StudentId,
                    Student.FirstName,
                    Student.LastName,
                    StudentLocation.Lat,
                    StudentLocation.Lng,
                    StudentLocation.CheckInUtc.label("CheckInTime"),
                )
                .join(Student, Student.StudentId == StudentLocation.StudentId)
                .filter(
                    StudentLocation.CheckInUtc >= start_of_day,
                    StudentLocation.CheckInUtc <= end_of_day,
                )
                .all()
            )
        except Exception:
            return []
    else:
        # Proceed with the normal query when columns exist
        try:
            rows = (
                db.query(
                    Attendance.StudentId,
                    Student.FirstName,
                    Student.LastName,
                    Attendance.Lat,
                    Attendance.Lng,
                    Attendance.CreatedAtUtc.label("CheckInTime"),
                )
                .join(Student, Student.StudentId == Attendance.StudentId)
                .filter(
                    Attendance.CreatedAtUtc >= start_of_day,
                    Attendance.CreatedAtUtc <= end_of_day,
                    Attendance.Lat.isnot(None),
                    Attendance.Lng.isnot(None),
                )
                .all()
            )
        except OperationalError:
            # Defensive: if query fails, return empty list
            return []

    # Proceed with the normal query when columns exist
    try:
        rows = (
            db.query(
                Attendance.StudentId,
                Student.FirstName,
                Student.LastName,
                Attendance.Lat,
                Attendance.Lng,
                Attendance.CreatedAtUtc.label("CheckInTime"),
            )
            .join(Student, Student.StudentId == Attendance.StudentId)
            .filter(
                Attendance.CreatedAtUtc >= start_of_day,
                Attendance.CreatedAtUtc <= end_of_day,
                Attendance.Lat.isnot(None),
                Attendance.Lng.isnot(None),
            )
            .all()
        )
    except OperationalError:
        # Defensive: if the Attendance table/schema doesn't match the model
        # (e.g. missing StudentId/Lat/Lng columns), return empty list
        return []

    # Convert to pydantic-friendly objects
    locations: list[StudentLocationOut] = []
    for r in rows:
        locations.append(
            StudentLocationOut(
                StudentId=r.StudentId,
                FirstName=r.FirstName,
                LastName=r.LastName,
                Lat=r.Lat,
                Lng=r.Lng,
                CheckInTime=r.CheckInTime,
            )
        )
    return locations