from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from Backend.models import Student

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
