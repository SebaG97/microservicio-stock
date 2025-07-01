from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import TipoProducto
import schemas

router = APIRouter(
    prefix="/tipos_producto",
    tags=["tipos_producto"]
)

@router.get("/", response_model=List[schemas.TipoProductoOut])
def get_tipos_producto(db: Session = Depends(get_db)):
    return db.query(TipoProducto).all()

@router.post("/", response_model=schemas.TipoProductoOut)
def create_tipo_producto(tipo: schemas.TipoProductoCreate, db: Session = Depends(get_db)):
    db_tipo = TipoProducto(nombre=tipo.nombre)
    db.add(db_tipo)
    db.commit()
    db.refresh(db_tipo)
    return db_tipo

@router.put("/{tipo_id}", response_model=schemas.TipoProductoOut)
def update_tipo_producto(tipo_id: int, tipo: schemas.TipoProductoCreate, db: Session = Depends(get_db)):
    db_tipo = db.query(TipoProducto).filter(TipoProducto.id == tipo_id).first()
    if not db_tipo:
        raise HTTPException(status_code=404, detail="Tipo de producto no encontrado")
    db_tipo.nombre = tipo.nombre
    db.commit()
    db.refresh(db_tipo)
    return db_tipo

@router.delete("/{tipo_id}")
def delete_tipo_producto(tipo_id: int, db: Session = Depends(get_db)):
    db_tipo = db.query(TipoProducto).filter(TipoProducto.id == tipo_id).first()
    if not db_tipo:
        raise HTTPException(status_code=404, detail="Tipo de producto no encontrado")
    db.delete(db_tipo)
    db.commit()
    return {"ok": True}
