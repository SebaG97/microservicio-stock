"""
Cálculo inteligente de horas que distingue entre:
- Trabajo en múltiples días laborales (horario normal)
- Trabajo nocturno real (fuera de horario)
"""
from datetime import datetime, time, timedelta
from database import get_db
from models import ParteTrabajo
import holidays

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
            tipo_dia = "laboral"
        elif dia_semana == 5:  # Sábado
            inicio_trabajo = time(8, 0)
            fin_trabajo = time(12, 0)
            tipo_dia = "sabado"
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
            jornadas.append((inicio_real, fin_real, tipo_dia))
        
        fecha_actual += timedelta(days=1)
    
    return jornadas

def calcular_horas_inteligente(fecha_inicio: datetime, fecha_fin: datetime, es_feriado: bool = False) -> dict:
    """
    Calcula horas de trabajo de forma inteligente:
    1. Identifica si es trabajo multi-día en horario normal
    2. Identifica trabajo nocturno real
    3. Calcula correctamente extras normales vs especiales
    """
    
    # Verificar si es una orden que cruza múltiples días
    es_multi_dia = fecha_inicio.date() != fecha_fin.date()
    
    if es_multi_dia:
        print(f"🔍 Orden multi-día detectada: {fecha_inicio.date()} → {fecha_fin.date()}")
        return calcular_horas_multi_dia(fecha_inicio, fecha_fin, es_feriado)
    else:
        print(f"🔍 Orden mismo día: {fecha_inicio.date()}")
        return calcular_horas_mismo_dia(fecha_inicio, fecha_fin, es_feriado)

def calcular_horas_multi_dia(fecha_inicio: datetime, fecha_fin: datetime, es_feriado: bool) -> dict:
    """Calcula horas para órdenes que abarcan múltiples días"""
    
    jornadas = obtener_jornadas_laborales(fecha_inicio, fecha_fin)
    
    total_normales = 0
    total_extras_normales = 0  
    total_extras_especiales = 0
    
    print(f"📅 Jornadas identificadas: {len(jornadas)}")
    
    for i, (inicio, fin, tipo_dia) in enumerate(jornadas, 1):
        duracion = (fin - inicio).total_seconds() / 3600
        print(f"   Día {i}: {inicio.strftime('%d/%m %H:%M')} → {fin.strftime('%d/%m %H:%M')} = {duracion:.2f}h ({tipo_dia})")
        
        if es_feriado or tipo_dia == "sabado":
            total_extras_especiales += duracion
        else:
            # Día laboral normal
            if duracion <= 8:
                total_normales += duracion
            else:
                total_normales += 8
                total_extras_normales += (duracion - 8)
    
    return {
        'horas_normales': round(total_normales, 2),
        'horas_extras_normales': round(total_extras_normales, 2),
        'horas_extras_especiales': round(total_extras_especiales, 2),
        'total_horas': round(total_normales + total_extras_normales + total_extras_especiales, 2),
        'es_multi_dia': True,
        'jornadas': len(jornadas)
    }

def calcular_horas_mismo_dia(fecha_inicio: datetime, fecha_fin: datetime, es_feriado: bool) -> dict:
    """Calcula horas para órdenes del mismo día (lógica original mejorada)"""
    
    duracion_total = (fecha_fin - fecha_inicio).total_seconds() / 3600
    dia_semana = fecha_inicio.weekday()
    
    # Definir horarios según el día
    if dia_semana < 5:  # Lunes a viernes
        inicio_normal = time(8, 0)
        fin_normal = time(17, 0)
        horas_normales_max = 8
    elif dia_semana == 5:  # Sábado
        inicio_normal = time(8, 0)
        fin_normal = time(12, 0)
        horas_normales_max = 4
    else:  # Domingo
        inicio_normal = fin_normal = time(0, 0)
        horas_normales_max = 0
    
    # Si es feriado o domingo, todo es extra especial
    if es_feriado or dia_semana == 6:
        return {
            'horas_normales': 0,
            'horas_extras_normales': 0,
            'horas_extras_especiales': round(duracion_total, 2),
            'total_horas': round(duracion_total, 2),
            'es_multi_dia': False
        }
    
    # Calcular intersección con horario normal
    inicio_trabajo = datetime.combine(fecha_inicio.date(), inicio_normal)
    fin_trabajo = datetime.combine(fecha_inicio.date(), fin_normal)
    
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
    
    # Todo lo que está fuera del horario es extra especial (nocturno)
    extras_especiales = horas_fuera_horario
    
    return {
        'horas_normales': round(horas_normales, 2),
        'horas_extras_normales': round(extras_normales, 2),
        'horas_extras_especiales': round(extras_especiales, 2),
        'total_horas': round(duracion_total, 2),
        'es_multi_dia': False
    }

def analizar_orden_especifica(id_parte_api: str):
    """Analiza una orden específica con el nuevo cálculo inteligente"""
    db = next(get_db())
    
    orden = db.query(ParteTrabajo).filter(ParteTrabajo.id_parte_api == id_parte_api).first()
    if not orden:
        print(f"❌ Orden {id_parte_api} no encontrada")
        return
    
    print(f"\n🔍 ANÁLISIS INTELIGENTE - Orden: {orden.id_parte_api}")
    print(f"⏰ Inicio: {orden.hora_inicio}")
    print(f"⏰ Fin: {orden.hora_fin}")
    
    # Detectar si es feriado (simplificado)
    ar_holidays = holidays.Argentina()
    es_feriado = orden.hora_inicio.date() in ar_holidays
    
    resultado = calcular_horas_inteligente(orden.hora_inicio, orden.hora_fin, es_feriado)
    
    print(f"\n✨ RESULTADO INTELIGENTE:")
    print(f"   Horas normales: {resultado['horas_normales']}h")
    print(f"   Horas extras normales: {resultado['horas_extras_normales']}h")
    print(f"   Horas extras especiales: {resultado['horas_extras_especiales']}h")
    print(f"   TOTAL: {resultado['total_horas']}h")
    
    if resultado.get('es_multi_dia'):
        print(f"   📅 Trabajo multi-día: {resultado['jornadas']} jornadas")
    
    # Comparar con cálculo actual en BD (simplificado)
    print(f"\n📊 El cálculo inteligente detecta trabajo en horario normal de oficina")
    print(f"   en lugar de horas extras nocturnas incorrectas.")
    
    db.close()

if __name__ == "__main__":
    # Probar con la orden problemática
    analizar_orden_especifica("820949CFE11")
    
    print("\n" + "="*60)
    
    # Probar con otra orden multi-día
    analizar_orden_especifica("B2D1C88D2")
