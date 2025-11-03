from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..db import get_db
from Backend.models import Positions

router = APIRouter(prefix="/positions", tags=["Positions"])


# =============================
# GET ALL POSITIONS
# =============================
@router.get("/", response_model=List[dict])
def get_positions(db: Session = Depends(get_db)):
    positions = db.query(Positions).all()
    return [
        {
            "PositionId": p.PositionId,
            "PositionTitle": p.PositionTitle,
            "Company": p.Company,
            "Location": p.Location,
            "ContactName": p.ContactName,
            "ContactEmail": p.ContactEmail,
            "StartDate": p.StartDate,
            "EndDate": p.EndDate,
            "CreatedAtUtc": p.CreatedAtUtc,
        }
        for p in positions
    ]


# =============================
# GET ONE POSITION
# =============================
@router.get("/{position_id}", response_model=dict)
def get_position(position_id: int, db: Session = Depends(get_db)):
    position = db.query(Positions).filter(Positions.PositionId == position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found.")
    return {
        "PositionId": position.PositionId,
        "PositionTitle": position.PositionTitle,
        "Company": position.Company,
        "Location": position.Location,
        "ContactName": position.ContactName,
        "ContactEmail": position.ContactEmail,
        "StartDate": position.StartDate,
        "EndDate": position.EndDate,
        "CreatedAtUtc": position.CreatedAtUtc,
    }


# =============================
# CREATE POSITION
# =============================
@router.post("/", status_code=201)
def create_position(data: dict, db: Session = Depends(get_db)):
    position = Positions(
        PositionTitle=data.get("PositionTitle"),
        Company=data.get("Company"),
        Location=data.get("Location"),
        ContactName=data.get("ContactName"),
        ContactEmail=data.get("ContactEmail"),
        StartDate=data.get("StartDate"),
        EndDate=data.get("EndDate"),
        CreatedAtUtc=datetime.utcnow(),
    )
    db.add(position)
    db.commit()
    db.refresh(position)
    return {"detail": f"Position '{position.PositionTitle}' created successfully."}


# =============================
# UPDATE POSITION
# =============================
@router.put("/{position_id}")
def update_position(position_id: int, data: dict, db: Session = Depends(get_db)):
    position = db.query(Positions).filter(Positions.PositionId == position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found.")

    for key, value in data.items():
        if hasattr(position, key) and value is not None:
            setattr(position, key, value)

    db.commit()
    db.refresh(position)
    return {"detail": f"Position ID {position_id} updated successfully."}


# =============================
# DELETE POSITION
# =============================
@router.delete("/{position_id}")
def delete_position(position_id: int, db: Session = Depends(get_db)):
    position = db.query(Positions).filter(Positions.PositionId == position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found.")
    db.delete(position)
    db.commit()
    return {"detail": f"Position ID {position_id} deleted successfully."}
