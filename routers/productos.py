from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Producto
import schemas

router = APIRouter(
    prefix="/productos",
    tags=["productos"]
)

@router.get("/", response_model=List[schemas.ProductoOut])
def get_productos(db: Session = Depends(get_db)):
    return db.query(Producto).all()

@router.post("/", response_model=schemas.ProductoOut)
def create_producto(producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    db_producto = Producto(**producto.dict())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto

@router.put("/{producto_id}", response_model=schemas.ProductoOut)
def update_producto(producto_id: int, producto: schemas.ProductoCreate, db: Session = Depends(get_db)):
    db_producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for key, value in producto.dict().items():
        setattr(db_producto, key, value)
    db.commit()
    db.refresh(db_producto)
    return db_producto

@router.delete("/{producto_id}")
def delete_producto(producto_id: int, db: Session = Depends(get_db)):
    db_producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not db_producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(db_producto)
    db.commit()
    return {"ok": True}
