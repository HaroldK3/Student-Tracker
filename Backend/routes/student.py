from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from Backend.models import Student, StudentOut, StudentUpdate

router = APIRouter(prefix="/student", tags=["Student"])


# Get a student's own profile
@router.get("/profile/{student_id}", response_model=StudentOut)
def get_profile(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.StudentId == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    return student


# Update a student's own profile
@router.put("/profile/{student_id}", response_model=StudentOut)
def update_profile(student_id: int, data: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.StudentId == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)
    return student


# (Optional placeholders based on your sketch)
@router.get("/feedback/{student_id}")
def get_feedback(student_id: int):
    # frontend can fill this later
    return {"detail": "feedback endpoint placeholder", "student_id": student_id}


@router.get("/internship/{student_id}")
def get_internship(student_id: int):
    # frontend can fill this later
    return {"detail": "internship endpoint placeholder", "student_id": student_id}
