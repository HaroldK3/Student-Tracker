from sqlalchemy import Column, Integer, String, Boolean, DateTime
from Backend.db import Base
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

## Users
class User(Base):
    __tablename__ = "Users"

    UserId = Column(Integer, primary_key=True, autoincrement=True)
    FirstName = Column(String, nullable=False)
    LastName = Column(String, nullable=False)
    Email = Column(String, unique=True, nullable=False)
    Role = Column(String, nullable=False)
    CreatedAtUtc = Column(String, nullable=False)
    IsActive = Column(Boolean, default=True)

class UserBase(BaseModel):
    FirstName: str
    LastName: str
    Email: str
    Role: str
    IsActive: bool = True

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    UserId: int
    CreatedAtUtc: str

    class Config:
        orm_mode = True

## Students
class Student(Base):
    __tablename__ = "Students"
    StudentId = Column(Integer, primary_key=True, index=True)
    UniversityId = Column(String(20), unique=True, nullable=False)
    FirstName = Column(String(100), nullable=False)
    LastName = Column(String(100), nullable=False)
    Email = Column(String(256), unique=True, nullable=False)
    PhoneE164 = Column(String(20), nullable=True)
    Program = Column(String(120), nullable=True)
    Year = Column(String(20), nullable=True)
    Status = Column(String(20), nullable=False, default="Active")
    CreatedAtUtc = Column(DateTime, default=datetime.utcnow)

class StudentOut(BaseModel):
    UniversityId: int
    FirstName: str
    LastName: str
    Email: str
    PhoneE164: Optional[str] = None
    Program: str
    Year: str
    Status: str = "IsActive"
    
##class StudentAssignments(Base):

##class Cohorts(Base):


## Other
##class Positions(Base):

##class Attendance(Base):





