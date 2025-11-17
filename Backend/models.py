from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from Backend.db import Base
from pydantic import BaseModel, field_validator, constr
from typing import Optional
from datetime import datetime

VALID_ROLES = {"ADMIN", "INSTRUCTOR", "IT"}

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

    @field_validator("Role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        value = value.upper()
        if value not in VALID_ROLES:
            raise ValueError(f"Role must be one of {VALID_ROLES}")
        return value

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    Email: Optional[str] = None
    Role: Optional[str] = None 
    IsActive: Optional[bool] = None

    @field_validator("Role")
    @classmethod


    def validate_role_update(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        value = value.upper()
        if value not in VALID_ROLES:
            raise ValueError(f"Role must be one of: {VALID_ROLES}")
        return value

class UserOut(UserBase):
    UserId: int
    CreatedAtUtc: str

    class Config:
        from_attributes = True

## Students
class Student(Base):
    __tablename__ = "Students"
    StudentId = Column(Integer, primary_key=True, index=True)
    UniversityId = Column(Integer, unique=True, nullable=False)
    FirstName = Column(String(100), nullable=False)
    LastName = Column(String(100), nullable=False)
    Email = Column(String(256), unique=True, nullable=False)
    PhoneE164 = Column(String(20), nullable=True)
    Program = Column(String(120), nullable=True)
    Year = Column(String(20), nullable=True)
    Status = Column(String(20), nullable=False, default="Active")
    GPA = Column(Float, nullable = True)
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
    GPA: Optional[float] = None

    class Config:
        omr_mode = True

class StudentCreate(BaseModel):
    UniversityId: int
    FirstName: str
    LastName: str
    Email: str
    PhoneE164: Optional[str] = None
    Program: str
    Year: str
    Status: str = "IsActive"
    GPA: Optional[float] = None
    
class StudentUpdate(BaseModel):
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    Email: Optional[str] = None
    PhoneE164: Optional[str] = None
    Program: Optional[str] = None
    Year: Optional[str] = None
    Status: Optional[str] = None
    GPA: Optional[float] = None


##class StudentAssignments(Base):
class StudentAssignment(Base):
    __tablename__ = "StudentAssignments"

    AssignmentId = Column(Integer, primary_key=True, index=True)
    StudentId = Column(Integer, ForeignKey("Students.StudentId"), nullable=False)
    UserId = Column(Integer, ForeignKey("Users.UserId"), nullable=False)
    IsActive = Column(Boolean, default=True)

    Student = relationship("Student", backref="Assignments")
    Instructor = relationship("User", backref="AssignedStudents")

class AssignmentCreate(BaseModel):
    StudentId: int
    UserId: int
    PositionId: int
    CohortId: Optional[int] = None


## Other
class Positions(Base):
    __tablename__ = "Positions"

    PositionId = Column(Integer, primary_key=True, index=True)
    Title = Column(String, nullable=False)    
    Company = Column(String, nullable=False)          
    SiteLocation = Column(String, nullable=False)         
    SupervisorName = Column(String, nullable=False)      
    SupervisorEmail = Column(String, nullable=False)     
    TermStart = Column(DateTime, nullable=False)      
    TermEnd = Column(DateTime, nullable=False)        
    CreatedAtUtc = Column(DateTime, nullable=False, default=datetime.utcnow)


class PositionCreate(BaseModel):
    Title: str
    Company: str
    SiteLocation: str
    SupervisorName: str
    SupervisorEmail: str
    TermStart: Optional[datetime] = None
    TermEnd: Optional[datetime] = None

class PositionUpdate(BaseModel):
    Title: Optional[str] = None
    Company: Optional[str] = None
    SiteLocation: Optional[str] = None
    SupervisorName: Optional[str] = None
    SupervisorEmail: Optional[str] = None
    TermStart: Optional[datetime] = None
    TermEnd: Optional[datetime] = None




