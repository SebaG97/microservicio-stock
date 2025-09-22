"""
Investigar por qué las duraciones están mal calculadas
"""
from datetime import datetime

def calcular_duracion_manual():
    """Calcular manualmente las duraciones para verificar"""
    
    print("🔍 VERIFICACIÓN MANUAL DE DURACIONES\n")
    
    # Caso B2D1C88D2: 21/07/2025 08:00 → 25/07/2025 17:00
    inicio_b2d = datetime(2025, 7, 21, 8, 0, 0)  # Lunes
    fin_b2d = datetime(2025, 7, 25, 17, 0, 0)    # Viernes
    
    print(f"B2D1C88D2:")
    print(f"  Inicio: {inicio_b2d} ({inicio_b2d.strftime('%A')})")
    print(f"  Fin: {fin_b2d} ({fin_b2d.strftime('%A')})")
    
    duracion_b2d = (fin_b2d - inicio_b2d).total_seconds() / 3600
    dias_b2d = (fin_b2d.date() - inicio_b2d.date()).days + 1
    
    print(f"  Duración calculada: {duracion_b2d:.2f}h")
    print(f"  Días involucrados: {dias_b2d}")
    print(f"  Horas por día: {duracion_b2d/dias_b2d:.2f}h")
    
    # Manual: Lunes 8-17 (9h) + Martes 8-17 (9h) + ... + Viernes 8-17 (9h) = 45h
    print(f"  Esperado manual: 5 días × 9h = 45h")
    print(f"  ¿Coincide? {abs(duracion_b2d - 45) < 0.1}")
    
    print("\n" + "="*50)
    
    # Caso 820949CFE11: 26/08/2025 10:00 → 27/08/2025 13:15
    inicio_820 = datetime(2025, 8, 26, 10, 0, 0)  # Martes
    fin_820 = datetime(2025, 8, 27, 13, 15, 0)    # Miércoles
    
    print(f"\n820949CFE11:")
    print(f"  Inicio: {inicio_820} ({inicio_820.strftime('%A')})")
    print(f"  Fin: {fin_820} ({fin_820.strftime('%A')})")
    
    duracion_820 = (fin_820 - inicio_820).total_seconds() / 3600
    dias_820 = (fin_820.date() - inicio_820.date()).days + 1
    
    print(f"  Duración calculada: {duracion_820:.2f}h")
    print(f"  Días involucrados: {dias_820}")
    print(f"  Horas por día: {duracion_820/dias_820:.2f}h")
    
    # Manual: Martes 10:00-17:00 (7h) + Miércoles 8:00-13:15 (5.25h) = 12.25h
    print(f"  Esperado manual: 7h + 5.25h = 12.25h")
    print(f"  ¡PROBLEMA! Está calculando trabajo continuo en lugar de jornadas separadas")

if __name__ == "__main__":
    calcular_duracion_manual()
