from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from database import get_db
from models import ParteTrabajo, Tecnico
import schemas
from datetime import datetime, date

router = APIRouter(
    prefix="/partes-trabajo",
    tags=["partes_trabajo"]
)

@router.get("/", response_model=List[schemas.ParteTrabajoOut])
def get_partes_trabajo(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    estado: Optional[str] = Query(None, description="Filtrar por estado: pendiente, en_proceso, finalizado"),
    tecnico_id: Optional[int] = Query(None, description="Filtrar por ID de técnico"),
    cliente_empresa: Optional[str] = Query(None, description="Filtrar por empresa cliente"),
    fecha_desde: Optional[date] = Query(None, description="Fecha inicio del rango (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha fin del rango (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Obtiene todas las órdenes de trabajo con filtros opcionales y paginación"""
    query = db.query(ParteTrabajo)
    
    # Aplicar filtros
    if estado:
        query = query.filter(ParteTrabajo.estado == estado)
    if tecnico_id:
        query = query.filter(ParteTrabajo.tecnico_id == tecnico_id)
    if cliente_empresa:
        query = query.filter(ParteTrabajo.cliente_empresa.ilike(f"%{cliente_empresa}%"))
    if fecha_desde:
        query = query.filter(ParteTrabajo.fecha_inicio >= fecha_desde)
    if fecha_hasta:
        # Agregar un día completo para incluir todo el día fecha_hasta
        fecha_hasta_completa = datetime.combine(fecha_hasta, datetime.max.time())
        query = query.filter(ParteTrabajo.fecha_inicio <= fecha_hasta_completa)
    
    return query.order_by(ParteTrabajo.fecha_inicio.desc()).offset(skip).limit(limit).all()

@router.get("/{parte_id}", response_model=schemas.ParteTrabajoOut)
def get_parte_trabajo(parte_id: int, db: Session = Depends(get_db)):
    """Obtiene una orden de trabajo específica por ID"""
    parte = db.query(ParteTrabajo).filter(ParteTrabajo.id == parte_id).first()
    if not parte:
        raise HTTPException(status_code=404, detail="Orden de trabajo no encontrada")
    return parte

@router.post("/", response_model=schemas.ParteTrabajoOut)
def create_parte_trabajo(parte: schemas.ParteTrabajoCreate, db: Session = Depends(get_db)):
    """Crea una nueva orden de trabajo"""
    # Verificar que el técnico exists
    tecnico = db.query(Tecnico).filter(Tecnico.id == parte.tecnico_id).first()
    if not tecnico:
        raise HTTPException(status_code=400, detail="Técnico no encontrado")
    
    db_parte = ParteTrabajo(**parte.dict())
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
    
    # Verificar que el técnico exists si se está actualizando
    if parte_update.tecnico_id:
        tecnico = db.query(Tecnico).filter(Tecnico.id == parte_update.tecnico_id).first()
        if not tecnico:
            raise HTTPException(status_code=400, detail="Técnico no encontrado")
    
    # Actualizar campos
    for field, value in parte_update.dict().items():
        setattr(db_parte, field, value)
    
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
    db: Session = Depends(get_db)
):
    """Busca órdenes de trabajo por varios campos"""
    search_term = f"%{q}%"
    
    partes = db.query(ParteTrabajo).join(Tecnico).filter(
        or_(
            ParteTrabajo.id_parte_api.ilike(search_term),
            ParteTrabajo.cliente_empresa.ilike(search_term),
            ParteTrabajo.cliente_id.ilike(search_term),
            ParteTrabajo.descripcion.ilike(search_term),
            func.concat(Tecnico.nombre, " ", Tecnico.apellido).ilike(search_term)
        )
    ).order_by(ParteTrabajo.fecha_inicio.desc()).limit(50).all()
    
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
