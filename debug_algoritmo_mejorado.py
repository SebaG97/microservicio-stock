"""
Debug detallado del algoritmo mejorado
"""
from datetime import datetime, time, timedelta

def debug_algoritmo_mejorado(fecha_inicio: datetime, fecha_fin: datetime, caso: str):
    """Debug paso a paso del algoritmo mejorado"""
    
    print(f"\n🔍 DEBUG ALGORITMO MEJORADO: {caso}")
    print(f"⏰ {fecha_inicio} → {fecha_fin}")
    
    # Criterio 1: Duración promedio por día
    dias_totales = (fecha_fin.date() - fecha_inicio.date()).days + 1
    duracion_total = (fecha_fin - fecha_inicio).total_seconds() / 3600
    horas_promedio_por_dia = duracion_total / dias_totales
    
    print(f"📊 Días totales: {dias_totales}")
    print(f"⏱️  Duración total: {duracion_total:.2f}h")
    print(f"📈 Promedio por día: {horas_promedio_por_dia:.2f}h")
    print(f"🚨 ¿Más de 16h/día? {horas_promedio_por_dia > 16}")
    
    # Criterio 2: Patrón horario
    hora_inicio = fecha_inicio.time()
    hora_fin = fecha_fin.time()
    
    inicio_oficina_extendido = time(7, 0)
    fin_oficina_extendido = time(19, 0)
    inicio_nocturno = time(22, 0)
    fin_nocturno = time(6, 0)
    
    print(f"🕐 Hora inicio: {hora_inicio}")
    print(f"🕐 Hora fin: {hora_fin}")
    
    inicio_muy_temprano_o_tarde = hora_inicio <= fin_nocturno or hora_inicio >= inicio_nocturno
    fin_nocturno_claro = hora_fin <= fin_nocturno or hora_fin >= inicio_nocturno
    
    print(f"🌙 ¿Inicio nocturno? {inicio_muy_temprano_o_tarde}")
    print(f"🌙 ¿Fin nocturno? {fin_nocturno_claro}")
    
    # Criterio 3: Análisis de días
    dias_laborales = 0
    dias_weekend = 0
    
    fecha_actual = fecha_inicio.date()
    while fecha_actual <= fecha_fin.date():
        if fecha_actual.weekday() < 5:  # Lunes a viernes
            dias_laborales += 1
        elif fecha_actual.weekday() == 5:  # Sábado
            dias_laborales += 0.5
        else:  # Domingo
            dias_weekend += 1
        fecha_actual += timedelta(days=1)
    
    print(f"📅 Días laborales: {dias_laborales}")
    print(f"📅 Días weekend: {dias_weekend}")
    
    mucho_trabajo_domingo = dias_weekend > 0 and duracion_total > (dias_laborales * 12)
    print(f"🔴 ¿Mucho trabajo domingo? {mucho_trabajo_domingo}")
    
    # Criterio 4: Límite razonable
    max_horas_esperadas = dias_laborales * 12
    limite_tolerancia = max_horas_esperadas * 1.1
    
    print(f"🏢 Máx esperadas (12h/día): {max_horas_esperadas:.1f}h")
    print(f"📏 Límite con tolerancia: {limite_tolerancia:.1f}h")
    print(f"✅ ¿Duración aceptable? {duracion_total <= limite_tolerancia}")
    
    # Criterio final
    patron_horario_ok = (hora_inicio >= inicio_oficina_extendido and 
                        hora_fin <= fin_oficina_extendido)
    print(f"⏰ ¿Patrón horario OK (7:00-19:00)? {patron_horario_ok}")
    
    # Resultado final
    es_oficina = (not (horas_promedio_por_dia > 16) and
                  not inicio_muy_temprano_o_tarde and
                  not fin_nocturno_claro and
                  not mucho_trabajo_domingo and
                  patron_horario_ok and
                  duracion_total <= limite_tolerancia)
    
    print(f"🎯 RESULTADO FINAL: {'TRABAJO DE OFICINA' if es_oficina else 'TRABAJO CONTINUO/NOCTURNO'}")
    print(f"🔍 Razones de exclusión:")
    if horas_promedio_por_dia > 16:
        print(f"   ❌ Más de 16h/día")
    if inicio_muy_temprano_o_tarde:
        print(f"   ❌ Inicio nocturno")
    if fin_nocturno_claro:
        print(f"   ❌ Fin nocturno")
    if mucho_trabajo_domingo:
        print(f"   ❌ Mucho trabajo domingo")
    if not patron_horario_ok:
        print(f"   ❌ Fuera del patrón 7:00-19:00")
    if not (duracion_total <= limite_tolerancia):
        print(f"   ❌ Duración excesiva")

if __name__ == "__main__":
    # Casos de prueba
    debug_algoritmo_mejorado(
        datetime(2025, 8, 26, 10, 0, 0),
        datetime(2025, 8, 27, 13, 15, 0),
        "820949CFE11 - Debería ser oficina"
    )
    
    debug_algoritmo_mejorado(
        datetime(2025, 9, 18, 17, 0, 0),
        datetime(2025, 9, 19, 0, 49, 0),
        "C52901EB609 - Debería ser nocturno"
    )
    
    debug_algoritmo_mejorado(
        datetime(2025, 7, 21, 8, 0, 0),
        datetime(2025, 7, 25, 17, 0, 0),
        "B2D1C88D2 - Debería ser oficina"
    )
