from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import CajaChica, GastoCajaChica, GastoProducto, Producto, Stock, StockMovimiento, MovimientoTipo, Proveedor, Deposito
from schemas import (
    CajaChicaCreate, CajaChicaOut, CajaChicaUpdate, CajaChicaResumen,
    GastoCajaChicaCreate, GastoCajaChicaOut, GastoCajaChicaUpdate,
    GastoProductoOut, ProveedorCreate, ProveedorOut, AjusteSaldoRequest
)
from typing import List, Optional
from datetime import datetime
from sqlalchemy import desc, func, extract

router = APIRouter(prefix="/caja-chica", tags=["Caja Chica"])

# --- ENDPOINTS DE CAJA CHICA ---

@router.post("/", response_model=CajaChicaOut)
def crear_caja_chica(caja_chica: CajaChicaCreate, db: Session = Depends(get_db)):
    """Crear una nueva caja chica o actualizar la existente"""
    
    # Desactivar todas las cajas chicas anteriores
    db.query(CajaChica).update({"activo": False})
    
    db_caja_chica = CajaChica(
        monto_inicial=caja_chica.monto_inicial,
        saldo_actual=caja_chica.monto_inicial,
        activo=True
    )
    db.add(db_caja_chica)
    db.commit()
    db.refresh(db_caja_chica)
    return db_caja_chica

@router.get("/actual", response_model=CajaChicaOut)
def obtener_caja_chica_actual(db: Session = Depends(get_db)):
    """Obtener la caja chica activa actual"""
    caja_chica = db.query(CajaChica).filter(CajaChica.activo == True).first()
    if not caja_chica:
        raise HTTPException(status_code=404, detail="No hay caja chica activa")
    return caja_chica

@router.put("/{caja_chica_id}", response_model=CajaChicaOut)
def actualizar_monto_caja_chica(caja_chica_id: int, caja_chica_update: CajaChicaUpdate, db: Session = Depends(get_db)):
    """Actualizar el monto inicial de la caja chica y recalcular saldo"""
    caja_chica = db.query(CajaChica).filter(CajaChica.id == caja_chica_id).first()
    if not caja_chica:
        raise HTTPException(status_code=404, detail="Caja chica no encontrada")
    
    # Calcular total de gastos
    total_gastos = db.query(func.sum(GastoCajaChica.monto_total)).filter(
        GastoCajaChica.caja_chica_id == caja_chica_id
    ).scalar() or 0
    
    if caja_chica_update.monto_inicial is not None:
        caja_chica.monto_inicial = caja_chica_update.monto_inicial
        caja_chica.saldo_actual = caja_chica_update.monto_inicial - total_gastos
    
    db.commit()
    db.refresh(caja_chica)
    return caja_chica

@router.get("/resumen", response_model=CajaChicaResumen)
def obtener_resumen_caja_chica(db: Session = Depends(get_db)):
    """Obtener resumen completo de la caja chica actual"""
    caja_chica = db.query(CajaChica).filter(CajaChica.activo == True).first()
    if not caja_chica:
        # Si no hay caja chica, crear una por defecto
        caja_chica = CajaChica(
            monto_inicial=0.0,
            saldo_actual=0.0,
            activo=True
        )
        db.add(caja_chica)
        db.commit()
        db.refresh(caja_chica)
    
    # Calcular gastos totales
    gastos_totales = db.query(func.sum(GastoCajaChica.monto_total)).filter(
        GastoCajaChica.caja_chica_id == caja_chica.id
    ).scalar() or 0.0
    
    # Calcular gastos del mes actual
    mes_actual = datetime.now().month
    año_actual = datetime.now().year
    gastos_del_mes = db.query(func.sum(GastoCajaChica.monto_total)).filter(
        GastoCajaChica.caja_chica_id == caja_chica.id,
        extract('month', GastoCajaChica.fecha_factura) == mes_actual,
        extract('year', GastoCajaChica.fecha_factura) == año_actual
    ).scalar() or 0.0
    
    # Obtener último gasto
    ultimo_gasto = db.query(GastoCajaChica).filter(
        GastoCajaChica.caja_chica_id == caja_chica.id
    ).order_by(desc(GastoCajaChica.fecha_registro)).first()
    
    # Actualizar saldo actual
    caja_chica.saldo_actual = caja_chica.monto_inicial - gastos_totales
    db.commit()
    
    return CajaChicaResumen(
        caja_chica=caja_chica,
        gastos_totales=gastos_totales,
        gastos_del_mes=gastos_del_mes,
        ultimo_gasto=ultimo_gasto
    )

@router.post("/ajustar-saldo")
def ajustar_saldo(ajuste: AjusteSaldoRequest, db: Session = Depends(get_db)):
    """Ajustar saldo manualmente"""
    caja_chica = db.query(CajaChica).filter(CajaChica.activo == True).first()
    if not caja_chica:
        raise HTTPException(status_code=404, detail="No hay caja chica activa")
    
    # Calcular total de gastos
    gastos_totales = db.query(func.sum(GastoCajaChica.monto_total)).filter(
        GastoCajaChica.caja_chica_id == caja_chica.id
    ).scalar() or 0.0
    
    caja_chica.monto_inicial = ajuste.nuevo_monto
    caja_chica.saldo_actual = ajuste.nuevo_monto - gastos_totales
    
    db.commit()
    return {"mensaje": "Saldo ajustado correctamente", "nuevo_saldo": caja_chica.saldo_actual}

# --- ENDPOINTS DE GASTOS ---

@router.post("/gastos/", response_model=GastoCajaChicaOut)
def crear_gasto(gasto: GastoCajaChicaCreate, db: Session = Depends(get_db)):
    """Crear un nuevo gasto de caja chica con productos opcionales"""
    
    # Obtener caja chica activa
    caja_chica = db.query(CajaChica).filter(CajaChica.activo == True).first()
    if not caja_chica:
        raise HTTPException(status_code=404, detail="No hay caja chica activa")
    
    # Validar proveedor si se proporciona ID
    if gasto.proveedor_id:
        proveedor = db.query(Proveedor).filter(Proveedor.id == gasto.proveedor_id).first()
        if not proveedor:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    
    # Calcular monto total de productos
    monto_productos = 0
    for producto in gasto.productos:
        monto_productos += producto.cantidad * producto.precio_unitario
    
    # Crear el gasto
    db_gasto = GastoCajaChica(
        caja_chica_id=caja_chica.id,
        proveedor_id=gasto.proveedor_id,
        proveedor_nombre=gasto.proveedor_nombre,
        numero_factura=gasto.numero_factura,
        fecha_factura=gasto.fecha_factura,
        descripcion=gasto.descripcion,
        monto_total=monto_productos
    )
    db.add(db_gasto)
    db.flush()  # Para obtener el ID del gasto
    
    # Crear productos asociados y movimientos de stock
    for producto_data in gasto.productos:
        # Verificar que el producto existe
        producto = db.query(Producto).filter(Producto.id == producto_data.producto_id).first()
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {producto_data.producto_id} no encontrado")
        
        subtotal = producto_data.cantidad * producto_data.precio_unitario
        
        # Crear el gasto producto
        db_gasto_producto = GastoProducto(
            gasto_id=db_gasto.id,
            producto_id=producto_data.producto_id,
            deposito_id=producto_data.deposito_id,
            cantidad=producto_data.cantidad,
            precio_unitario=producto_data.precio_unitario,
            subtotal=subtotal
        )
        db.add(db_gasto_producto)
        
        # Actualizar stock existente o crear nuevo
        stock_existente = db.query(Stock).filter(
            Stock.producto_id == producto_data.producto_id,
            Stock.deposito_id == producto_data.deposito_id
        ).first()
        
        if stock_existente:
            stock_existente.existencia += producto_data.cantidad
        else:
            nuevo_stock = Stock(
                producto_id=producto_data.producto_id,
                deposito_id=producto_data.deposito_id,
                existencia=producto_data.cantidad,
                stock_minimo=0
            )
            db.add(nuevo_stock)
        
        # Crear movimiento de stock
        movimiento = StockMovimiento(
            producto_id=producto_data.producto_id,
            deposito_id=producto_data.deposito_id,
            cantidad=producto_data.cantidad,
            tipo=MovimientoTipo.ingreso,
            motivo=f"Compra por caja chica - Factura: {gasto.numero_factura}",
            cliente_empresa=gasto.proveedor_nombre or (proveedor.nombre if gasto.proveedor_id else "Sin proveedor")
        )
        db.add(movimiento)
    
    # Actualizar saldo de caja chica
    caja_chica.saldo_actual -= db_gasto.monto_total
    
    db.commit()
    db.refresh(db_gasto)
    return db_gasto

@router.get("/gastos/", response_model=List[GastoCajaChicaOut])
def listar_gastos(
    skip: int = 0, 
    limit: int = 100, 
    mes: Optional[int] = None,
    año: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Listar gastos de caja chica con filtros opcionales"""
    query = db.query(GastoCajaChica)
    
    if mes:
        query = query.filter(extract('month', GastoCajaChica.fecha_factura) == mes)
    if año:
        query = query.filter(extract('year', GastoCajaChica.fecha_factura) == año)
    
    gastos = query.order_by(desc(GastoCajaChica.fecha_registro)).offset(skip).limit(limit).all()
    return gastos

@router.get("/gastos/{gasto_id}", response_model=GastoCajaChicaOut)
def obtener_gasto(gasto_id: int, db: Session = Depends(get_db)):
    """Obtener un gasto específico con todos sus detalles"""
    gasto = db.query(GastoCajaChica).filter(GastoCajaChica.id == gasto_id).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    return gasto

@router.put("/gastos/{gasto_id}", response_model=GastoCajaChicaOut)
def actualizar_gasto(gasto_id: int, gasto_update: GastoCajaChicaUpdate, db: Session = Depends(get_db)):
    """Actualizar un gasto existente (solo datos básicos, no productos)"""
    gasto = db.query(GastoCajaChica).filter(GastoCajaChica.id == gasto_id).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    
    update_data = gasto_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(gasto, field, value)
    
    db.commit()
    db.refresh(gasto)
    return gasto

@router.delete("/gastos/{gasto_id}")
def eliminar_gasto(gasto_id: int, db: Session = Depends(get_db)):
    """Eliminar un gasto y revertir movimientos de stock asociados"""
    gasto = db.query(GastoCajaChica).filter(GastoCajaChica.id == gasto_id).first()
    if not gasto:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    
    # Revertir movimientos de stock
    gastos_productos = db.query(GastoProducto).filter(GastoProducto.gasto_id == gasto_id).all()
    
    for gasto_producto in gastos_productos:
        # Reducir stock
        stock = db.query(Stock).filter(
            Stock.producto_id == gasto_producto.producto_id,
            Stock.deposito_id == gasto_producto.deposito_id
        ).first()
        
        if stock:
            stock.existencia -= gasto_producto.cantidad
            if stock.existencia < 0:
                stock.existencia = 0
        
        # Crear movimiento de corrección
        movimiento_correccion = StockMovimiento(
            producto_id=gasto_producto.producto_id,
            deposito_id=gasto_producto.deposito_id,
            cantidad=gasto_producto.cantidad,
            tipo=MovimientoTipo.egreso,
            motivo=f"Corrección por eliminación de gasto - Factura: {gasto.numero_factura}"
        )
        db.add(movimiento_correccion)
        
        # Eliminar gasto producto
        db.delete(gasto_producto)
    
    # Actualizar saldo de caja chica
    caja_chica = db.query(CajaChica).filter(CajaChica.id == gasto.caja_chica_id).first()
    if caja_chica:
        caja_chica.saldo_actual += gasto.monto_total
    
    # Eliminar el gasto
    db.delete(gasto)
    db.commit()
    
    return {"message": "Gasto eliminado correctamente"}

# --- ENDPOINTS AUXILIARES ---

@router.post("/proveedores/", response_model=ProveedorOut)
def crear_proveedor_rapido(proveedor: ProveedorCreate, db: Session = Depends(get_db)):
    """Crear un proveedor nuevo rápidamente desde el formulario de gastos"""
    # Verificar que no existe
    existing = db.query(Proveedor).filter(Proveedor.nombre == proveedor.nombre).first()
    if existing:
        raise HTTPException(status_code=400, detail="El proveedor ya existe")
    
    if proveedor.ruc:
        existing_ruc = db.query(Proveedor).filter(Proveedor.ruc == proveedor.ruc).first()
        if existing_ruc:
            raise HTTPException(status_code=400, detail="Ya existe un proveedor con ese RUC")
    
    db_proveedor = Proveedor(**proveedor.dict())
    db.add(db_proveedor)
    db.commit()
    db.refresh(db_proveedor)
    return db_proveedor

@router.get("/gastos/productos/{gasto_id}", response_model=List[GastoProductoOut])
def obtener_productos_gasto(gasto_id: int, db: Session = Depends(get_db)):
    """Obtener todos los productos asociados a un gasto específico"""
    productos = db.query(GastoProducto).filter(GastoProducto.gasto_id == gasto_id).all()
    return productos