from json import JSONDecodeError
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
    

## User display
@app.get("/users")
@app.get("/users/")
async def get_users(name: Optional(str) = Query(None)):
    conn = getDBConnection()
    try:
        has_filter = bool(name) and str(name).strip().lower() != "null"

        if has_filter:
            users = conn.execute(
                "SELECT UserId, FirstName, LastName, Email," \
                " Role, CreatedAtUtc, IsActive FROM Users WHERE FirstName = ?" \
                " COLLATE NOCASE",
                (name.strip(),),
            ).fetchall()
        
        else:
            users = conn.execute(
                "SELECT UserId, FirstName, LastName, Email, Role, CreatedAtUtc, IsActive FROM Users ORDER BY id DESC"
            ).fetchall()

        return [{"id": user["UserId"], "FirstName": user["FirstName"], "LastName": user["LastName"], "Email": user["Email"], 
                 "Role": user["Role"], "CreatedAtUtc": user["CreatedAtUtc"], "IsActive": bool(user["IsActive"])} for user in users]
    
    finally:
        conn.close()

## Updating a user
@app.put("/users/{UserId}", response_class=PlainTextResponse)
async def update_user(UserId: int, request: Request):
    try:
        payload = await request.json()
        if not isinstance(payload, dict):
            payload = {}
    except JSONDecodeError:
        payload = {}


    conn = getDBConnection()
    try:
        row = conn.execute(
            "SELECT UserId, FirstName, LastName, Email, Role, CreatedAtUtc, IsActive FROM Users WHERE id = ?",
            (UserId,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        
        new_first_name = payload.get("FirstName")
        new_last_name = payload.get("LastName")
        new_email = payload.get("Email")
        new_role = payload.get("Role")
        new_is_active = payload.get("IsActive")

        first_name  = new_first_name  if new_first_name  is not None else row["FirstName"]
        last_name = new_last_name  if new_last_name  is not None else row["LastName"]
        email = new_email  if new_email  is not None else row["Email"]
        role = new_role  if new_role is not None else row["Role"]
        is_active = row["is_admin"] if new_is_active is None else (1 if bool(new_is_active) else 0)

        try:
            conn.execute(
                "UPDATE users SET FirstName = ?, LastName = ?, Email = ?, Role = ?, IsActive = ? WHERE UserId = ?",
                (first_name, last_name, email, role, is_active, UserId),
            )
            conn.commit()

        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="Username already exists.")
        
        return str(UserId)

    finally:
        conn.close()


