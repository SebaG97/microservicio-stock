from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Estado
import schemas

router = APIRouter(
    prefix="/estados",
    tags=["estados"]
)

@router.get("/", response_model=List[schemas.EstadoOut])
def get_estados(db: Session = Depends(get_db)):
    return db.query(Estado).all()

@router.post("/", response_model=schemas.EstadoOut)
def create_estado(estado: schemas.EstadoCreate, db: Session = Depends(get_db)):
    db_estado = Estado(nombre=estado.nombre)
    db.add(db_estado)
    db.commit()
    db.refresh(db_estado)
    return db_estado

@router.put("/{estado_id}", response_model=schemas.EstadoOut)
def update_estado(estado_id: int, estado: schemas.EstadoCreate, db: Session = Depends(get_db)):
    db_estado = db.query(Estado).filter(Estado.id == estado_id).first()
    if not db_estado:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    db_estado.nombre = estado.nombre
    db.commit()
    db.refresh(db_estado)
    return db_estado

@router.delete("/{estado_id}")
def delete_estado(estado_id: int, db: Session = Depends(get_db)):
    db_estado = db.query(Estado).filter(Estado.id == estado_id).first()
    if not db_estado:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    db.delete(db_estado)
    db.commit()
    return {"ok": True}
