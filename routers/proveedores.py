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
    # Verificar si el nombre ya existe
    existing_nombre = db.query(Proveedor).filter(Proveedor.nombre == proveedor.nombre).first()
    if existing_nombre:
        raise HTTPException(status_code=400, detail="Ya existe un proveedor con ese nombre")
    
    # Verificar si el RUC ya existe (si se proporciona)
    if proveedor.ruc:
        existing_ruc = db.query(Proveedor).filter(Proveedor.ruc == proveedor.ruc).first()
        if existing_ruc:
            raise HTTPException(status_code=400, detail="Ya existe un proveedor con ese RUC")
    
    db_proveedor = Proveedor(nombre=proveedor.nombre, ruc=proveedor.ruc)
    db.add(db_proveedor)
    db.commit()
    db.refresh(db_proveedor)
    return db_proveedor

@router.put("/{proveedor_id}", response_model=schemas.ProveedorOut)
def update_proveedor(proveedor_id: int, proveedor_update: schemas.ProveedorUpdate, db: Session = Depends(get_db)):
    db_proveedor = db.query(Proveedor).filter(Proveedor.id == proveedor_id).first()
    if not db_proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    # Validar nombre único (si se cambia)
    if proveedor_update.nombre and proveedor_update.nombre != db_proveedor.nombre:
        existing_nombre = db.query(Proveedor).filter(
            Proveedor.nombre == proveedor_update.nombre,
            Proveedor.id != proveedor_id
        ).first()
        if existing_nombre:
            raise HTTPException(status_code=400, detail="Ya existe un proveedor con ese nombre")
        db_proveedor.nombre = proveedor_update.nombre
    
    # Validar RUC único (si se cambia)
    if proveedor_update.ruc is not None and proveedor_update.ruc != db_proveedor.ruc:
        if proveedor_update.ruc:  # Solo validar si no es vacío
            existing_ruc = db.query(Proveedor).filter(
                Proveedor.ruc == proveedor_update.ruc,
                Proveedor.id != proveedor_id
            ).first()
            if existing_ruc:
                raise HTTPException(status_code=400, detail="Ya existe un proveedor con ese RUC")
        db_proveedor.ruc = proveedor_update.ruc
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
