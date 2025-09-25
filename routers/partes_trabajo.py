from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from database import get_db
from models import ParteTrabajo, Tecnico, StockMovimiento, Producto
import schemas
from datetime import datetime, date

router = APIRouter(
    prefix="/partes-trabajo",
    tags=["partes_trabajo"]
)

@router.get("/", response_model=List[schemas.ParteTrabajoOut])
def get_partes_trabajo(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(1000, ge=1, le=10000, description="Número máximo de registros a retornar"),
    estado: Optional[int] = Query(None, description="Filtrar por estado numérico"),
    numero: Optional[int] = Query(None, description="Filtrar por número de parte"),
    cliente_empresa: Optional[str] = Query(None, description="Filtrar por empresa cliente"),
    fecha_desde: Optional[date] = Query(None, description="Fecha inicio del rango (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha fin del rango (YYYY-MM-DD)"),
    tecnico_email: Optional[str] = Query(None, description="Filtrar por email de técnico"),
    db: Session = Depends(get_db)
):
    """Obtiene todas las órdenes de trabajo con filtros opcionales y paginación"""
    query = db.query(ParteTrabajo)
    
    # Aplicar filtros
    if estado is not None:
        query = query.filter(ParteTrabajo.estado == estado)
    if numero:
        query = query.filter(ParteTrabajo.numero == numero)
    if cliente_empresa:
        query = query.filter(ParteTrabajo.cliente_empresa.ilike(f"%{cliente_empresa}%"))
    if fecha_desde:
        query = query.filter(ParteTrabajo.fecha >= fecha_desde)
    if fecha_hasta:
        # Agregar un día completo para incluir todo el día fecha_hasta
        fecha_hasta_completa = datetime.combine(fecha_hasta, datetime.max.time())
        query = query.filter(ParteTrabajo.fecha <= fecha_hasta_completa)
    
    # Filtrar por técnico si se especifica
    if tecnico_email:
        query = query.join(ParteTrabajo.tecnicos).filter(Tecnico.email == tecnico_email)
    
    return query.order_by(ParteTrabajo.fecha.desc()).offset(skip).limit(limit).all()

@router.get("/con-productos/", response_model=List[schemas.ParteTrabajoConProductosOut])
def get_partes_trabajo_con_productos(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(1000, ge=1, le=10000, description="Número máximo de registros a retornar"),
    estado: Optional[int] = Query(None, description="Filtrar por estado numérico"),
    numero: Optional[int] = Query(None, description="Filtrar por número de parte"),
    cliente_empresa: Optional[str] = Query(None, description="Filtrar por empresa cliente"),
    fecha_desde: Optional[date] = Query(None, description="Fecha inicio del rango (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha fin del rango (YYYY-MM-DD)"),
    tecnico_email: Optional[str] = Query(None, description="Filtrar por email de técnico"),
    db: Session = Depends(get_db)
):
    """Obtiene todas las órdenes de trabajo con información de productos utilizados"""
    query = db.query(ParteTrabajo)
    
    # Aplicar filtros (mismos que el endpoint original)
    if estado is not None:
        query = query.filter(ParteTrabajo.estado == estado)
    if numero:
        query = query.filter(ParteTrabajo.numero == numero)
    if cliente_empresa:
        query = query.filter(ParteTrabajo.cliente_empresa.ilike(f"%{cliente_empresa}%"))
    if fecha_desde:
        query = query.filter(ParteTrabajo.fecha >= fecha_desde)
    if fecha_hasta:
        # Agregar un día completo para incluir todo el día fecha_hasta
        fecha_hasta_completa = datetime.combine(fecha_hasta, datetime.max.time())
        query = query.filter(ParteTrabajo.fecha <= fecha_hasta_completa)
    
    # Filtrar por técnico si se especifica
    if tecnico_email:
        query = query.join(ParteTrabajo.tecnicos).filter(Tecnico.email == tecnico_email)
    
    partes = query.order_by(ParteTrabajo.fecha.desc()).offset(skip).limit(limit).all()
    
    # Enriquecer cada parte con información de productos
    resultado = []
    for parte in partes:
        # Obtener productos utilizados en este parte
        movimientos = db.query(StockMovimiento)\
            .filter(StockMovimiento.parte_trabajo_id == parte.id)\
            .join(Producto)\
            .all()
        
        # Contar productos únicos
        productos_ids = set()
        productos_nombres = []
        for mov in movimientos:
            if mov.producto_id not in productos_ids:
                productos_ids.add(mov.producto_id)
                productos_nombres.append(mov.producto.nombre)
        
        # Crear resumen de productos (máximo 3)
        productos_resumen = ""
        if productos_nombres:
            if len(productos_nombres) <= 3:
                productos_resumen = ", ".join(productos_nombres)
            else:
                productos_resumen = f"{', '.join(productos_nombres[:3])} y {len(productos_nombres) - 3} más"
        
        # Crear objeto resultado
        parte_dict = {
            **parte.__dict__,
            "productos_utilizados": len(productos_ids),
            "productos_resumen": productos_resumen
        }
        
        resultado.append(parte_dict)
    
    return resultado

@router.get("/{parte_id}", response_model=schemas.ParteTrabajoOut)
def get_parte_trabajo(parte_id: int, db: Session = Depends(get_db)):
    """Obtiene una orden de trabajo específica por ID"""
    parte = db.query(ParteTrabajo).filter(ParteTrabajo.id == parte_id).first()
    if not parte:
        raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada")
    return parte

@router.post("/", response_model=schemas.ParteTrabajoOut)
def create_parte_trabajo(parte: schemas.ParteTrabajoCreate, db: Session = Depends(get_db)):
    """Crea una nueva orden de trabajo con múltiples técnicos"""
    # Crear el parte de trabajo
    parte_data = parte.dict(exclude={'tecnico_ids'})
    db_parte = ParteTrabajo(**parte_data)
    
    # Agregar técnicos si se especificaron
    if parte.tecnico_ids:
        tecnicos = db.query(Tecnico).filter(Tecnico.id.in_(parte.tecnico_ids)).all()
        if len(tecnicos) != len(parte.tecnico_ids):
            raise HTTPException(status_code=400, detail="Algunos técnicos no fueron encontrados")
        db_parte.tecnicos = tecnicos
    
    db.add(db_parte)
    db.commit()
    db.refresh(db_parte)
    return db_parte

@router.put("/{parte_id}", response_model=schemas.ParteTrabajoOut)
def update_parte_trabajo(parte_id: int, parte_update: schemas.ParteTrabajoCreate, db: Session = Depends(get_db)):
    """Actualiza una orden de trabajo existente"""
    db_parte = db.query(ParteTrabajo).filter(ParteTrabajo.id == parte_id).first()
    if not db_parte:
        raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada")
    
    # Actualizar campos básicos
    parte_data = parte_update.dict(exclude={'tecnico_ids'})
    for field, value in parte_data.items():
        if value is not None:
            setattr(db_parte, field, value)
    
    # Actualizar técnicos si se especificaron
    if parte_update.tecnico_ids is not None:
        tecnicos = db.query(Tecnico).filter(Tecnico.id.in_(parte_update.tecnico_ids)).all()
        if len(tecnicos) != len(parte_update.tecnico_ids):
            raise HTTPException(status_code=400, detail="Algunos técnicos no fueron encontrados")
        db_parte.tecnicos = tecnicos
    
    db.commit()
    db.refresh(db_parte)
    return db_parte

@router.delete("/{parte_id}")
def delete_parte_trabajo(parte_id: int, db: Session = Depends(get_db)):
    """Elimina una orden de trabajo"""
    db_parte = db.query(ParteTrabajo).filter(ParteTrabajo.id == parte_id).first()
    if not db_parte:
        raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada")
    
    db.delete(db_parte)
    db.commit()
    return {"message": "Orden de trabajo eliminada exitosamente"}

@router.get("/stats/resumen")
def get_estadisticas_partes(db: Session = Depends(get_db)):
    """Obtiene estadísticas resumidas de las órdenes de trabajo"""
    total = db.query(ParteTrabajo).count()
    pendientes = db.query(ParteTrabajo).filter(ParteTrabajo.estado == "pendiente").count()
    en_proceso = db.query(ParteTrabajo).filter(ParteTrabajo.estado == "en_proceso").count()
    finalizados = db.query(ParteTrabajo).filter(ParteTrabajo.estado == "finalizado").count()
    
    # Estadísticas adicionales
    partes_por_tecnico = db.query(
        Tecnico.nombre,
        Tecnico.apellido,
        func.count(ParteTrabajo.id).label("total_partes")
    ).join(ParteTrabajo).group_by(Tecnico.id, Tecnico.nombre, Tecnico.apellido).all()
    
    return {
        "totales": {
            "total": total,
            "pendientes": pendientes,
            "en_proceso": en_proceso,
            "finalizados": finalizados
        },
        "por_tecnico": [
            {
                "tecnico": f"{pt.nombre} {pt.apellido}",
                "total_partes": pt.total_partes
            } for pt in partes_por_tecnico
        ]
    }

@router.get("/buscar/")
def buscar_partes_trabajo(
    q: str = Query(..., description="Término de búsqueda"),
    limit: int = Query(500, ge=1, le=5000, description="Número máximo de resultados"),
    db: Session = Depends(get_db)
):
    """Busca órdenes de trabajo por varios campos"""
    search_term = f"%{q}%"
    
    partes = db.query(ParteTrabajo).join(ParteTrabajo.tecnicos).filter(
        or_(
            ParteTrabajo.id_parte_api.ilike(search_term),
            ParteTrabajo.cliente_empresa.ilike(search_term),
            ParteTrabajo.cliente_id.ilike(search_term),
            ParteTrabajo.trabajo_solicitado.ilike(search_term),
            ParteTrabajo.numero.ilike(search_term),
            func.concat(Tecnico.nombre, " ", Tecnico.apellido).ilike(search_term)
        )
    ).order_by(ParteTrabajo.fecha.desc()).limit(limit).all()
    
    return [schemas.ParteTrabajoOut.from_orm(parte) for parte in partes]

@router.patch("/{parte_id}/estado")
def cambiar_estado_parte(
    parte_id: int, 
    nuevo_estado: str = Query(..., regex="^(pendiente|en_proceso|finalizado)$"),
    db: Session = Depends(get_db)
):
    """Cambia el estado de una orden de trabajo"""
    db_parte = db.query(ParteTrabajo).filter(ParteTrabajo.id == parte_id).first()
    if not db_parte:
        raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada")
    
    estado_anterior = db_parte.estado
    db_parte.estado = nuevo_estado
    
    # Si se marca como finalizado y no tiene fecha_fin, asignar fecha actual
    if nuevo_estado == "finalizado" and not db_parte.fecha_fin:
        db_parte.fecha_fin = datetime.now()
    
    db.commit()
    db.refresh(db_parte)
    
    return {
        "message": f"Estado cambiado de '{estado_anterior}' a '{nuevo_estado}'",
        "parte": schemas.ParteTrabajoOut.from_orm(db_parte)
    }

@router.post("/{parte_id}/tecnicos/{tecnico_id}")
def asignar_tecnico(
    parte_id: int,
    tecnico_id: int,
    db: Session = Depends(get_db)
):
    """Asigna un técnico a una orden de trabajo"""
    # Verificar que existe el parte
    db_parte = db.query(ParteTrabajo).filter(ParteTrabajo.id == parte_id).first()
    if not db_parte:
        raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada")
    
    # Verificar que existe el técnico
    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    
    # Verificar si ya está asignado
    if tecnico in db_parte.tecnicos:
        raise HTTPException(status_code=400, detail="Técnico ya está asignado a este parte")
    
    # Asignar técnico
    db_parte.tecnicos.append(tecnico)
    db.commit()
    
    return {
        "mensaje": f"Técnico {tecnico.nombre} {tecnico.apellido} asignado al parte {db_parte.numero}",
        "parte_id": parte_id,
        "tecnico_id": tecnico_id
    }

@router.delete("/{parte_id}/tecnicos/{tecnico_id}")
def desasignar_tecnico(
    parte_id: int,
    tecnico_id: int,
    db: Session = Depends(get_db)
):
    """Desasigna un técnico de una orden de trabajo"""
    # Verificar que existe el parte
    db_parte = db.query(ParteTrabajo).filter(ParteTrabajo.id == parte_id).first()
    if not db_parte:
        raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada")
    
    # Verificar que existe el técnico
    tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    
    # Verificar si está asignado
    if tecnico not in db_parte.tecnicos:
        raise HTTPException(status_code=400, detail="Técnico no está asignado a este parte")
    
    # Desasignar técnico
    db_parte.tecnicos.remove(tecnico)
    db.commit()
    
    return {
        "mensaje": f"Técnico {tecnico.nombre} {tecnico.apellido} desasignado del parte {db_parte.numero}",
        "parte_id": parte_id,
        "tecnico_id": tecnico_id
    }

@router.get("/{parte_id}/productos", response_model=List[schemas.ProductoParteTrabajoOut])
def get_productos_parte_trabajo(
    parte_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene todos los productos utilizados en una orden de trabajo específica"""
    # Verificar que existe el parte
    db_parte = db.query(ParteTrabajo).filter(ParteTrabajo.id == parte_id).first()
    if not db_parte:
        raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada")
    
    # Obtener movimientos de stock asociados a este parte de trabajo
    movimientos = db.query(StockMovimiento)\
        .filter(StockMovimiento.parte_trabajo_id == parte_id)\
        .join(Producto)\
        .all()
    
    if not movimientos:
        return []
    
    # Agrupar movimientos por producto
    productos_utilizados = {}
    for mov in movimientos:
        producto_id = mov.producto_id
        
        if producto_id not in productos_utilizados:
            productos_utilizados[producto_id] = {
                "producto": mov.producto,
                "cantidad_total": 0,
                "movimientos": []
            }
        
        # Calcular cantidad según tipo de movimiento
        cantidad = mov.cantidad if mov.tipo == "egreso" else -mov.cantidad
        productos_utilizados[producto_id]["cantidad_total"] += cantidad
        
        productos_utilizados[producto_id]["movimientos"].append({
            "id": mov.id,
            "cantidad": mov.cantidad,
            "tipo": mov.tipo,
            "motivo": mov.motivo,
            "fecha": mov.fecha,
            "deposito_id": mov.deposito_id
        })
    
    return list(productos_utilizados.values())
