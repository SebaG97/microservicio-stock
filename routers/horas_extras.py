from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Tecnico, Feriado, ParteTrabajo, HorasExtras
import schemas
from datetime import datetime, date, time, timedelta
import calendar

router = APIRouter(
    prefix="/horas-extras",
    tags=["horas_extras"]
)

# Funciones auxiliares para cálculo de horas
def es_feriado(fecha: date, db: Session) -> bool:
    """Verifica si una fecha es feriado"""
    return db.query(Feriado).filter(Feriado.fecha == fecha).first() is not None

def tipo_dia(fecha: date, db: Session) -> str:
    """Determina el tipo de día: laboral, sabado, domingo, feriado"""
    if es_feriado(fecha, db):
        return "feriado"
    dia_semana = fecha.weekday()  # 0=lunes, 6=domingo
    if dia_semana == 6:  # domingo
        return "domingo"
    elif dia_semana == 5:  # sábado
        return "sabado"
    else:  # lunes a viernes
        return "laboral"

def calcular_horas_extras(fecha_inicio: datetime, fecha_fin: datetime, db: Session) -> dict:
    """
    Calcula las horas extras basado en las reglas:
    - Horario normal: Lunes a viernes 8-17hs, Sábados 8-12hs
    - Horas extras: Todo fuera de esos rangos
    - Horas extras especiales (dobles): Domingos, feriados y horario nocturno (20-6hs)
    """
    fecha = fecha_inicio.date()
    hora_inicio = fecha_inicio.time()
    hora_fin = fecha_fin.time()
    
    tipo_dia_actual = tipo_dia(fecha, db)
    
    # Definir horarios normales
    if tipo_dia_actual == "laboral":  # lunes a viernes
        horario_normal_inicio = time(8, 0)
        horario_normal_fin = time(17, 0)
    elif tipo_dia_actual == "sabado":
        horario_normal_inicio = time(8, 0)
        horario_normal_fin = time(12, 0)
    else:  # domingo o feriado
        horario_normal_inicio = None
        horario_normal_fin = None
    
    # Horario nocturno (20:00 - 6:00)
    horario_nocturno_inicio = time(20, 0)
    horario_nocturno_fin = time(6, 0)
    
    # Convertir a minutos para facilitar cálculos
    def time_to_minutes(t):
        return t.hour * 60 + t.minute
    
    inicio_min = time_to_minutes(hora_inicio)
    fin_min = time_to_minutes(hora_fin)
    
    # Si el trabajo cruza medianoche, ajustar
    if fin_min < inicio_min:
        fin_min += 24 * 60
    
    total_minutos = fin_min - inicio_min
    horas_normales = 0
    horas_extras_normales = 0
    horas_extras_especiales = 0
    
    if tipo_dia_actual in ["domingo", "feriado"]:
        # Todo es hora extra especial en domingos y feriados
        horas_extras_especiales = total_minutos / 60
    else:
        # Calcular intersecciones con horarios
        if horario_normal_inicio and horario_normal_fin:
            normal_inicio_min = time_to_minutes(horario_normal_inicio)
            normal_fin_min = time_to_minutes(horario_normal_fin)
            
            # Calcular horas normales
            overlap_inicio = max(inicio_min, normal_inicio_min)
            overlap_fin = min(fin_min, normal_fin_min)
            if overlap_fin > overlap_inicio:
                horas_normales = (overlap_fin - overlap_inicio) / 60
            
            # El resto son horas extras normales
            horas_extras_normales = (total_minutos / 60) - horas_normales
        else:
            # Sin horario normal, todo es extra
            horas_extras_normales = total_minutos / 60
        
        # Verificar horario nocturno para horas especiales
        nocturno_inicio_min = time_to_minutes(horario_nocturno_inicio)
        nocturno_fin_min = time_to_minutes(horario_nocturno_fin) + 24 * 60  # ajustar para cruce de medianoche
        
        # Calcular intersección con horario nocturno
        noche_overlap_inicio = max(inicio_min, nocturno_inicio_min)
        noche_overlap_fin = min(fin_min, nocturno_fin_min)
        
        # También verificar horario nocturno antes de las 6 AM
        if hora_inicio <= horario_nocturno_fin:
            madrugada_inicio = inicio_min
            madrugada_fin = min(fin_min, time_to_minutes(horario_nocturno_fin))
            if madrugada_fin > madrugada_inicio:
                horas_nocturnas_madrugada = (madrugada_fin - madrugada_inicio) / 60
                horas_extras_especiales += horas_nocturnas_madrugada
                horas_extras_normales -= horas_nocturnas_madrugada
        
        # Horario nocturno después de las 20:00
        if hora_fin >= horario_nocturno_inicio:
            noche_inicio = max(inicio_min, time_to_minutes(horario_nocturno_inicio))
            noche_fin = fin_min
            if noche_fin > noche_inicio:
                horas_nocturnas_noche = (noche_fin - noche_inicio) / 60
                horas_extras_especiales += horas_nocturnas_noche
                horas_extras_normales -= horas_nocturnas_noche
    
    # Asegurar que no haya valores negativos
    horas_normales = max(0, horas_normales)
    horas_extras_normales = max(0, horas_extras_normales)
    horas_extras_especiales = max(0, horas_extras_especiales)
    
    return {
        "horas_normales": round(horas_normales, 2),
        "horas_extras_normales": round(horas_extras_normales, 2),
        "horas_extras_especiales": round(horas_extras_especiales, 2),
        "tipo_dia": tipo_dia_actual
    }

# Endpoints CRUD para técnicos
@router.get("/tecnicos/", response_model=List[schemas.TecnicoOut])
def get_tecnicos(db: Session = Depends(get_db)):
    return db.query(Tecnico).filter(Tecnico.activo == True).all()

@router.post("/tecnicos/", response_model=schemas.TecnicoOut)
def create_tecnico(tecnico: schemas.TecnicoCreate, db: Session = Depends(get_db)):
    db_tecnico = Tecnico(**tecnico.dict())
    db.add(db_tecnico)
    db.commit()
    db.refresh(db_tecnico)
    return db_tecnico

@router.put("/tecnicos/{tecnico_id}", response_model=schemas.TecnicoOut)
def update_tecnico(tecnico_id: int, tecnico: schemas.TecnicoCreate, db: Session = Depends(get_db)):
    db_tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()
    if not db_tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    for key, value in tecnico.dict().items():
        setattr(db_tecnico, key, value)
    db.commit()
    db.refresh(db_tecnico)
    return db_tecnico

# Endpoints CRUD para feriados
@router.get("/feriados/", response_model=List[schemas.FeriadoOut])
def get_feriados(db: Session = Depends(get_db)):
    return db.query(Feriado).order_by(Feriado.fecha).all()

@router.post("/feriados/", response_model=schemas.FeriadoOut)
def create_feriado(feriado: schemas.FeriadoCreate, db: Session = Depends(get_db)):
    db_feriado = Feriado(**feriado.dict())
    db.add(db_feriado)
    db.commit()
    db.refresh(db_feriado)
    return db_feriado

# Endpoints CRUD para partes de trabajo
@router.get("/partes-trabajo/", response_model=List[schemas.ParteTrabajoOut])
def get_partes_trabajo(db: Session = Depends(get_db)):
    return db.query(ParteTrabajo).order_by(ParteTrabajo.fecha_inicio.desc()).all()

@router.post("/partes-trabajo/", response_model=schemas.ParteTrabajoOut)
def create_parte_trabajo(parte: schemas.ParteTrabajoCreate, db: Session = Depends(get_db)):
    db_parte = ParteTrabajo(**parte.dict())
    db.add(db_parte)
    db.commit()
    db.refresh(db_parte)
    return db_parte

# Endpoint para calcular horas extras automáticamente
@router.post("/calcular-horas/{parte_trabajo_id}")
def calcular_horas_parte(parte_trabajo_id: int, db: Session = Depends(get_db)):
    """Calcula y guarda las horas extras para un parte de trabajo específico"""
    parte = db.query(ParteTrabajo).filter(ParteTrabajo.id == parte_trabajo_id).first()
    if not parte:
        raise HTTPException(status_code=404, detail="Parte de trabajo no encontrado")
    
    if not parte.fecha_fin:
        raise HTTPException(status_code=400, detail="Parte de trabajo sin fecha de finalización")
    
    # Verificar si ya existe cálculo para este parte
    horas_existente = db.query(HorasExtras).filter(HorasExtras.parte_trabajo_id == parte_trabajo_id).first()
    if horas_existente:
        db.delete(horas_existente)
    
    # Calcular horas
    calculo = calcular_horas_extras(parte.fecha_inicio, parte.fecha_fin, db)
    
    # Crear registro de horas extras
    db_horas = HorasExtras(
        parte_trabajo_id=parte_trabajo_id,
        tecnico_id=parte.tecnico_id,
        fecha=parte.fecha_inicio.date(),
        hora_inicio=parte.fecha_inicio.time(),
        hora_fin=parte.fecha_fin.time(),
        horas_normales=calculo["horas_normales"],
        horas_extras_normales=calculo["horas_extras_normales"],
        horas_extras_especiales=calculo["horas_extras_especiales"],
        tipo_dia=calculo["tipo_dia"],
        calculado_automaticamente=True
    )
    
    db.add(db_horas)
    db.commit()
    db.refresh(db_horas)
    
    return {
        "mensaje": "Horas extras calculadas correctamente",
        "calculo": calculo,
        "horas_extras_id": db_horas.id
    }

# Endpoint principal: Reporte de horas extras
@router.get("/reporte/", response_model=schemas.HorasExtrasReporte)
def get_reporte_horas_extras(
    fecha_inicio: date = Query(..., description="Fecha inicio del período"),
    fecha_fin: date = Query(..., description="Fecha fin del período"),
    tecnico_id: Optional[int] = Query(None, description="ID del técnico (opcional)"),
    db: Session = Depends(get_db)
):
    """
    Genera reporte de horas extras por técnico en un período determinado
    """
    query = db.query(HorasExtras).filter(
        HorasExtras.fecha >= fecha_inicio,
        HorasExtras.fecha <= fecha_fin
    )
    
    if tecnico_id:
        query = query.filter(HorasExtras.tecnico_id == tecnico_id)
    
    horas_extras = query.all()
    
    # Agrupar por técnico
    tecnicos_resumen = {}
    for hora in horas_extras:
        tecnico_id = hora.tecnico_id
        if tecnico_id not in tecnicos_resumen:
            tecnicos_resumen[tecnico_id] = {
                "tecnico": hora.tecnico,
                "total_horas_extras_normales": 0,
                "total_horas_extras_especiales": 0,
                "total_horas_trabajadas": 0,
                "partes_trabajados": set()
            }
        
        tecnicos_resumen[tecnico_id]["total_horas_extras_normales"] += hora.horas_extras_normales
        tecnicos_resumen[tecnico_id]["total_horas_extras_especiales"] += hora.horas_extras_especiales
        tecnicos_resumen[tecnico_id]["total_horas_trabajadas"] += (
            hora.horas_normales + hora.horas_extras_normales + hora.horas_extras_especiales
        )
        tecnicos_resumen[tecnico_id]["partes_trabajados"].add(hora.parte_trabajo_id)
    
    # Convertir a formato de respuesta
    resumen = []
    for tecnico_id, datos in tecnicos_resumen.items():
        resumen.append(schemas.HorasExtrasResumen(
            tecnico_id=tecnico_id,
            tecnico_nombre=datos["tecnico"].nombre,
            tecnico_apellido=datos["tecnico"].apellido,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            total_horas_extras_normales=round(datos["total_horas_extras_normales"], 2),
            total_horas_extras_especiales=round(datos["total_horas_extras_especiales"], 2),
            total_horas_trabajadas=round(datos["total_horas_trabajadas"], 2),
            partes_trabajados=len(datos["partes_trabajados"])
        ))
    
    return schemas.HorasExtrasReporte(
        resumen=resumen,
        periodo_inicio=fecha_inicio,
        periodo_fin=fecha_fin,
        total_tecnicos=len(resumen)
    )

# Endpoint para obtener horas extras de un técnico específico
@router.get("/detalle/{tecnico_id}", response_model=List[schemas.HorasExtrasOut])
def get_horas_extras_tecnico(
    tecnico_id: int,
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    db: Session = Depends(get_db)
):
    """Obtiene el detalle de horas extras de un técnico específico"""
    return db.query(HorasExtras).filter(
        HorasExtras.tecnico_id == tecnico_id,
        HorasExtras.fecha >= fecha_inicio,
        HorasExtras.fecha <= fecha_fin
    ).order_by(HorasExtras.fecha.desc()).all()

# Endpoint para obtener partes con horas extras de un técnico específico (para el frontend)
@router.get("/partes/{tecnico_id}/")
def get_partes_con_horas_extras(
    tecnico_id: int,
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    db: Session = Depends(get_db)
):
    """Obtiene los partes de trabajo con horas extras de un técnico específico"""
    
    # Obtener horas extras del técnico en el rango de fechas
    horas_extras = db.query(HorasExtras).filter(
        HorasExtras.tecnico_id == tecnico_id,
        HorasExtras.fecha >= fecha_inicio,
        HorasExtras.fecha <= fecha_fin
    ).all()
    
    # Agrupar por parte de trabajo y preparar respuesta
    partes_detalle = []
    for hora in horas_extras:
        parte = hora.parte_trabajo
        if parte:
            partes_detalle.append({
                "id": parte.id,
                "id_parte_api": parte.id_parte_api,
                "fecha": hora.fecha.isoformat(),
                "hora_inicio": hora.hora_inicio.strftime("%H:%M"),
                "hora_fin": hora.hora_fin.strftime("%H:%M"),
                "descripcion": parte.descripcion or "Sin descripción",
                "cliente_empresa": parte.cliente_empresa or "Sin cliente",
                "horas_normales": hora.horas_normales,
                "horas_extras_normales": hora.horas_extras_normales,
                "horas_extras_especiales": hora.horas_extras_especiales,
                "tipo_dia": hora.tipo_dia,
                "calculado_automaticamente": hora.calculado_automaticamente
            })
    
    return partes_detalle

# Endpoint para sincronizar partes de trabajo desde API externa (MEJORADO)
@router.post("/sincronizar-partes-mejorado/")
def sincronizar_partes_trabajo_mejorado(db: Session = Depends(get_db)):
    """
    Sincroniza solo partes finalizadas desde la API externa y calcula horas extras automáticamente
    """
    from servicios.sincronizador_automatico import SincronizadorAutomatico
    
    sincronizador = SincronizadorAutomatico()
    try:
        resultado = sincronizador.sincronizar_partes_trabajo()
        return {
            "mensaje": "Sincronización completada exitosamente",
            "estadisticas": resultado
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en sincronización: {str(e)}")

# Endpoint original (mantener por compatibilidad)
@router.post("/sincronizar-partes/")
def sincronizar_partes_trabajo(db: Session = Depends(get_db)):
    """
    Sincroniza partes de trabajo desde la API externa y calcula horas extras automáticamente
    """
    import requests
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    API_URL = "https://api.partedetrabajo.com/v1/partes/"
    HEADERS = {"X-Auth-Partedetrabajo-Token": os.getenv("API_TOKEN")}
    
    try:
        response = requests.get(API_URL, headers=HEADERS)
        response.raise_for_status()
        partes = response.json().get("docs", [])
        
        nuevos_partes = 0
        horas_calculadas = 0
        
        for parte_data in partes:
            # Verificar si el parte ya existe
            parte_existente = db.query(ParteTrabajo).filter(
                ParteTrabajo.id_parte_api == parte_data["id"]
            ).first()
            
            if not parte_existente:
                # Buscar o crear técnico (asumiendo que viene en los datos)
                tecnico_info = parte_data.get("tecnico", {})
                if tecnico_info:
                    tecnico = db.query(Tecnico).filter(
                        Tecnico.legajo == tecnico_info.get("legajo", "")
                    ).first()
                    
                    if not tecnico and tecnico_info.get("nombre"):
                        # Crear técnico si no existe
                        tecnico = Tecnico(
                            nombre=tecnico_info.get("nombre", ""),
                            apellido=tecnico_info.get("apellido", ""),
                            legajo=tecnico_info.get("legajo", f"T{parte_data['id']}")
                        )
                        db.add(tecnico)
                        db.commit()
                        db.refresh(tecnico)
                    
                    if tecnico:
                        # Crear parte de trabajo
                        nuevo_parte = ParteTrabajo(
                            id_parte_api=parte_data["id"],
                            tecnico_id=tecnico.id,
                            cliente_id=parte_data.get("cliente_id"),
                            cliente_empresa=parte_data.get("cliente_empresa"),
                            fecha_inicio=datetime.fromisoformat(parte_data["fecha_inicio"]),
                            fecha_fin=datetime.fromisoformat(parte_data["fecha_fin"]) if parte_data.get("fecha_fin") else None,
                            descripcion=parte_data.get("descripcion", ""),
                            estado=parte_data.get("estado", "pendiente")
                        )
                        
                        db.add(nuevo_parte)
                        db.commit()
                        db.refresh(nuevo_parte)
                        nuevos_partes += 1
                        
                        # Calcular horas extras si tiene fecha fin
                        if nuevo_parte.fecha_fin:
                            try:
                                calculo = calcular_horas_extras(nuevo_parte.fecha_inicio, nuevo_parte.fecha_fin, db)
                                
                                db_horas = HorasExtras(
                                    parte_trabajo_id=nuevo_parte.id,
                                    tecnico_id=nuevo_parte.tecnico_id,
                                    fecha=nuevo_parte.fecha_inicio.date(),
                                    hora_inicio=nuevo_parte.fecha_inicio.time(),
                                    hora_fin=nuevo_parte.fecha_fin.time(),
                                    horas_normales=calculo["horas_normales"],
                                    horas_extras_normales=calculo["horas_extras_normales"],
                                    horas_extras_especiales=calculo["horas_extras_especiales"],
                                    tipo_dia=calculo["tipo_dia"],
                                    calculado_automaticamente=True
                                )
                                
                                db.add(db_horas)
                                horas_calculadas += 1
                            except Exception as e:
                                print(f"Error calculando horas para parte {nuevo_parte.id}: {e}")
        
        db.commit()
        
        return {
            "mensaje": "Sincronización completada",
            "nuevos_partes": nuevos_partes,
            "horas_calculadas": horas_calculadas
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en sincronización: {str(e)}")

# Endpoints para control de sincronización automática
@router.post("/sync/iniciar/")
def iniciar_sincronizacion_auto():
    """Inicia la sincronización automática cada 5 minutos"""
    from servicios.sincronizador_automatico import iniciar_sincronizacion_automatica
    iniciar_sincronizacion_automatica()
    return {"mensaje": "Sincronización automática iniciada", "intervalo": "5 minutos"}

@router.post("/sync/detener/")
def detener_sincronizacion_auto():
    """Detiene la sincronización automática"""
    from servicios.sincronizador_automatico import detener_sincronizacion_automatica
    detener_sincronizacion_automatica()
    return {"mensaje": "Sincronización automática detenida"}

@router.get("/sync/estado/")
def estado_sincronizacion():
    """Obtiene el estado de la sincronización automática"""
    from servicios.sincronizador_automatico import obtener_estado_sincronizacion
    return obtener_estado_sincronizacion()

@router.post("/sync/manual/")
def sincronizacion_manual():
    """Ejecuta una sincronización manual"""
    from servicios.sincronizador_automatico import sincronizador_global
    try:
        resultado = sincronizador_global.sincronizar_partes_trabajo()
        return {
            "mensaje": "Sincronización manual completada",
            "resultado": resultado
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en sincronización manual: {str(e)}")
