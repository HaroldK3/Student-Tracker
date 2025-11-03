from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
import models

router = APIRouter(
    prefix="/student",
    tags=["Student"]
)


@router.get("/", response_model=list[models.StudentOut])
def get_students(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()
    return students


@router.get("/profile/{student_id}", response_model=models.StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.post("/", response_model=models.StudentOut)
def create_student(student_in: models.StudentCreate, db: Session = Depends(get_db)):
    student = models.Student(**student_in.dict())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.put("/update-profile/{student_id}", response_model=models.StudentOut)
def update_student(student_id: int, student_in: models.StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    for k, v in student_in.dict(exclude_unset=True).items():
        setattr(student, k, v)
    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return {"detail": "Student deleted"}
