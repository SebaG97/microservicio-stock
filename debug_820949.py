"""
Debug específico de la orden problemática 820949CFE11
"""
from datetime import datetime, time
from database import get_db

def debug_orden_820949CFE11():
    """Debug de la orden que debería ser trabajo normal de oficina"""
    
    # Orden 820949CFE11: 26/08/2025 10:00 → 27/08/2025 13:15
    inicio = datetime(2025, 8, 26, 10, 0, 0)
    fin = datetime(2025, 8, 27, 13, 15, 0)
    
    print(f"🔍 DEBUG ORDEN 820949CFE11")
    print(f"⏰ Inicio: {inicio}")
    print(f"⏰ Fin: {fin}")
    print(f"📅 Multi-día: {inicio.date() != fin.date()}")
    
    print(f"\n📊 ANÁLISIS DÍA POR DÍA:")
    
    # Día 1: 26/08/2025 10:00 → 27/08/2025 00:00
    dia1_inicio = inicio
    dia1_fin = datetime(2025, 8, 27, 0, 0, 0)
    duracion_dia1 = (dia1_fin - dia1_inicio).total_seconds() / 3600
    
    print(f"   DÍA 1 (26/08): {dia1_inicio} → {dia1_fin}")
    print(f"   Duración total: {duracion_dia1}h")
    print(f"   Día semana: {dia1_inicio.weekday()} (lunes=0)")
    
    # Horario de oficina día 1: 8:00-17:00
    oficina_inicio_dia1 = datetime(2025, 8, 26, 8, 0, 0)
    oficina_fin_dia1 = datetime(2025, 8, 26, 17, 0, 0)
    
    # Trabajo en horario de oficina
    trabajo_oficina_inicio = max(dia1_inicio, oficina_inicio_dia1)  # 10:00
    trabajo_oficina_fin = min(dia1_fin, oficina_fin_dia1)  # 17:00
    
    if trabajo_oficina_inicio < trabajo_oficina_fin:
        horas_oficina_dia1 = (trabajo_oficina_fin - trabajo_oficina_inicio).total_seconds() / 3600
    else:
        horas_oficina_dia1 = 0
    
    # Trabajo fuera de oficina
    horas_fuera_dia1 = duracion_dia1 - horas_oficina_dia1
    
    print(f"      Trabajo en oficina (10:00-17:00): {horas_oficina_dia1}h")
    print(f"      Trabajo fuera oficina (17:00-00:00): {horas_fuera_dia1}h")
    print(f"      ¿Fuera es nocturno (20:00-06:00)? Sí")
    
    # Día 2: 27/08/2025 00:00 → 27/08/2025 13:15
    dia2_inicio = datetime(2025, 8, 27, 0, 0, 0)
    dia2_fin = fin
    duracion_dia2 = (dia2_fin - dia2_inicio).total_seconds() / 3600
    
    print(f"   DÍA 2 (27/08): {dia2_inicio} → {dia2_fin}")
    print(f"   Duración total: {duracion_dia2:.2f}h")
    print(f"   Día semana: {dia2_inicio.weekday()}")
    
    # Horario de oficina día 2: 8:00-17:00
    oficina_inicio_dia2 = datetime(2025, 8, 27, 8, 0, 0)
    oficina_fin_dia2 = datetime(2025, 8, 27, 17, 0, 0)
    
    # Trabajo nocturno (00:00-06:00)
    nocturno_fin = datetime(2025, 8, 27, 6, 0, 0)
    trabajo_nocturno_fin = min(dia2_fin, nocturno_fin)
    
    if dia2_inicio < trabajo_nocturno_fin:
        horas_nocturno_dia2 = (trabajo_nocturno_fin - dia2_inicio).total_seconds() / 3600
    else:
        horas_nocturno_dia2 = 0
    
    # Trabajo en horario de oficina (08:00-13:15)
    trabajo_oficina_inicio_dia2 = max(oficina_inicio_dia2, dia2_inicio, datetime(2025, 8, 27, 6, 0, 0))
    trabajo_oficina_fin_dia2 = min(dia2_fin, oficina_fin_dia2)
    
    if trabajo_oficina_inicio_dia2 < trabajo_oficina_fin_dia2:
        horas_oficina_dia2 = (trabajo_oficina_fin_dia2 - trabajo_oficina_inicio_dia2).total_seconds() / 3600
    else:
        horas_oficina_dia2 = 0
    
    print(f"      Trabajo nocturno (00:00-06:00): {horas_nocturno_dia2}h")
    print(f"      Trabajo en oficina (08:00-13:15): {horas_oficina_dia2:.2f}h")
    
    # Resultado esperado
    total_normales = horas_oficina_dia1 + horas_oficina_dia2
    total_especiales = horas_fuera_dia1 + horas_nocturno_dia2
    
    print(f"\n✅ CÁLCULO CORRECTO ESPERADO:")
    print(f"   Horas normales: {total_normales:.2f}h")
    print(f"   Horas extras especiales: {total_especiales:.2f}h")
    print(f"   TOTAL: {total_normales + total_especiales:.2f}h")

if __name__ == "__main__":
    debug_orden_820949CFE11()
