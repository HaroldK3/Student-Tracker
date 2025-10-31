from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db                   
from Backend.models import User, UserOut, UserCreate, UserUpdate         
from typing import List


## Get the students in a position

## Get a student

## post feeback for a student

## post feedback for a position

## get a time punch

## get a time clock

## Get attendance sheet for specified time

## post attendance sheet

## update an attendance sheet 

## get a check in

## approve a check in

## upload a resource