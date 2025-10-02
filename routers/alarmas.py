"""
Router para endpoints de alarmas de vessels
Maneja las consultas sobre el estado de recepción de datos de los vessels
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_mysql_db
from schemas import ListaAlarmas, AlarmaVessel
from servicios.alarmas_service import AlarmasService

router = APIRouter()

@router.get("/alarmas", response_model=ListaAlarmas)
async def obtener_todas_las_alarmas(
    db: Session = Depends(get_mysql_db)
):
    """
    Obtiene el estado de alarmas para todos los vessels.
    
    Retorna información sobre el último dato recibido de cada vessel
    y el estado de alarma correspondiente:
    - Verde: < 2 horas sin datos
    - Amarillo: 2-8 horas sin datos  
    - Naranja: 8-12 horas sin datos
    - Rojo: > 12 horas sin datos
    """
    try:
        alarmas = AlarmasService.calcular_alarmas_vessels(db)
        return alarmas
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener las alarmas: {str(e)}"
        )

@router.get("/alarmas/criticos", response_model=List[AlarmaVessel])
async def obtener_alarmas_criticas(
    horas: Optional[float] = Query(default=12.0, description="Número de horas para considerar crítico"),
    db: Session = Depends(get_mysql_db)
):
    """
    Obtiene solo los vessels en estado crítico (más de X horas sin datos).
    
    Args:
        horas: Número de horas sin datos para considerar crítico (default: 12)
    
    Returns:
        Lista de vessels que superan el umbral crítico especificado
    """
    try:
        vessels_criticos = AlarmasService.obtener_vessels_criticos(db, horas)
        return vessels_criticos
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener vessels críticos: {str(e)}"
        )

@router.get("/alarmas/resumen")
async def obtener_resumen_alarmas(
    db: Session = Depends(get_mysql_db)
):
    """
    Obtiene un resumen estadístico del estado de las alarmas.
    
    Returns:
        Diccionario con conteo por estado y porcentajes
    """
    try:
        alarmas = AlarmasService.calcular_alarmas_vessels(db)
        total = alarmas.total_vessels
        
        resumen_detallado = {
            "total_vessels": total,
            "conteo_por_estado": alarmas.resumen,
            "porcentajes": {
                estado: round((count / total * 100), 1) if total > 0 else 0
                for estado, count in alarmas.resumen.items()
            },
            "vessels_operativos": alarmas.resumen["verde"],
            "vessels_con_problemas": total - alarmas.resumen["verde"]
        }
        
        return resumen_detallado
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener resumen de alarmas: {str(e)}"
        )

@router.get("/alarmas/vessel/{vessel_name}", response_model=AlarmaVessel)
async def obtener_alarma_vessel_especifico(
    vessel_name: str,
    db: Session = Depends(get_mysql_db)
):
    """
    Obtiene el estado de alarma para un vessel específico.
    
    Args:
        vessel_name: Nombre del vessel a consultar
        
    Returns:
        Estado de alarma del vessel especificado
    """
    try:
        todas_alarmas = AlarmasService.calcular_alarmas_vessels(db)
        
        # Buscar el vessel específico
        alarma_vessel = None
        for alarma in todas_alarmas.alarmas:
            if alarma.vessel_name.lower() == vessel_name.lower():
                alarma_vessel = alarma
                break
        
        if not alarma_vessel:
            raise HTTPException(
                status_code=404,
                detail=f"Vessel '{vessel_name}' no encontrado"
            )
            
        return alarma_vessel
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error al obtener alarma del vessel: {str(e)}"
        )