from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Proveedor
import schemas

router = APIRouter(
    prefix="/proveedores",
    tags=["proveedores"]
)

@router.get("/", response_model=List[schemas.ProveedorOut])
def get_proveedores(db: Session = Depends(get_db)):
    return db.query(Proveedor).all()

@router.post("/", response_model=schemas.ProveedorOut)
def create_proveedor(proveedor: schemas.ProveedorCreate, db: Session = Depends(get_db)):
    db_proveedor = Proveedor(nombre=proveedor.nombre)
    db.add(db_proveedor)
    db.commit()
    db.refresh(db_proveedor)
    return db_proveedor

@router.put("/{proveedor_id}", response_model=schemas.ProveedorOut)
def update_proveedor(proveedor_id: int, proveedor: schemas.ProveedorCreate, db: Session = Depends(get_db)):
    db_proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not db_proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    db_proveedor.nombre = proveedor.nombre
    db.commit()
    db.refresh(db_proveedor)
    return db_proveedor

@router.delete("/{proveedor_id}")
def delete_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    db_proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not db_proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    db.delete(db_proveedor)
    db.commit()
    return {"ok": True}
