from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Tecnico, Feriado, ParteTrabajo, HorasExtras
import schemas
from datetime import datetime, date, time, timedelta
import calendar
import holidays

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

def es_horario_oficina(dt: datetime) -> bool:
    """Determina si una hora está dentro del horario de oficina"""
    hora = dt.time()
    dia_semana = dt.weekday()  # 0=lunes, 6=domingo
    
    if dia_semana < 5:  # Lunes a viernes
        return time(8, 0) <= hora <= time(17, 0)
    elif dia_semana == 5:  # Sábado
        return time(8, 0) <= hora <= time(12, 0)
    else:  # Domingo
        return False

def obtener_jornadas_laborales(fecha_inicio: datetime, fecha_fin: datetime) -> list:
    """
    Divide un período en jornadas laborales separadas
    Retorna lista de tuplas (inicio_jornada, fin_jornada, tipo_dia)
    """
    jornadas = []
    fecha_actual = fecha_inicio.date()
    fecha_limite = fecha_fin.date()
    
    while fecha_actual <= fecha_limite:
        dia_semana = fecha_actual.weekday()
        
        # Definir horarios de trabajo según el día
        if dia_semana < 5:  # Lunes a viernes
            inicio_trabajo = time(8, 0)
            fin_trabajo = time(17, 0)
            tipo_dia_jornada = "laboral"
        elif dia_semana == 5:  # Sábado
            inicio_trabajo = time(8, 0)
            fin_trabajo = time(12, 0)
            tipo_dia_jornada = "sabado"
        else:  # Domingo
            fecha_actual += timedelta(days=1)
            continue
        
        # Crear datetime para inicio y fin del día laboral
        inicio_dia = datetime.combine(fecha_actual, inicio_trabajo)
        fin_dia = datetime.combine(fecha_actual, fin_trabajo)
        
        # Ajustar según las fechas reales de la orden
        if fecha_actual == fecha_inicio.date():
            # Primer día: usar la hora de inicio real si es después del horario
            inicio_real = max(fecha_inicio, inicio_dia)
        else:
            inicio_real = inicio_dia
            
        if fecha_actual == fecha_fin.date():
            # Último día: usar la hora de fin real si es antes del horario
            fin_real = min(fecha_fin, fin_dia)
        else:
            fin_real = fin_dia
        
        # Solo agregar si hay trabajo en este día
        if inicio_real < fin_real:
            jornadas.append((inicio_real, fin_real, tipo_dia_jornada))
        
        fecha_actual += timedelta(days=1)
    
    return jornadas

def calcular_horas_extras(fecha_inicio: datetime, fecha_fin: datetime, db: Session) -> dict:
    """
    CÁLCULO INTELIGENTE DE HORAS - Versión 2.0
    
    Distingue entre:
    1. Trabajo en múltiples días laborales (horario normal de oficina)
    2. Trabajo nocturno real (fuera de horario)
    3. Fines de semana y feriados
    
    Reglas:
    - Horario normal: Lunes-Viernes 8-17h (8h), Sábados 8-12h (4h)
    - Horas extras normales: Exceso sobre horario normal en días laborales
    - Horas extras especiales: Domingos, feriados, horario nocturno (20-6h)
    """
    
    # Verificar si es una orden que cruza múltiples días
    es_multi_dia = fecha_inicio.date() != fecha_fin.date()
    
    if es_multi_dia:
        return calcular_horas_multi_dia(fecha_inicio, fecha_fin, db)
    else:
        return calcular_horas_mismo_dia(fecha_inicio, fecha_fin, db)

def es_trabajo_oficina_multidia(fecha_inicio: datetime, fecha_fin: datetime) -> bool:
    """
    Detecta automáticamente si una orden multi-día es trabajo de oficina normal
    vs trabajo nocturno/continuo real.
    
    ENFOQUE CORREGIDO:
    En lugar de analizar duración total continua, analiza si el patrón
    coincide con jornadas de oficina normales separadas.
    """
    
    # Criterio principal: ¿Podría ser trabajo de oficina normal?
    # Simulamos calcular solo las horas de oficina para ver si es razonable
    
    total_horas_oficina_posibles = 0
    fecha_actual = fecha_inicio.date()
    
    while fecha_actual <= fecha_fin.date():
        dia_semana = fecha_actual.weekday()
        
        # Horarios de oficina según día
        if dia_semana < 5:  # Lunes a viernes
            oficina_inicio = time(8, 0)
            oficina_fin = time(17, 0)
        elif dia_semana == 5:  # Sábado  
            oficina_inicio = time(8, 0)
            oficina_fin = time(12, 0)
        else:  # Domingo - saltar
            fecha_actual += timedelta(days=1)
            continue
        
        # Calcular intersección con horario de oficina este día
        dia_inicio = datetime.combine(fecha_actual, oficina_inicio)
        dia_fin = datetime.combine(fecha_actual, oficina_fin)
        
        # Ajustar según fechas reales de la orden
        trabajo_inicio = max(fecha_inicio if fecha_actual == fecha_inicio.date() else dia_inicio, dia_inicio)
        trabajo_fin = min(fecha_fin if fecha_actual == fecha_fin.date() else dia_fin, dia_fin)
        
        if trabajo_inicio < trabajo_fin:
            horas_oficina_dia = (trabajo_fin - trabajo_inicio).total_seconds() / 3600
            # Máximo 10h por día (8h normales + 2h extras)
            total_horas_oficina_posibles += min(horas_oficina_dia, 10)
        
        fecha_actual += timedelta(days=1)
    
    # Calcular duración total real
    duracion_total_real = (fecha_fin - fecha_inicio).total_seconds() / 3600
    
    # Criterios para determinar si es trabajo de oficina:
    
    # 1. La duración real no debe exceder mucho las horas de oficina posibles
    ratio_oficina = duracion_total_real / max(total_horas_oficina_posibles, 1)
    
    # 2. Análisis de horarios de inicio/fin
    hora_inicio = fecha_inicio.time()
    hora_fin = fecha_fin.time()
    
    # Horarios razonables para trabajo de oficina (6:00-20:00)
    inicio_razonable = time(6, 0) <= hora_inicio <= time(20, 0)
    fin_razonable = time(6, 0) <= hora_fin <= time(20, 0)
    
    # 3. No debe terminar en horario nocturno claro (22:00-05:00)
    horario_nocturno_claro = (time(22, 0) <= hora_fin or hora_fin <= time(5, 0))
    
    # Es trabajo de oficina si:
    # - El ratio es razonable (no más del 150% de horas de oficina)
    # - Los horarios son razonables 
    # - No termina en horario nocturno claro
    es_oficina = (ratio_oficina <= 1.5 and 
                  inicio_razonable and 
                  fin_razonable and 
                  not horario_nocturno_claro)
    
    return es_oficina

def calcular_horas_multi_dia(fecha_inicio: datetime, fecha_fin: datetime, db: Session) -> dict:
    """
    Calcula horas para órdenes que abarcan múltiples días
    INTELIGENTE: Detecta automáticamente trabajo de oficina vs nocturno
    """
    
    # Detectar si es trabajo de oficina multi-día
    es_oficina_multidia = es_trabajo_oficina_multidia(fecha_inicio, fecha_fin)
    
    if es_oficina_multidia:
        return calcular_trabajo_oficina_multidia(fecha_inicio, fecha_fin, db)
    else:
        return calcular_trabajo_continuo_multidia(fecha_inicio, fecha_fin, db)

def calcular_trabajo_oficina_multidia(fecha_inicio: datetime, fecha_fin: datetime, db: Session) -> dict:
    """
    Calcula horas para trabajo de oficina que abarca múltiples días
    Solo cuenta las horas dentro del horario de oficina de cada día
    """
    
    total_normales = 0
    total_extras_normales = 0  
    total_extras_especiales = 0
    
    fecha_actual = fecha_inicio.date()
    
    while fecha_actual <= fecha_fin.date():
        dia_semana = fecha_actual.weekday()
        
        # Definir horario de oficina según el día
        if dia_semana < 5:  # Lunes a viernes
            oficina_inicio = time(8, 0)
            oficina_fin = time(17, 0)
            horas_normales_max = 8
        elif dia_semana == 5:  # Sábado
            oficina_inicio = time(8, 0)
            oficina_fin = time(12, 0)
            horas_normales_max = 4
        else:  # Domingo - saltar
            fecha_actual += timedelta(days=1)
            continue
        
        # Verificar si es feriado
        if es_feriado(fecha_actual, db):
            fecha_actual += timedelta(days=1)
            continue
        
        # Calcular intersección con el horario de oficina
        dia_inicio = datetime.combine(fecha_actual, oficina_inicio)
        dia_fin = datetime.combine(fecha_actual, oficina_fin)
        
        # Ajustar según las fechas reales de la orden
        trabajo_inicio = max(fecha_inicio if fecha_actual == fecha_inicio.date() else dia_inicio, dia_inicio)
        trabajo_fin = min(fecha_fin if fecha_actual == fecha_fin.date() else dia_fin, dia_fin)
        
        # Calcular horas trabajadas en oficina este día
        if trabajo_inicio < trabajo_fin:
            horas_dia = (trabajo_fin - trabajo_inicio).total_seconds() / 3600
            
            if horas_dia <= horas_normales_max:
                total_normales += horas_dia
            else:
                total_normales += horas_normales_max
                total_extras_normales += (horas_dia - horas_normales_max)
        
        fecha_actual += timedelta(days=1)
    
    return {
        "horas_normales": round(total_normales, 2),
        "horas_extras_normales": round(total_extras_normales, 2),
        "horas_extras_especiales": round(total_extras_especiales, 2),
        "tipo_dia": "oficina_multidia"
    }

def calcular_trabajo_continuo_multidia(fecha_inicio: datetime, fecha_fin: datetime, db: Session) -> dict:
    """
    Calcula horas para trabajo continuo/nocturno que abarca múltiples días
    Usa la lógica día por día para detectar trabajo nocturno real
    """
    
    total_normales = 0
    total_extras_normales = 0  
    total_extras_especiales = 0
    
    # Procesar cada día individualmente
    fecha_actual = fecha_inicio
    
    while fecha_actual.date() <= fecha_fin.date():
        # Determinar inicio y fin para este día específico
        if fecha_actual.date() == fecha_inicio.date():
            inicio_dia = fecha_actual
        else:
            inicio_dia = datetime.combine(fecha_actual.date(), time(0, 0))
        
        if fecha_actual.date() == fecha_fin.date():
            fin_dia = fecha_fin
        else:
            fin_dia = datetime.combine(fecha_actual.date() + timedelta(days=1), time(0, 0))
        
        # Calcular este día como si fuera individual
        if inicio_dia < fin_dia:
            resultado_dia = calcular_horas_mismo_dia(inicio_dia, fin_dia, db)
            
            total_normales += resultado_dia['horas_normales']
            total_extras_normales += resultado_dia['horas_extras_normales']
            total_extras_especiales += resultado_dia['horas_extras_especiales']
        
        # Avanzar al siguiente día
        fecha_actual = datetime.combine(fecha_actual.date() + timedelta(days=1), time(0, 0))
    
    return {
        "horas_normales": round(total_normales, 2),
        "horas_extras_normales": round(total_extras_normales, 2),
        "horas_extras_especiales": round(total_extras_especiales, 2),
        "tipo_dia": "continuo_multidia"
    }

def calcular_horas_mismo_dia(fecha_inicio: datetime, fecha_fin: datetime, db: Session) -> dict:
    """Calcula horas para órdenes del mismo día (lógica original mejorada)"""
    
    duracion_total = (fecha_fin - fecha_inicio).total_seconds() / 3600
    dia_semana = fecha_inicio.weekday()
    fecha = fecha_inicio.date()
    
    # Definir horarios según el día
    if dia_semana < 5:  # Lunes a viernes
        inicio_normal = time(8, 0)
        fin_normal = time(17, 0)
        horas_normales_max = 8
        tipo_dia_actual = "laboral"
    elif dia_semana == 5:  # Sábado
        inicio_normal = time(8, 0)
        fin_normal = time(12, 0)
        horas_normales_max = 4
        tipo_dia_actual = "sabado"
    else:  # Domingo
        inicio_normal = fin_normal = time(0, 0)
        horas_normales_max = 0
        tipo_dia_actual = "domingo"
    
    # Si es feriado o domingo, todo es extra especial
    if es_feriado(fecha, db) or dia_semana == 6:
        return {
            "horas_normales": 0,
            "horas_extras_normales": 0,
            "horas_extras_especiales": round(duracion_total, 2),
            "tipo_dia": "feriado" if es_feriado(fecha, db) else "domingo"
        }
    
    # Calcular intersección con horario normal
    inicio_trabajo = datetime.combine(fecha, inicio_normal)
    fin_trabajo = datetime.combine(fecha, fin_normal)
    
    # Trabajo dentro del horario normal
    inicio_normal_real = max(fecha_inicio, inicio_trabajo)
    fin_normal_real = min(fecha_fin, fin_trabajo)
    
    horas_en_horario_normal = 0
    if inicio_normal_real < fin_normal_real:
        horas_en_horario_normal = (fin_normal_real - inicio_normal_real).total_seconds() / 3600
    
    # Trabajo fuera del horario normal (nocturno/extra)
    horas_fuera_horario = duracion_total - horas_en_horario_normal
    
    # Clasificar horas
    if horas_en_horario_normal <= horas_normales_max:
        horas_normales = horas_en_horario_normal
        extras_normales = 0
    else:
        horas_normales = horas_normales_max
        extras_normales = horas_en_horario_normal - horas_normales_max
    
    # Verificar si las horas fuera de horario son nocturnas (20:00-06:00)
    extras_especiales = 0
    if horas_fuera_horario > 0:
        # Simplificación: si hay trabajo fuera del horario normal, verificar si es nocturno
        hora_inicio = fecha_inicio.time()
        hora_fin = fecha_fin.time()
        
        # Horario nocturno: 20:00-06:00
        if (hora_inicio >= time(20, 0) or hora_inicio <= time(6, 0) or 
            hora_fin >= time(20, 0) or hora_fin <= time(6, 0)):
            extras_especiales = horas_fuera_horario
        else:
            extras_normales += horas_fuera_horario
    
    return {
        "horas_normales": round(horas_normales, 2),
        "horas_extras_normales": round(extras_normales, 2),
        "horas_extras_especiales": round(extras_especiales, 2),
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

# Endpoint principal: Reporte de horas extras UNIFICADO
@router.get("/reporte/", response_model=schemas.HorasExtrasReporte)
def get_reporte_horas_extras(
    fecha_inicio: date = Query(..., description="Fecha inicio del período"),
    fecha_fin: date = Query(..., description="Fecha fin del período"),
    tecnico_id: Optional[int] = Query(None, description="ID del técnico (opcional)"),
    db: Session = Depends(get_db)
):
    """
    Genera reporte UNIFICADO de horas extras por técnico en un período determinado.
    Ahora usa la misma lógica que /partes/{tecnico_id}/ para consistencia.
    """
    try:
        query = db.query(HorasExtras).filter(
            HorasExtras.fecha >= fecha_inicio,
            HorasExtras.fecha <= fecha_fin
        )
        
        if tecnico_id:
            query = query.filter(HorasExtras.tecnico_id == tecnico_id)
        
        horas_extras = query.all()
        
        # Agrupar por técnico (MISMA LÓGICA que /partes/)
        tecnicos_resumen = {}
        for hora in horas_extras:
            tid = hora.tecnico_id
            if tid not in tecnicos_resumen:
                tecnicos_resumen[tid] = {
                    "tecnico": hora.tecnico,
                    "total_horas_extras_normales": 0,
                    "total_horas_extras_especiales": 0,
                    "total_horas_trabajadas": 0,
                    "partes_trabajados": set()
                }
            
            tecnicos_resumen[tid]["total_horas_extras_normales"] += hora.horas_extras_normales or 0
            tecnicos_resumen[tid]["total_horas_extras_especiales"] += hora.horas_extras_especiales or 0
            tecnicos_resumen[tid]["total_horas_trabajadas"] += (
                (hora.horas_normales or 0) + (hora.horas_extras_normales or 0) + (hora.horas_extras_especiales or 0)
            )
            tecnicos_resumen[tid]["partes_trabajados"].add(hora.parte_trabajo_id)
        
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
        
    except Exception as e:
        print(f"Error en get_reporte_horas_extras: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

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

# Endpoint para obtener partes con horas extras de un técnico específico (FUENTE DE VERDAD)
@router.get("/partes/{tecnico_id}/")
def get_partes_con_horas_extras(
    tecnico_id: int,
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    db: Session = Depends(get_db)
):
    """
    Obtiene los partes de trabajo con horas extras de un técnico específico.
    ESTE ES EL ENDPOINT PRINCIPAL - La lógica aquí es la fuente de verdad.
    El endpoint /reporte/ debe usar la misma lógica para consistencia.
    """
    
    try:
        # Verificar que el técnico existe
        tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()
        if not tecnico:
            raise HTTPException(status_code=404, detail="Técnico no encontrado")
        
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
                    "numero": parte.numero,
                    "fecha": hora.fecha.isoformat(),
                    "hora_inicio": hora.hora_inicio.strftime("%H:%M"),
                    "hora_fin": hora.hora_fin.strftime("%H:%M"),
                    "trabajo_solicitado": parte.trabajo_solicitado or "Sin descripción",
                    "cliente_empresa": parte.cliente_empresa or "Sin cliente",
                    "horas_normales": hora.horas_normales,
                    "horas_extras_normales": hora.horas_extras_normales,
                    "horas_extras_especiales": hora.horas_extras_especiales,
                    "tipo_dia": hora.tipo_dia,
                    "calculado_automaticamente": hora.calculado_automaticamente
                })
        
        return {
            "tecnico": {
                "id": tecnico.id,
                "nombre": f"{tecnico.nombre} {tecnico.apellido}",
                "email": tecnico.email
            },
            "partes": partes_detalle,
            "total_horas_normales": sum(p.get("horas_normales", 0) for p in partes_detalle),
            "total_horas_extras_normales": sum(p.get("horas_extras_normales", 0) for p in partes_detalle),
            "total_horas_extras_especiales": sum(p.get("horas_extras_especiales", 0) for p in partes_detalle)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en get_partes_con_horas_extras: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# Endpoint de debug temporal
@router.get("/debug/partes/{tecnico_id}/")
def debug_partes_tecnico(
    tecnico_id: int,
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    db: Session = Depends(get_db)
):
    """Endpoint de debug para diagnosticar problemas."""
    try:
        # Verificar técnico
        tecnico = db.query(Tecnico).filter(Tecnico.id == tecnico_id).first()
        if not tecnico:
            return {"error": "Técnico no encontrado", "tecnico_id": tecnico_id}
        
        # Contar registros
        total_horas_extras = db.query(HorasExtras).count()
        horas_extras_tecnico = db.query(HorasExtras).filter(HorasExtras.tecnico_id == tecnico_id).count()
        horas_extras_rango = db.query(HorasExtras).filter(
            HorasExtras.tecnico_id == tecnico_id,
            HorasExtras.fecha >= fecha_inicio,
            HorasExtras.fecha <= fecha_fin
        ).count()
        
        return {
            "tecnico": {
                "id": tecnico.id,
                "nombre": f"{tecnico.nombre} {tecnico.apellido}",
                "email": tecnico.email
            },
            "total_horas_extras_bd": total_horas_extras,
            "horas_extras_del_tecnico": horas_extras_tecnico,
            "horas_extras_en_rango": horas_extras_rango,
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat()
        }
        
    except Exception as e:
        return {"error": str(e), "tipo": type(e).__name__}

# Endpoint de consistencia - Verifica que ambos endpoints den resultados coherentes
@router.get("/debug/consistencia/")
def verificar_consistencia_endpoints(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    db: Session = Depends(get_db)
):
    """Verifica consistencia entre /reporte/ y /partes/ endpoints"""
    try:
        # Obtener datos del endpoint /reporte/
        reporte = get_reporte_horas_extras(fecha_inicio, fecha_fin, None, db)
        
        # Comparar con datos directos de /partes/ para cada técnico
        inconsistencias = []
        
        for resumen_tecnico in reporte.resumen:
            tecnico_id = resumen_tecnico.tecnico_id
            
            # Obtener datos del endpoint /partes/
            try:
                partes_data = get_partes_con_horas_extras(tecnico_id, fecha_inicio, fecha_fin, db)
                partes_count = len(partes_data.get('partes', []))
                
                # Comparar conteos
                if resumen_tecnico.partes_trabajados != partes_count:
                    inconsistencias.append({
                        "tecnico_id": tecnico_id,
                        "tecnico_nombre": f"{resumen_tecnico.tecnico_nombre} {resumen_tecnico.tecnico_apellido}",
                        "reporte_partes": resumen_tecnico.partes_trabajados,
                        "partes_endpoint": partes_count,
                        "diferencia": abs(resumen_tecnico.partes_trabajados - partes_count)
                    })
                    
            except Exception as e:
                inconsistencias.append({
                    "tecnico_id": tecnico_id,
                    "error": f"Error verificando técnico {tecnico_id}: {str(e)}"
                })
        
        return {
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "total_tecnicos_reporte": len(reporte.resumen),
            "inconsistencias_encontradas": len(inconsistencias),
            "inconsistencias": inconsistencias,
            "estado": "CONSISTENTE" if len(inconsistencias) == 0 else "INCONSISTENTE"
        }
        
    except Exception as e:
        return {"error": str(e), "tipo": type(e).__name__}

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

@router.post("/recalcular-todas-las-horas/")
def recalcular_todas_las_horas(db: Session = Depends(get_db)):
    """Recalcula todas las horas extras con la lógica mejorada"""
    try:
        # Obtener todos los partes con fechas
        partes = db.query(ParteTrabajo).filter(
            ParteTrabajo.hora_inicio.isnot(None),
            ParteTrabajo.hora_fin.isnot(None)
        ).all()
        
        actualizados = 0
        errores = 0
        
        for parte in partes:
            try:
                # Obtener registros de horas existentes para este parte
                horas_existentes = db.query(HorasExtras).filter(
                    HorasExtras.parte_trabajo_id == parte.id
                ).all()
                
                if horas_existentes:
                    # Recalcular con la nueva lógica
                    nuevo_calculo = calcular_horas_extras(parte.hora_inicio, parte.hora_fin, db)
                    
                    # Actualizar todos los registros de técnicos para este parte
                    for hora_reg in horas_existentes:
                        hora_reg.horas_normales = nuevo_calculo['horas_normales']
                        hora_reg.horas_extras_normales = nuevo_calculo['horas_extras_normales'] 
                        hora_reg.horas_extras_especiales = nuevo_calculo['horas_extras_especiales']
                        hora_reg.tipo_dia = nuevo_calculo['tipo_dia']
                    
                    actualizados += 1
            except Exception as e:
                errores += 1
                print(f"Error procesando parte {parte.id_parte_api}: {e}")
        
        db.commit()
        
        return {
            "mensaje": "Recálculo completado",
            "partes_totales": len(partes),
            "partes_actualizados": actualizados,
            "errores": errores
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error en recálculo: {str(e)}")

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
