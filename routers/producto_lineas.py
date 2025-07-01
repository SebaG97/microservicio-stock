from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import ProductoLinea
import schemas

router = APIRouter(
    prefix="/producto_lineas",
    tags=["producto_lineas"]
)

@router.get("/", response_model=List[schemas.ProductoLineaOut])
def get_producto_lineas(db: Session = Depends(get_db)):
    return db.query(ProductoLinea).all()

@router.post("/", response_model=schemas.ProductoLineaOut)
def create_producto_linea(linea: schemas.ProductoLineaCreate, db: Session = Depends(get_db)):
    db_linea = ProductoLinea(nombre=linea.nombre)
    db.add(db_linea)
    db.commit()
    db.refresh(db_linea)
    return db_linea

@router.put("/{linea_id}", response_model=schemas.ProductoLineaOut)
def update_producto_linea(linea_id: int, linea: schemas.ProductoLineaCreate, db: Session = Depends(get_db)):
    db_linea = db.query(ProductoLinea).filter(ProductoLinea.id == linea_id).first()
    if not db_linea:
        raise HTTPException(status_code=404, detail="Línea de producto no encontrada")
    db_linea.nombre = linea.nombre
    db.commit()
    db.refresh(db_linea)
    return db_linea

@router.delete("/{linea_id}")
def delete_producto_linea(linea_id: int, db: Session = Depends(get_db)):
    db_linea = db.query(ProductoLinea).filter(ProductoLinea.id == linea_id).first()
    if not db_linea:
        raise HTTPException(status_code=404, detail="Línea de producto no encontrada")
    db.delete(db_linea)
    db.commit()
    return {"ok": True}
