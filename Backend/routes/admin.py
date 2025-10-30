from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db                   
from Backend.models import User, UserOut, UserCreate, UserUpdate         
from typing import List

## HTTP status codes
## https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
router = APIRouter(prefix="/admin", tags=["Admin"])


## Users display (multiple)
@router.get("/users", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
    
## User display (one)
@router.get("/users/{user_id)}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.UserId == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")
    return user

## Get Students (multiple)

## Get a student (one)

## Create_User
@router.post("/users/create_user", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.Email == user.Email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already in use.")

    new_user = User(**user.model_dump(), CreatedAtUtc=datetime.utcnow().isoformat())
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
@router.delete("/users/delete_user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.UserId == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    db.delete(user)
    db.commit()

    return


## Get all dashboard metrics

## Get Admin logs

## Assign a teacher to a student


