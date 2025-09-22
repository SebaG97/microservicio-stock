"""
Debug del algoritmo de detección automática
"""
from datetime import datetime, time, timedelta

def debug_deteccion(fecha_inicio: datetime, fecha_fin: datetime, caso: str):
    """Debug paso a paso del algoritmo de detección"""
    
    print(f"\n🔍 DEBUG DETECCIÓN: {caso}")
    print(f"⏰ {fecha_inicio} → {fecha_fin}")
    
    # 1. Verificar si comienza en horario de oficina
    hora_inicio = fecha_inicio.time()
    dia_inicio = fecha_inicio.weekday()
    
    print(f"📅 Día inicio: {dia_inicio} (0=lunes)")
    print(f"🕐 Hora inicio: {hora_inicio}")
    
    comienza_en_oficina = False
    if dia_inicio < 5:  # Lunes a viernes
        comienza_en_oficina = time(8, 0) <= hora_inicio <= time(17, 0)
        print(f"   Lunes-Viernes (8:00-17:00): {comienza_en_oficina}")
    elif dia_inicio == 5:  # Sábado
        comienza_en_oficina = time(8, 0) <= hora_inicio <= time(12, 0)
        print(f"   Sábado (8:00-12:00): {comienza_en_oficina}")
    
    # 2. Verificar si termina en horario de oficina
    hora_fin = fecha_fin.time()
    dia_fin = fecha_fin.weekday()
    
    print(f"📅 Día fin: {dia_fin}")
    print(f"🕐 Hora fin: {hora_fin}")
    
    termina_en_oficina = False
    if dia_fin < 5:  # Lunes a viernes
        termina_en_oficina = time(8, 0) <= hora_fin <= time(17, 0)
        print(f"   Lunes-Viernes (8:00-17:00): {termina_en_oficina}")
    elif dia_fin == 5:  # Sábado
        termina_en_oficina = time(8, 0) <= hora_fin <= time(12, 0)
        print(f"   Sábado (8:00-12:00): {termina_en_oficina}")
    
    # 3. Calcular días laborales
    dias_laborales = 0
    fecha_actual = fecha_inicio.date()
    while fecha_actual <= fecha_fin.date():
        if fecha_actual.weekday() < 6:  # No domingo
            dias_laborales += 1
        fecha_actual += timedelta(days=1)
    
    print(f"📊 Días laborales involucrados: {dias_laborales}")
    
    # 4. Calcular duración y límites
    duracion_total = (fecha_fin - fecha_inicio).total_seconds() / 3600
    horas_esperadas_oficina = dias_laborales * 9  # 8h + 1h extra máx por día
    limite_tolerancia = horas_esperadas_oficina * 1.2
    
    print(f"⏱️  Duración total: {duracion_total:.2f}h")
    print(f"🏢 Horas esperadas oficina: {horas_esperadas_oficina}h")
    print(f"📏 Límite con tolerancia: {limite_tolerancia:.2f}h")
    
    # Resultado
    es_oficina = (comienza_en_oficina and termina_en_oficina and 
                  duracion_total <= limite_tolerancia)
    
    print(f"✅ Criterios:")
    print(f"   Comienza en oficina: {comienza_en_oficina}")
    print(f"   Termina en oficina: {termina_en_oficina}")
    print(f"   Duración aceptable: {duracion_total <= limite_tolerancia}")
    print(f"🎯 RESULTADO: {'TRABAJO DE OFICINA' if es_oficina else 'TRABAJO CONTINUO/NOCTURNO'}")

if __name__ == "__main__":
    # Caso 1: 820949CFE11 - Debería ser trabajo de oficina
    debug_deteccion(
        datetime(2025, 8, 26, 10, 0, 0),  # Lunes 10:00
        datetime(2025, 8, 27, 13, 15, 0), # Martes 13:15
        "820949CFE11 - Trabajo oficina multi-día"
    )
    
    # Caso 2: C52901EB609 - Debería ser trabajo nocturno
    debug_deteccion(
        datetime(2025, 9, 18, 17, 0, 0),  # Miércoles 17:00
        datetime(2025, 9, 19, 0, 49, 0),  # Jueves 00:49
        "C52901EB609 - Trabajo nocturno"
    )
    
    # Caso 3: B2D1C88D2 - Debería ser trabajo de oficina
    debug_deteccion(
        datetime(2025, 7, 21, 8, 0, 0),   # Lunes 08:00
        datetime(2025, 7, 25, 17, 0, 0),  # Viernes 17:00
        "B2D1C88D2 - Trabajo oficina 5 días"
    )
