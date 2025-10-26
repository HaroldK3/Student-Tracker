from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db                   
from Backend.models import User, UserOut             
from pydantic import BaseModel
from typing import List


router = APIRouter(prefix="/admin", tags=["Admin"])


## Users display
@router.get("/users", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
    
## User display
@router.get("/users/{user_id)}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.UserId == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")
    return user

## Create_User
    
## Updating a user

## Deleting a user

## Get all dashboard metrics

## Get Admin logs

## Assign a teacher to a student


