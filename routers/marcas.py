from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Marca
import schemas

router = APIRouter(
    prefix="/marcas",
    tags=["marcas"]
)

@router.get("/", response_model=List[schemas.MarcaOut])
def get_marcas(db: Session = Depends(get_db)):
    return db.query(Marca).all()

@router.post("/", response_model=schemas.MarcaOut)
def create_marca(marca: schemas.MarcaCreate, db: Session = Depends(get_db)):
    db_marca = Marca(nombre=marca.nombre)
    db.add(db_marca)
    db.commit()
    db.refresh(db_marca)
    return db_marca

@router.put("/{marca_id}", response_model=schemas.MarcaOut)
def update_marca(marca_id: int, marca: schemas.MarcaCreate, db: Session = Depends(get_db)):
    db_marca = db.query(Marca).filter(Marca.id == marca_id).first()
    if not db_marca:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    db_marca.nombre = marca.nombre
    db.commit()
    db.refresh(db_marca)
    return db_marca

@router.delete("/{marca_id}")
def delete_marca(marca_id: int, db: Session = Depends(get_db)):
    db_marca = db.query(Marca).filter(Marca.id == marca_id).first()
    if not db_marca:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    db.delete(db_marca)
    db.commit()
    return {"ok": True}
