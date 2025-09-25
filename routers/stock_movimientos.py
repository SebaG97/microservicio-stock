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

@router.post("/multiple/", response_model=schemas.MovimientoMultipleResponse)
def movimiento_multiple(
    movimiento: schemas.MovimientoMultiple,
    db: Session = Depends(get_db)
):
    """
    Registrar movimiento de stock con múltiples productos
    
    Tipos de movimiento:
    - ingreso: Sumar stock (compras, devoluciones, etc.)
    - egreso: Restar stock (ventas, consumos, etc.)
    - ajuste: Ajustar stock (inventario, correcciones, etc.)
    
    Body JSON:
    {
        "deposito_id": 1,
        "tipo": "egreso",
        "items": [
            {"producto_id": 1, "cantidad": 5, "precio_unitario": 100.0},
            {"producto_id": 2, "cantidad": 2, "precio_unitario": 50.0}
        ],
        "motivo": "venta_cliente",
        "cliente_id": "12345",
        "cliente_empresa": "ACME Corp"
    }
    """
    try:
        # Validaciones básicas
        if not movimiento.items:
            raise HTTPException(status_code=400, detail="Debe incluir al menos un item")
        
        # Verificar que el depósito existe
        deposito = db.query(Deposito).filter(Deposito.id == movimiento.deposito_id).first()
        if not deposito:
            raise HTTPException(status_code=404, detail=f"Depósito con ID {movimiento.deposito_id} no encontrado")
        
        resultados = []
        items_exitosos = 0
        items_fallidos = 0
        total_valor = 0.0
        
        for item in movimiento.items:
            try:
                # Verificar que el producto existe
                producto = db.query(Producto).filter(Producto.id == item.producto_id).first()
                if not producto:
                    resultados.append(schemas.ResultadoItemMovimiento(
                        producto_id=item.producto_id,
                        descripcion=f"Producto ID {item.producto_id}",
                        cantidad=item.cantidad,
                        stock_anterior=0,
                        stock_actual=0,
                        exitoso=False,
                        error=f"Producto con ID {item.producto_id} no encontrado",
                        precio_unitario=item.precio_unitario
                    ))
                    items_fallidos += 1
                    continue
                
                # Obtener o crear stock
                stock = db.query(Stock).filter(
                    Stock.producto_id == item.producto_id,
                    Stock.deposito_id == movimiento.deposito_id
                ).first()
                
                if not stock:
                    stock = Stock(
                        producto_id=item.producto_id,
                        deposito_id=movimiento.deposito_id,
                        existencia=0,
                        stock_minimo=0
                    )
                    db.add(stock)
                
                stock_anterior = stock.existencia
                
                # Aplicar movimiento según el tipo
                if movimiento.tipo == schemas.MovimientoTipo.ingreso:
                    stock.existencia += item.cantidad
                elif movimiento.tipo == schemas.MovimientoTipo.egreso:
                    if stock.existencia < item.cantidad:
                        resultados.append(schemas.ResultadoItemMovimiento(
                            producto_id=item.producto_id,
                            descripcion=producto.descripcion,
                            cantidad=item.cantidad,
                            stock_anterior=stock_anterior,
                            stock_actual=stock_anterior,
                            exitoso=False,
                            error=f"Stock insuficiente. Disponible: {stock.existencia}, Solicitado: {item.cantidad}",
                            precio_unitario=item.precio_unitario
                        ))
                        items_fallidos += 1
                        continue
                    stock.existencia -= item.cantidad
                elif movimiento.tipo == schemas.MovimientoTipo.ajuste:
                    stock.existencia += item.cantidad  # Para ajustes, cantidad puede ser negativa
                
                # Crear registro de movimiento
                movimiento_registro = StockMovimiento(
                    producto_id=item.producto_id,
                    deposito_id=movimiento.deposito_id,
                    cantidad=item.cantidad,
                    tipo=movimiento.tipo,
                    motivo=movimiento.motivo,
                    cliente_id=movimiento.cliente_id,
                    cliente_empresa=movimiento.cliente_empresa
                )
                db.add(movimiento_registro)
                
                # Calcular valor si tiene precio
                if item.precio_unitario:
                    total_valor += item.cantidad * item.precio_unitario
                
                resultados.append(schemas.ResultadoItemMovimiento(
                    producto_id=item.producto_id,
                    descripcion=producto.descripcion,
                    cantidad=item.cantidad,
                    stock_anterior=stock_anterior,
                    stock_actual=stock.existencia,
                    exitoso=True,
                    error=None,
                    precio_unitario=item.precio_unitario
                ))
                items_exitosos += 1
                
            except Exception as e:
                resultados.append(schemas.ResultadoItemMovimiento(
                    producto_id=item.producto_id,
                    descripcion=f"Producto ID {item.producto_id}",
                    cantidad=item.cantidad,
                    stock_anterior=0,
                    stock_actual=0,
                    exitoso=False,
                    error=f"Error procesando item: {str(e)}",
                    precio_unitario=item.precio_unitario
                ))
                items_fallidos += 1
        
        # Solo hacer commit si al menos un item fue exitoso
        if items_exitosos > 0:
            db.commit()
        
        return schemas.MovimientoMultipleResponse(
            mensaje=f"Movimiento procesado: {items_exitosos} exitosos, {items_fallidos} fallidos",
            deposito_id=movimiento.deposito_id,
            tipo=movimiento.tipo.value,
            items_procesados=len(movimiento.items),
            items_exitosos=items_exitosos,
            items_fallidos=items_fallidos,
            total_valor=total_valor if total_valor > 0 else None,
            resultados=resultados
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.post("/transferencia-multiple/", response_model=schemas.TransferenciaMultipleResponse)
def transferencia_multiple(
    transferencia: schemas.TransferenciaMultiple,
    db: Session = Depends(get_db)
):
    """
    Transferir múltiples productos entre depósitos
    
    Body JSON:
    {
        "deposito_origen_id": 1,
        "deposito_destino_id": 2,
        "items": [
            {"producto_id": 1, "cantidad": 5},
            {"producto_id": 2, "cantidad": 2}
        ],
        "motivo": "transferencia_multiple"
    }
    """
    try:
        # Validaciones básicas
        if not transferencia.items:
            raise HTTPException(status_code=400, detail="Debe incluir al menos un item")
        
        if transferencia.deposito_origen_id == transferencia.deposito_destino_id:
            raise HTTPException(status_code=400, detail="Los depósitos origen y destino no pueden ser iguales")
        
        # Verificar que los depósitos existen
        deposito_origen = db.query(Deposito).filter(Deposito.id == transferencia.deposito_origen_id).first()
        if not deposito_origen:
            raise HTTPException(status_code=404, detail=f"Depósito origen con ID {transferencia.deposito_origen_id} no encontrado")
        
        deposito_destino = db.query(Deposito).filter(Deposito.id == transferencia.deposito_destino_id).first()
        if not deposito_destino:
            raise HTTPException(status_code=404, detail=f"Depósito destino con ID {transferencia.deposito_destino_id} no encontrado")
        
        resultados = []
        items_exitosos = 0
        items_fallidos = 0
        
        for item in transferencia.items:
            try:
                # Verificar que el producto existe
                producto = db.query(Producto).filter(Producto.id == item.producto_id).first()
                if not producto:
                    resultados.append(schemas.ResultadoItemTransferencia(
                        producto_id=item.producto_id,
                        descripcion=f"Producto ID {item.producto_id}",
                        cantidad=item.cantidad,
                        stock_origen_anterior=0,
                        stock_origen_actual=0,
                        stock_destino_anterior=0,
                        stock_destino_actual=0,
                        exitoso=False,
                        error=f"Producto con ID {item.producto_id} no encontrado"
                    ))
                    items_fallidos += 1
                    continue
                
                # Verificar stock origen
                stock_origen = db.query(Stock).filter(
                    Stock.producto_id == item.producto_id,
                    Stock.deposito_id == transferencia.deposito_origen_id
                ).first()
                
                if not stock_origen or stock_origen.existencia < item.cantidad:
                    stock_disponible = stock_origen.existencia if stock_origen else 0
                    resultados.append(schemas.ResultadoItemTransferencia(
                        producto_id=item.producto_id,
                        descripcion=producto.descripcion,
                        cantidad=item.cantidad,
                        stock_origen_anterior=stock_disponible,
                        stock_origen_actual=stock_disponible,
                        stock_destino_anterior=0,
                        stock_destino_actual=0,
                        exitoso=False,
                        error=f"Stock insuficiente en '{deposito_origen.nombre}'. Disponible: {stock_disponible}, Solicitado: {item.cantidad}"
                    ))
                    items_fallidos += 1
                    continue
                
                # Obtener o crear stock destino
                stock_destino = db.query(Stock).filter(
                    Stock.producto_id == item.producto_id,
                    Stock.deposito_id == transferencia.deposito_destino_id
                ).first()
                
                if not stock_destino:
                    stock_destino = Stock(
                        producto_id=item.producto_id,
                        deposito_id=transferencia.deposito_destino_id,
                        existencia=0,
                        stock_minimo=0
                    )
                    db.add(stock_destino)
                
                # Guardar stocks anteriores
                stock_origen_anterior = stock_origen.existencia
                stock_destino_anterior = stock_destino.existencia
                
                # Realizar transferencia
                stock_origen.existencia -= item.cantidad
                stock_destino.existencia += item.cantidad
                
                # Crear movimientos de egreso e ingreso
                movimiento_egreso = StockMovimiento(
                    producto_id=item.producto_id,
                    deposito_id=transferencia.deposito_origen_id,
                    cantidad=item.cantidad,
                    tipo=schemas.MovimientoTipo.egreso,
                    motivo=transferencia.motivo
                )
                db.add(movimiento_egreso)
                
                movimiento_ingreso = StockMovimiento(
                    producto_id=item.producto_id,
                    deposito_id=transferencia.deposito_destino_id,
                    cantidad=item.cantidad,
                    tipo=schemas.MovimientoTipo.ingreso,
                    motivo=transferencia.motivo
                )
                db.add(movimiento_ingreso)
                
                resultados.append(schemas.ResultadoItemTransferencia(
                    producto_id=item.producto_id,
                    descripcion=producto.descripcion,
                    cantidad=item.cantidad,
                    stock_origen_anterior=stock_origen_anterior,
                    stock_origen_actual=stock_origen.existencia,
                    stock_destino_anterior=stock_destino_anterior,
                    stock_destino_actual=stock_destino.existencia,
                    exitoso=True,
                    error=None
                ))
                items_exitosos += 1
                
            except Exception as e:
                resultados.append(schemas.ResultadoItemTransferencia(
                    producto_id=item.producto_id,
                    descripcion=f"Producto ID {item.producto_id}",
                    cantidad=item.cantidad,
                    stock_origen_anterior=0,
                    stock_origen_actual=0,
                    stock_destino_anterior=0,
                    stock_destino_actual=0,
                    exitoso=False,
                    error=f"Error procesando item: {str(e)}"
                ))
                items_fallidos += 1
        
        # Solo hacer commit si al menos un item fue exitoso
        if items_exitosos > 0:
            db.commit()
        
        return schemas.TransferenciaMultipleResponse(
            mensaje=f"Transferencia procesada: {items_exitosos} exitosos, {items_fallidos} fallidos",
            deposito_origen_id=transferencia.deposito_origen_id,
            deposito_destino_id=transferencia.deposito_destino_id,
            items_procesados=len(transferencia.items),
            items_exitosos=items_exitosos,
            items_fallidos=items_fallidos,
            resultados=resultados
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
