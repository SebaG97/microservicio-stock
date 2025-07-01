from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Deposito
import schemas

router = APIRouter(
    prefix="/depositos",
    tags=["depositos"]
)

@router.get("/", response_model=List[schemas.DepositoOut])
def get_depositos(db: Session = Depends(get_db)):
    return db.query(Deposito).all()

@router.post("/", response_model=schemas.DepositoOut)
def create_deposito(deposito: schemas.DepositoCreate, db: Session = Depends(get_db)):
    db_deposito = Deposito(nombre=deposito.nombre)
    db.add(db_deposito)
    db.commit()
    db.refresh(db_deposito)
    return db_deposito

@router.put("/{deposito_id}", response_model=schemas.DepositoOut)
def update_deposito(deposito_id: int, deposito: schemas.DepositoCreate, db: Session = Depends(get_db)):
    db_deposito = db.query(Deposito).filter(Deposito.id == deposito_id).first()
    if not db_deposito:
        raise HTTPException(status_code=404, detail="Depósito no encontrado")
    db_deposito.nombre = deposito.nombre
    db.commit()
    db.refresh(db_deposito)
    return db_deposito

@router.delete("/{deposito_id}")
def delete_deposito(deposito_id: int, db: Session = Depends(get_db)):
    db_deposito = db.query(Deposito).filter(Deposito.id == deposito_id).first()
    if not db_deposito:
        raise HTTPException(status_code=404, detail="Depósito no encontrado")
    db.delete(db_deposito)
    db.commit()
    return {"ok": True}
