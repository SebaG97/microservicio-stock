from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Procedencia
import schemas

router = APIRouter(
    prefix="/procedencias",
    tags=["procedencias"]
)

@router.get("/", response_model=List[schemas.ProcedenciaOut])
def get_procedencias(db: Session = Depends(get_db)):
    return db.query(Procedencia).all()

@router.post("/", response_model=schemas.ProcedenciaOut)
def create_procedencia(procedencia: schemas.ProcedenciaCreate, db: Session = Depends(get_db)):
    db_procedencia = Procedencia(nombre=procedencia.nombre)
    db.add(db_procedencia)
    db.commit()
    db.refresh(db_procedencia)
    return db_procedencia

@router.put("/{procedencia_id}", response_model=schemas.ProcedenciaOut)
def update_procedencia(procedencia_id: int, procedencia: schemas.ProcedenciaCreate, db: Session = Depends(get_db)):
    db_procedencia = db.query(Procedencia).filter(Procedencia.id == procedencia_id).first()
    if not db_procedencia:
        raise HTTPException(status_code=404, detail="Procedencia no encontrada")
    db_procedencia.nombre = procedencia.nombre
    db.commit()
    db.refresh(db_procedencia)
    return db_procedencia

@router.delete("/{procedencia_id}")
def delete_procedencia(procedencia_id: int, db: Session = Depends(get_db)):
    db_procedencia = db.query(Procedencia).filter(Procedencia.id == procedencia_id).first()
    if not db_procedencia:
        raise HTTPException(status_code=404, detail="Procedencia no encontrada")
    db.delete(db_procedencia)
    db.commit()
    return {"ok": True}
