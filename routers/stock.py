from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Stock, Producto, Deposito
import schemas

router = APIRouter(
    prefix="/stock",
    tags=["stock"]
)

@router.get("/", response_model=List[schemas.StockOut])
def get_stock(db: Session = Depends(get_db)):
    return db.query(Stock).all()

@router.get("/{producto_id}", response_model=List[schemas.StockOut])
def get_stock_producto(producto_id: int, db: Session = Depends(get_db)):
    return db.query(Stock).filter(Stock.producto_id == producto_id).all()

@router.put("/{stock_id}", response_model=schemas.StockOut)
def update_stock(stock_id: int, stock: schemas.StockUpdate, db: Session = Depends(get_db)):
    db_stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock no encontrado")
    for key, value in stock.dict(exclude_unset=True).items():
        setattr(db_stock, key, value)
    db.commit()
    db.refresh(db_stock)
    return db_stock

@router.delete("/{stock_id}")
def delete_stock(stock_id: int, db: Session = Depends(get_db)):
    db_stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stock no encontrado")
    db.delete(db_stock)
    db.commit()
    return {"ok": True}
