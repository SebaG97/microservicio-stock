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

@router.post("/transferencia/", response_model=schemas.TransferenciaResponse)
def transferencia_stock(
    transferencia: schemas.TransferenciaStock,
    db: Session = Depends(get_db)
):
    """
    Transferir stock entre depósitos: resta del origen y suma al destino
    
    Body JSON:
    {
        "producto_id": 1,
        "deposito_origen_id": 2,
        "deposito_destino_id": 1,
        "cantidad": 5,
        "motivo": "transferencia_deposito"
    }
    """
    try:
        # Validaciones básicas
        if transferencia.cantidad <= 0:
            raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")
        
        if transferencia.deposito_origen_id == transferencia.deposito_destino_id:
            raise HTTPException(status_code=400, detail="Los depósitos origen y destino no pueden ser iguales")
        
        # Verificar que el producto existe
        producto = db.query(Producto).filter(Producto.id == transferencia.producto_id).first()
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto con ID {transferencia.producto_id} no encontrado")
        
        # Verificar que los depósitos existen
        deposito_origen = db.query(Deposito).filter(Deposito.id == transferencia.deposito_origen_id).first()
        if not deposito_origen:
            raise HTTPException(status_code=404, detail=f"Depósito origen con ID {transferencia.deposito_origen_id} no encontrado")
        
        deposito_destino = db.query(Deposito).filter(Deposito.id == transferencia.deposito_destino_id).first()
        if not deposito_destino:
            raise HTTPException(status_code=404, detail=f"Depósito destino con ID {transferencia.deposito_destino_id} no encontrado")
        
        # Verificar stock origen
        stock_origen = db.query(Stock).filter(
            Stock.producto_id == transferencia.producto_id, 
            Stock.deposito_id == transferencia.deposito_origen_id
        ).first()
        
        if not stock_origen:
            raise HTTPException(
                status_code=400, 
                detail=f"No existe stock del producto '{producto.descripcion}' en el depósito '{deposito_origen.nombre}'"
            )
        
        if stock_origen.existencia < transferencia.cantidad:
            raise HTTPException(
                status_code=400, 
                detail=f"Stock insuficiente en '{deposito_origen.nombre}'. Disponible: {stock_origen.existencia}, Solicitado: {transferencia.cantidad}"
            )
        
        # Obtener o crear stock destino
        stock_destino = db.query(Stock).filter(
            Stock.producto_id == transferencia.producto_id, 
            Stock.deposito_id == transferencia.deposito_destino_id
        ).first()
        
        if not stock_destino:
            stock_destino = Stock(
                producto_id=transferencia.producto_id, 
                deposito_id=transferencia.deposito_destino_id, 
                existencia=0, 
                stock_minimo=0
            )
            db.add(stock_destino)
        
        # Realizar transferencia
        stock_origen.existencia -= transferencia.cantidad
        stock_destino.existencia += transferencia.cantidad
        
        # Crear movimiento de egreso (origen)
        movimiento_egreso = StockMovimiento(
            producto_id=transferencia.producto_id,
            deposito_id=transferencia.deposito_origen_id,
            cantidad=transferencia.cantidad,
            tipo=schemas.MovimientoTipo.egreso,
            motivo=transferencia.motivo
        )
        db.add(movimiento_egreso)
        
        # Crear movimiento de ingreso (destino)
        movimiento_ingreso = StockMovimiento(
            producto_id=transferencia.producto_id,
            deposito_id=transferencia.deposito_destino_id,
            cantidad=transferencia.cantidad,
            tipo=schemas.MovimientoTipo.ingreso,
            motivo=transferencia.motivo
        )
        db.add(movimiento_ingreso)
        
        db.commit()
        
        return schemas.TransferenciaResponse(
            mensaje="Transferencia realizada exitosamente",
            producto_id=transferencia.producto_id,
            deposito_origen_id=transferencia.deposito_origen_id,
            deposito_destino_id=transferencia.deposito_destino_id,
            cantidad=transferencia.cantidad,
            stock_origen_actual=stock_origen.existencia,
            stock_destino_actual=stock_destino.existencia
        )
        
    except HTTPException:
        # Re-lanzar las excepciones HTTP que ya tienen el mensaje correcto
        raise
    except Exception as e:
        # Para cualquier otro error, proporcionar un mensaje genérico
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
