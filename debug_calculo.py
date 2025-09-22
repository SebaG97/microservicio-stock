"""
Debug manual para entender el problema del cálculo
"""
from datetime import datetime, time
from database import get_db

def debug_calculo_manual():
    """Debug manual del cálculo problemático"""
    
    # Orden C52901EB609: 18/09/2025 17:00 → 19/09/2025 00:49
    inicio = datetime(2025, 9, 18, 17, 0, 0)
    fin = datetime(2025, 9, 19, 0, 49, 0)
    
    print(f"🔍 DEBUG MANUAL - Orden C52901EB609")
    print(f"⏰ Inicio: {inicio}")
    print(f"⏰ Fin: {fin}")
    print(f"📅 Multi-día: {inicio.date() != fin.date()}")
    
    # Procesar día por día
    print(f"\n📊 PROCESANDO DÍA POR DÍA:")
    
    # Día 1: 18/09/2025 17:00 → 19/09/2025 00:00
    dia1_inicio = inicio
    dia1_fin = datetime(2025, 9, 19, 0, 0, 0)
    duracion_dia1 = (dia1_fin - dia1_inicio).total_seconds() / 3600
    
    print(f"   DÍA 1: {dia1_inicio} → {dia1_fin}")
    print(f"   Duración: {duracion_dia1}h")
    print(f"   Día semana: {dia1_inicio.weekday()} (0=lunes)")
    print(f"   Horario oficina (8-17): No (empieza a las 17:00)")
    print(f"   ¿Es nocturno (17:00-00:00)? Sí (después de 17:00)")
    
    # Día 2: 19/09/2025 00:00 → 19/09/2025 00:49
    dia2_inicio = datetime(2025, 9, 19, 0, 0, 0)
    dia2_fin = fin
    duracion_dia2 = (dia2_fin - dia2_inicio).total_seconds() / 3600
    
    print(f"   DÍA 2: {dia2_inicio} → {dia2_fin}")
    print(f"   Duración: {duracion_dia2:.2f}h")
    print(f"   Día semana: {dia2_inicio.weekday()}")
    print(f"   ¿Es nocturno (00:00-00:49)? Sí (antes de 6:00)")
    
    print(f"\n✅ RESULTADO ESPERADO:")
    print(f"   Día 1: {duracion_dia1}h extras especiales (después de 17:00)")
    print(f"   Día 2: {duracion_dia2:.2f}h extras especiales (antes de 6:00)")
    print(f"   TOTAL: {duracion_dia1 + duracion_dia2:.2f}h extras especiales")

if __name__ == "__main__":
    debug_calculo_manual()
