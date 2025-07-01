from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Rubro
from schemas import RubroCreate, RubroRead, RubroUpdate
from typing import List

router = APIRouter(prefix="/rubros", tags=["rubros"])

@router.get("/", response_model=List[RubroRead])
def read_rubros(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Rubro).offset(skip).limit(limit).all()

@router.get("/{rubro_id}", response_model=RubroRead)
def read_rubro(rubro_id: int, db: Session = Depends(get_db)):
    rubro = db.query(Rubro).filter(Rubro.id == rubro_id).first()
    if not rubro:
        raise HTTPException(status_code=404, detail="Rubro not found")
    return rubro

@router.post("/", response_model=RubroRead)
def create_rubro(rubro: RubroCreate, db: Session = Depends(get_db)):
    db_rubro = Rubro(**rubro.dict())
    db.add(db_rubro)
    db.commit()
    db.refresh(db_rubro)
    return db_rubro

@router.put("/{rubro_id}", response_model=RubroRead)
def update_rubro(rubro_id: int, rubro: RubroUpdate, db: Session = Depends(get_db)):
    db_rubro = db.query(Rubro).filter(Rubro.id == rubro_id).first()
    if not db_rubro:
        raise HTTPException(status_code=404, detail="Rubro not found")
    for key, value in rubro.dict(exclude_unset=True).items():
        setattr(db_rubro, key, value)
    db.commit()
    db.refresh(db_rubro)
    return db_rubro

@router.delete("/{rubro_id}")
def delete_rubro(rubro_id: int, db: Session = Depends(get_db)):
    db_rubro = db.query(Rubro).filter(Rubro.id == rubro_id).first()
    if not db_rubro:
        raise HTTPException(status_code=404, detail="Rubro not found")
    db.delete(db_rubro)
    db.commit()
    return {"ok": True}
