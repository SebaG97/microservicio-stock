from datetime import datetime, time
from database import get_db
from models import Feriado
from sqlalchemy.orm import sessionmaker
from database import engine

def tipo_dia_simple(fecha, db):
    """Determina el tipo de día sin depender de la función original"""
    # Verificar feriados
    if db.query(Feriado).filter(Feriado.fecha == fecha.date()).first():
        return "feriado"
    
    dia_semana = fecha.weekday()  # 0=lunes, 6=domingo
    if dia_semana == 6:  # domingo
        return "domingo"
    elif dia_semana == 5:  # sábado
        return "sabado"
    else:  # lunes a viernes
        return "laboral"

# Datos de la orden problemática
inicio = datetime(2025, 8, 26, 10, 0)  # 26/08/2025 10:00
fin = datetime(2025, 8, 27, 13, 15)    # 27/08/2025 13:15

Session = sessionmaker(bind=engine)
db = Session()

print(f"🔍 DEBUGGEANDO ORDEN 820949CFE11")
print(f"📅 Inicio: {inicio}")
print(f"📅 Fin: {fin}")

# Análisis manual del problema
total_horas = (fin - inicio).total_seconds() / 3600
print(f"\n🔍 ANÁLISIS MANUAL:")
print(f"   Total real: {total_horas:.2f}h")
print(f"   Diferencia: {(fin - inicio).days} días, {(fin - inicio).seconds//3600}h {((fin - inicio).seconds%3600)//60}min")

# Verificar tipos de día
tipo_inicio = tipo_dia_simple(inicio, db)
tipo_fin = tipo_dia_simple(fin, db)

print(f"\n📅 INFORMACIÓN DE LOS DÍAS:")
print(f"   {inicio.strftime('%A %d/%m/%Y')}: {tipo_inicio}")
print(f"   {fin.strftime('%A %d/%m/%Y')}: {tipo_fin}")

# Análisis por segmentos (lo que debería hacer la función)
print(f"\n🕒 ANÁLISIS POR SEGMENTOS:")

# Día 1: 26/08/2025 lunes 10:00-24:00 
dia1_inicio = time(10, 0)
dia1_fin = time(23, 59, 59)
horas_dia1 = 14  # 10:00 a 24:00

print(f"   DÍA 1 (lunes): 10:00-24:00 = {horas_dia1}h")
print(f"      Normal (8-17h): 7h (10:00-17:00)")
print(f"      Extras normales (17-20h): 3h (17:00-20:00)")  
print(f"      Extras especiales (20-24h): 4h (20:00-24:00) - NOCTURNO")

# Día 2: 27/08/2025 martes 00:00-13:15
dia2_inicio = time(0, 0)
dia2_fin = time(13, 15)
horas_dia2 = 13.25  # 00:00 a 13:15

print(f"   DÍA 2 (martes): 00:00-13:15 = {horas_dia2}h")
print(f"      Extras especiales (00-06h): 6h (00:00-06:00) - NOCTURNO")
print(f"      Extras normales (06-08h): 2h (06:00-08:00)")
print(f"      Normal (8-13.25h): 5.25h (08:00-13:15)")

print(f"\n📊 TOTALES ESPERADOS:")
print(f"   Normales: 7 + 5.25 = 12.25h")
print(f"   Extras normales: 3 + 2 = 5h") 
print(f"   Extras especiales: 4 + 6 = 10h")
print(f"   TOTAL: 27.25h ✓")

print(f"\n❌ PROBLEMA DETECTADO:")
print(f"   El cálculo actual muestra 10h extras especiales")
print(f"   Esto coincide con el análisis manual (4h + 6h nocturno)")
print(f"   Pero parece que no está distribuyendo bien las horas normales/extras normales")

db.close()
