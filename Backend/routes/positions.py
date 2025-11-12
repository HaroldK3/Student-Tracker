from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from Backend.db import get_db
from Backend.models import Positions

router = APIRouter(prefix="/positions", tags=["Positions"])


# ---------------------------------------------------------
# GET ALL POSITIONS
# ---------------------------------------------------------
@router.get("/", response_model=List[dict])
def get_positions(db: Session = Depends(get_db)):
    rows = db.query(Positions).all()
    return [
        {
        "PositionId": r.PositionId,
        "Title": r.Title,
        "Company": r.Company,
        "SiteLocation": r.SiteLocation,
        "SupervisorName": r.SupervisorName,
        "SupervisorEmail": r.SupervisorEmail,
        "TermStart": r.TermStart,
        "TermEnd": r.TermEnd,
        "CreatedAtUtc": r.CreatedAtUtc
        }
        for r in rows
    ]


# ---------------------------------------------------------
# GET ONE POSITION
# ---------------------------------------------------------
@router.get("/{position_id}", response_model=dict)
def get_position(position_id: int, db: Session = Depends(get_db)):
    pos = db.query(Positions).filter(Positions.PositionId == position_id).first()
    if not pos:
        raise HTTPException(status_code=404, detail="Position not found.")
    return {
        "PositionId": pos.PositionId,
        "PositionTitle": pos.PositionTitle,
        "Company": pos.Company,
        "Location": pos.Location,
        "ContactName": pos.ContactName,
        "ContactEmail": pos.ContactEmail,
        "StartDate": pos.StartDate,
        "EndDate": pos.EndDate,
        "CreatedAtUtc": pos.CreatedAtUtc,
    }


# ---------------------------------------------------------
# CREATE POSITION
# ---------------------------------------------------------
@router.post("/", status_code=201)
def create_position(payload: dict, db: Session = Depends(get_db)):
    pos = Positions(
        PositionTitle=payload.get("PositionTitle"),
        Company=payload.get("Company"),
        Location=payload.get("Location"),
        ContactName=payload.get("ContactName"),
        ContactEmail=payload.get("ContactEmail"),
        StartDate=payload.get("StartDate"),
        EndDate=payload.get("EndDate"),
        CreatedAtUtc=datetime.utcnow(),
    )
    db.add(pos)
    db.commit()
    db.refresh(pos)
    return {"detail": f"Position '{pos.PositionTitle}' created.", "PositionId": pos.PositionId}


# ---------------------------------------------------------
# UPDATE POSITION
# ---------------------------------------------------------
@router.put("/{position_id}")
def update_position(position_id: int, payload: dict, db: Session = Depends(get_db)):
    pos = db.query(Positions).filter(Positions.PositionId == position_id).first()
    if not pos:
        raise HTTPException(status_code=404, detail="Position not found.")

    for key, value in payload.items():
        if hasattr(pos, key) and value is not None:
            setattr(pos, key, value)

    db.commit()
    db.refresh(pos)
    return {"detail": f"Position {position_id} updated."}


# ---------------------------------------------------------
# DELETE POSITION
# ---------------------------------------------------------
@router.delete("/{position_id}")
def delete_position(position_id: int, db: Session = Depends(get_db)):
    pos = db.query(Positions).filter(Positions.PositionId == position_id).first()
    if not pos:
        raise HTTPException(status_code=404, detail="Position not found.")
    db.delete(pos)
    db.commit()
    return {"detail": f"Position {position_id} deleted."}
