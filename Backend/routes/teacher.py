from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..db import get_db                   
from Backend.models import User, UserOut, UserCreate, UserUpdate 
from Backend.models import StudentOut, StudentCreate, Student        
from typing import List

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
    result = db.execute(
        text("""
            SELECT * FROM Attendance 
            WHERE DATE(AttendanceDate) = DATE(:date)
        """),
        {"date": date}
    ).fetchall()
    return {"attendance": [dict(row._mapping) for row in result]}

## post attendance sheet
@router.post("/attendance")
def post_attendance_sheet(data: dict, db: Session = Depends(get_db)):
    try:
        for record in data.get("students", []):
            db.execute(
                text("""
                    INSERT INTO Attendance (StudentId, Status, AttendanceDate)
                    VALUES (:sid, :status, :date)
                """),
                {"sid": record["StudentId"], "status": record["Status"], "date": data["Date"]}
            )
        db.commit()
        return {"message": "Attendance sheet saved successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

## update an attendance sheet 
@router.put("/attendance/{attendance_id}")
def update_attendance(attendance_id: int, status: str, db: Session = Depends(get_db)):
    try:
        db.execute(
            text("""
                UPDATE Attendance SET Status = :status
                WHERE AttendanceId = :aid
            """),
            {"aid": attendance_id, "status": status}
        )
        db.commit()
        return {"message": f"Attendance record {attendance_id} updated."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

## get a check in
@router.get("/check_in/{student_id}")
def get_check_in(student_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT * FROM CheckIns WHERE StudentId = :sid ORDER BY CheckInTime DESC"),
        {"sid": student_id}
    ).fetchall()
    return {"checkins": [dict(row._mapping) for row in result]}

## approve a check in
@router.put("/check_in/{checkin_id}/approve")
def approve_check_in(checkin_id: int, db: Session = Depends(get_db)):
    try:
        db.execute(
            text("""
                UPDATE CheckIns SET Approved = 1
                WHERE CheckInId = :cid
            """),
            {"cid": checkin_id}
        )
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