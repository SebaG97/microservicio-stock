"""
Debug específico del algoritmo completamente nuevo
"""
from datetime import datetime, time, timedelta

def debug_nuevo_algoritmo(fecha_inicio: datetime, fecha_fin: datetime, caso: str):
    """Debug del algoritmo basado en horas de oficina"""
    
    print(f"\n🔍 DEBUG ALGORITMO NUEVO: {caso}")
    print(f"⏰ {fecha_inicio} → {fecha_fin}")
    
    # Calcular horas de oficina posibles
    total_horas_oficina_posibles = 0
    fecha_actual = fecha_inicio.date()
    detalles_dias = []
    
    while fecha_actual <= fecha_fin.date():
        dia_semana = fecha_actual.weekday()
        
        # Horarios de oficina según día
        if dia_semana < 5:  # Lunes a viernes
            oficina_inicio = time(8, 0)
            oficina_fin = time(17, 0)
            tipo_dia = f"{['Lun','Mar','Mié','Jue','Vie'][dia_semana]}"
        elif dia_semana == 5:  # Sábado  
            oficina_inicio = time(8, 0)
            oficina_fin = time(12, 0)
            tipo_dia = "Sáb"
        else:  # Domingo - saltar
            fecha_actual += timedelta(days=1)
            continue
        
        # Calcular intersección con horario de oficina este día
        dia_inicio = datetime.combine(fecha_actual, oficina_inicio)
        dia_fin = datetime.combine(fecha_actual, oficina_fin)
        
        # Ajustar según fechas reales de la orden
        trabajo_inicio = max(fecha_inicio if fecha_actual == fecha_inicio.date() else dia_inicio, dia_inicio)
        trabajo_fin = min(fecha_fin if fecha_actual == fecha_fin.date() else dia_fin, dia_fin)
        
        horas_oficina_dia = 0
        if trabajo_inicio < trabajo_fin:
            horas_oficina_dia = (trabajo_fin - trabajo_inicio).total_seconds() / 3600
            # Máximo 10h por día (8h normales + 2h extras)
            horas_oficina_dia_limitadas = min(horas_oficina_dia, 10)
            total_horas_oficina_posibles += horas_oficina_dia_limitadas
            
            detalles_dias.append(f"   {tipo_dia} {fecha_actual}: {trabajo_inicio.time()}-{trabajo_fin.time()} = {horas_oficina_dia:.2f}h")
        
        fecha_actual += timedelta(days=1)
    
    print(f"🏢 HORAS DE OFICINA POSIBLES:")
    for detalle in detalles_dias:
        print(detalle)
    print(f"   TOTAL: {total_horas_oficina_posibles:.2f}h")
    
    # Duración total real
    duracion_total_real = (fecha_fin - fecha_inicio).total_seconds() / 3600
    print(f"⏱️  DURACIÓN TOTAL REAL: {duracion_total_real:.2f}h")
    
    # Ratio
    ratio_oficina = duracion_total_real / max(total_horas_oficina_posibles, 1)
    print(f"📊 RATIO (real/oficina): {ratio_oficina:.2f}")
    
    # Análisis horarios
    hora_inicio = fecha_inicio.time()
    hora_fin = fecha_fin.time()
    
    inicio_razonable = time(6, 0) <= hora_inicio <= time(20, 0)
    fin_razonable = time(6, 0) <= hora_fin <= time(20, 0)
    horario_nocturno_claro = (time(22, 0) <= hora_fin or hora_fin <= time(5, 0))
    
    print(f"🕐 ANÁLISIS HORARIOS:")
    print(f"   Inicio {hora_inicio}: ¿Razonable (6:00-20:00)? {inicio_razonable}")
    print(f"   Fin {hora_fin}: ¿Razonable (6:00-20:00)? {fin_razonable}")
    print(f"   ¿Fin nocturno claro (22:00-05:00)? {horario_nocturno_claro}")
    
    # Decisión final
    es_oficina = (ratio_oficina <= 1.5 and 
                  inicio_razonable and 
                  fin_razonable and 
                  not horario_nocturno_claro)
    
    print(f"✅ CRITERIOS:")
    print(f"   Ratio ≤ 1.5: {ratio_oficina <= 1.5} ({ratio_oficina:.2f})")
    print(f"   Inicio razonable: {inicio_razonable}")
    print(f"   Fin razonable: {fin_razonable}")
    print(f"   No fin nocturno: {not horario_nocturno_claro}")
    
    print(f"🎯 RESULTADO: {'TRABAJO DE OFICINA' if es_oficina else 'TRABAJO CONTINUO/NOCTURNO'}")

if __name__ == "__main__":
    # Casos de prueba
    debug_nuevo_algoritmo(
        datetime(2025, 8, 26, 10, 0, 0),
        datetime(2025, 8, 27, 13, 15, 0),
        "820949CFE11 - Debería ser oficina"
    )
    
    debug_nuevo_algoritmo(
        datetime(2025, 9, 18, 17, 0, 0),
        datetime(2025, 9, 19, 0, 49, 0),
        "C52901EB609 - Debería ser nocturno"
    )
    
    debug_nuevo_algoritmo(
        datetime(2025, 7, 21, 8, 0, 0),
        datetime(2025, 7, 25, 17, 0, 0),
        "B2D1C88D2 - Debería ser oficina"
    )
