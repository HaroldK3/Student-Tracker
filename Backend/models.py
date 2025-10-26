from datetime import date
import time
from sqlalchemy import Column, Integer, String, Boolean
from Backend.db import Base
from pydantic import BaseModel

class User(Base):
    __tablename__ = "Users"
    UserId = Column(Integer, primary_key=True, autoincrement=True)
    FirstName = Column(String, nullable=False)
    LastName = Column(String, nullable=False)
    Email = Column(String, unique=True, nullable=False)
    Role = Column(String, nullable=False)
    CreatedAtUtc = Column(String, nullable=False)
    IsActive = Column(Boolean, default=True)


class UserOut(BaseModel):
    UserId: int
    FirstName: str
    LastName: str
    Email: str
    Role: str
    CreatedAtUtc: str
    IsActive: bool


##class Student(Base):


##class Positions(Base):


##class Cohorts(Base):


##class StudentAssignments(Base):


##class Attendance(Base):





