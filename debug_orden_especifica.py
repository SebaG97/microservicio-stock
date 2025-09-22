from datetime import datetime, time
from routers.horas_extras import calcular_horas_extras

# Datos de la orden problemática
inicio = datetime(2025, 8, 26, 10, 0)  # 26/08/2025 10:00
fin = datetime(2025, 8, 27, 13, 15)    # 27/08/2025 13:15

print(f"🔍 DEBUGGEANDO ORDEN 820949CFE11")
print(f"📅 Inicio: {inicio}")
print(f"📅 Fin: {fin}")

# Calcular con la función actual
resultado = calcular_horas_extras(inicio, fin)

print(f"\n📊 RESULTADO ACTUAL:")
print(f"   Normales: {resultado['horas_normales']}h")
print(f"   Extras normales: {resultado['horas_extras_normales']}h")
print(f"   Extras especiales: {resultado['horas_extras_especiales']}h")
print(f"   Tipo día: {resultado['tipo_dia']}")
print(f"   TOTAL: {resultado['horas_normales'] + resultado['horas_extras_normales'] + resultado['horas_extras_especiales']}h")

# Análisis manual
total_horas = (fin - inicio).total_seconds() / 3600
print(f"\n🔍 ANÁLISIS MANUAL:")
print(f"   Total real: {total_horas}h")
print(f"   Diferencia: {(fin - inicio).days} días, {(fin - inicio).seconds//3600} horas")

# Verificar si es lunes (día laboral)
print(f"\n📅 INFORMACIÓN DEL DÍA:")
print(f"   Día de la semana inicio: {inicio.strftime('%A')} ({inicio.weekday()})")  # 0=lunes, 6=domingo
print(f"   Día de la semana fin: {fin.strftime('%A')} ({fin.weekday()})")
