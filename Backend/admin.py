from fastapi import Body, FastAPI, Depends, Request, Response, status, Query, Path, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional
import sqlite3
from models import User, Student, Positions, Cohorts, StudentAssignments, Attendance

app = FastAPI()

def getDBConnection():
    connection = sqlite3.connect('social_media.db')
    connection.row_factory = sqlite3.Row
    return connection

## Root call
@app.get("/")
async def read_root():
    return{"status": "ok"}

## Create_User
@app.post("/admin/create_user")
async def create_user(user: User):
    conn = getDBConnection()
    try:
        cur = conn.execute(
            "INSERT INTO Users (FirstName, LastName, Email, Role, CreatedAtUTC, IsActive)",
            (user.FirstName, user.LastName, user.Email, user.Role, user.CreatedAtUTC, 1 if user.IsActive else 0,),
        )

        conn.commit()
        return str(cur.lastrowid)
    
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="User already exists.")
    
    finally:
        conn.close()




