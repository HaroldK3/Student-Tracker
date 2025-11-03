from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from Backend.models import Positions, PositionOut, PositionCreate, PositionUpdate
from typing import List

router = APIRouter(prefix="/positions", tags=["Positions"])


# Get all positions
@router.get("/", response_model=List[PositionOut])
def get_positions(db: Session = Depends(get_db)):
    positions = db.query(Positions).all()
    return positions


# Get one position
@router.get("/{position_id}", response_model=PositionOut)
def get_position(position_id: int, db: Session = Depends(get_db)):
    position = db.query(Positions).filter(Positions.PositionId == position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found.")
    return position


# Create a position
@router.post("/", response_model=PositionOut, status_code=201)
def create_position(data: PositionCreate, db: Session = Depends(get_db)):
    position = Positions(**data.model_dump())
    db.add(position)
    db.commit()
    db.refresh(position)
    return position


# Update a position
@router.put("/{position_id}", response_model=PositionOut)
def update_position(position_id: int, data: PositionUpdate, db: Session = Depends(get_db)):
    position = db.query(Positions).filter(Positions.PositionId == position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found.")

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(position, key, value)

    db.commit()
    db.refresh(position)
    return position


# Soft delete a position
@router.delete("/{position_id}", status_code=204)
def delete_position(position_id: int, db: Session = Depends(get_db)):
    position = db.query(Positions).filter(Positions.PositionId == position_id).first()
    if not position:
        raise HTTPException(status_code=404, detail="Position not found.")

    # if you have an IsActive column, do a soft delete
    if hasattr(position, "IsActive"):
        position.IsActive = False
    else:
        db.delete(position)

    db.commit()
    return
