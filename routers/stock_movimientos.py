from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import StockMovimiento, Stock, Producto, Deposito
from datetime import datetime
import schemas

router = APIRouter(
    prefix="/stock/movimientos",
    tags=["stock_movimientos"]
)

@router.get("/", response_model=List[schemas.StockMovimientoOut])
def get_movimientos(db: Session = Depends(get_db)):
    return db.query(StockMovimiento).order_by(StockMovimiento.fecha.desc()).all()

@router.post("/ingreso/", response_model=schemas.StockMovimientoOut)
def ingreso_stock(mov: schemas.StockMovimientoCreate, db: Session = Depends(get_db)):
    # Sumar existencia en stock, crear si no existe
    stock = db.query(Stock).filter(Stock.producto_id == mov.producto_id, Stock.deposito_id == mov.deposito_id).first()
    if not stock:
        stock = Stock(producto_id=mov.producto_id, deposito_id=mov.deposito_id, existencia=0, stock_minimo=0)
        db.add(stock)
    stock.existencia += mov.cantidad
    movimiento = StockMovimiento(
        producto_id=mov.producto_id,
        deposito_id=mov.deposito_id,
        cantidad=mov.cantidad,
        tipo=schemas.MovimientoTipo.ingreso,
        motivo=mov.motivo
    )
    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)
    return movimiento

@router.post("/egreso/", response_model=schemas.StockMovimientoOut)
def egreso_stock(mov: schemas.StockMovimientoCreate, db: Session = Depends(get_db)):
    stock = db.query(Stock).filter(Stock.producto_id == mov.producto_id, Stock.deposito_id == mov.deposito_id).first()
    if not stock or stock.existencia < mov.cantidad:
        raise HTTPException(status_code=400, detail="Stock insuficiente")
    stock.existencia -= mov.cantidad
    movimiento = StockMovimiento(
        producto_id=mov.producto_id,
        deposito_id=mov.deposito_id,
        cantidad=mov.cantidad,
        tipo=schemas.MovimientoTipo.egreso,
        motivo=mov.motivo
    )
    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)
    return movimiento

@router.get("/filtro/", response_model=List[schemas.StockMovimientoOut])
def get_movimientos_filtrados(
    producto_id: int = Query(None),
    deposito_id: int = Query(None),
    fecha_ini: datetime = Query(None),
    fecha_fin: datetime = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(StockMovimiento)
    if producto_id:
        q = q.filter(StockMovimiento.producto_id == producto_id)
    if deposito_id:
        q = q.filter(StockMovimiento.deposito_id == deposito_id)
    if fecha_ini:
        q = q.filter(StockMovimiento.fecha >= fecha_ini)
    if fecha_fin:
        q = q.filter(StockMovimiento.fecha <= fecha_fin)
    return q.order_by(StockMovimiento.fecha.desc()).all()

@router.post("/ajuste/", response_model=schemas.StockMovimientoOut)
def ajuste_stock(mov: schemas.StockMovimientoCreate, db: Session = Depends(get_db)):
    stock = db.query(Stock).filter(Stock.producto_id == mov.producto_id, Stock.deposito_id == mov.deposito_id).first()
    if not stock:
        stock = Stock(producto_id=mov.producto_id, deposito_id=mov.deposito_id, existencia=0, stock_minimo=0)
        db.add(stock)
    stock.existencia += mov.cantidad
    movimiento = StockMovimiento(
        producto_id=mov.producto_id,
        deposito_id=mov.deposito_id,
        cantidad=mov.cantidad,
        tipo=schemas.MovimientoTipo.ajuste,
        motivo=mov.motivo
    )
    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)
    return movimiento
