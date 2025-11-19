from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..db import get_db                   
from Backend.models import User, UserOut, UserCreate, UserUpdate
from Backend.models import Student, StudentOut, StudentCreate, StudentUpdate
from Backend.models import AssignmentCreate, StudentAssignment, Positions
from typing import List

## HTTP status codes
## https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
router = APIRouter(prefix="/admin", tags=["Admin"])

## Possible things to add: Getting Attendance, Student Records, 


## Users display (multiple)
@router.get("/users", response_model=List[UserOut])
def get_users(status: bool = True, db: Session = Depends(get_db)):
    # status is a boolean filter for active users (default True)
    users = db.query(User).filter(User.IsActive == status).all()
    return users                                                 ## Active and inactive
    
## User display (one)
@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.UserId == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")
    return user

## Create_User
@router.post("/users/create_user", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.Email == user.Email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already in use.")

    new_user = User(
        FirstName=user.FirstName,
        LastName=user.LastName,
        Email=user.Email,
        Role=user.Role.upper(),
        CreatedAtUtc=datetime.now(timezone.utc).isoformat(),
        IsActive=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

## Updating a user
@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, update_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.UserId == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    update_dict = update_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user

## Deleting a user
@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.UserId == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    ## Soft deletes
    user.IsActive = False

    db.commit()
    return


## /students                → Active students only (default)
## /students?status=all     → All students
## /students?status=Inactive → Only inactive students
## Get Students (multiple)
@router.get("/students", response_model=list[StudentOut])
def get_students(status: str = "Active", db: Session = Depends(get_db)):
    students = db.query(Student).filter(Student.Status.ilike(status)).all() ## Status can be called to allow filtering between
    return students                                                         ## Active, Inactive, and OnLeave

## Get a student (one)
@router.get("/student/{student_id}", response_model=StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.StudentId == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student Not Found.")
    return student

## Create a student
@router.post("/students", response_model=StudentOut, status_code=201)
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    student = Student(
        UniversityId = data.UniversityId,
        FirstName = data.FirstName,
        LastName = data.LastName,
        Email = data.Email,
        PhoneE164 = data.PhoneE164,
        Program = data.Program,
        Year = data.Year,
        GPA = data.GPA,
        Status = "Active"
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return student

## Update a student
@router.put("/students/{student_id}", response_model=StudentOut)
def update_student(student_id: int, data: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.StudentId == student_id).first()

    update_dict = data.model_dump(exclude_unset=True)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    
    for key, value in update_dict.items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)
    return student

## Delete a student
@router.delete("/student/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.StudentId == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
    
    # soft-delete the specific student record
    student.Status = "Gone"

    db.commit()
    return

## Get all dashboard metrics
## Recent Students can be added in the frontend
## Add an attendance average to the students? 
@router.get("/dashboard/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db)):
    today = datetime.utcnow()
    total_students = db.query(Student).count()
    total_assignments = db.query(StudentAssignment).count()

    ## Active term functionality
    ##active_term = db.query(Cohort).filter(
    ##  Cohort.StartDate <= today,
    ##  Cohort.EndDate >= today
    ##).count

    avg_gpa = db.query(func.avg(Student.GPA)).scalar()
    avg_gpa = round(avg_gpa, 2) if avg_gpa is not None else 0.0

    return{
        "total_students": total_students,
        "total_assignments": total_assignments,
        "average_gpa": avg_gpa
    }

## Get Admin logs

## Assign a teacher to a student
@router.post("/assign", status_code=201)
def assign_teacher(data: AssignmentCreate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.StudentId == data.StudentId).first()
    # AssignmentCreate provides UserId as the instructor's user id
    instructor = db.query(User).filter(
        User.UserId == data.UserId,
        User.Role == "INSTRUCTOR"
        ).first()

    if not student: 
        raise HTTPException(status_code=404, detail="Student not found.")
    if not instructor:
        raise HTTPException(status_code=404, detail="Instrustor not found.")

    assignment = StudentAssignment(
        StudentId = data.StudentId,
        UserId = data.UserId,
        IsActive = True
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment

