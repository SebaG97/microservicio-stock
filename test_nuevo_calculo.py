"""
Probar el nuevo cálculo inteligente integrado en el sistema
"""
from datetime import datetime
from database import get_db
from models import ParteTrabajo
from routers.horas_extras import calcular_horas_extras

def probar_calculo_orden(id_parte_api: str):
    """Probar el nuevo cálculo con una orden específica"""
    db = next(get_db())
    
    orden = db.query(ParteTrabajo).filter(ParteTrabajo.id_parte_api == id_parte_api).first()
    if not orden:
        print(f"❌ Orden {id_parte_api} no encontrada")
        return
    
    print(f"\n🧪 PROBANDO NUEVO CÁLCULO - Orden: {orden.id_parte_api}")
    print(f"⏰ Inicio: {orden.hora_inicio}")
    print(f"⏰ Fin: {orden.hora_fin}")
    
    # Usar la nueva función integrada
    resultado = calcular_horas_extras(orden.hora_inicio, orden.hora_fin, db)
    
    print(f"\n✨ RESULTADO CON NUEVA LÓGICA:")
    print(f"   Horas normales: {resultado['horas_normales']}h")
    print(f"   Horas extras normales: {resultado['horas_extras_normales']}h")
    print(f"   Horas extras especiales: {resultado['horas_extras_especiales']}h")
    print(f"   Tipo día: {resultado['tipo_dia']}")
    
    total = resultado['horas_normales'] + resultado['horas_extras_normales'] + resultado['horas_extras_especiales']
    print(f"   TOTAL: {total}h")
    
    db.close()

if __name__ == "__main__":
    print("🚀 Probando nuevo cálculo inteligente integrado")
    
    # Probar con las órdenes problemáticas
    probar_calculo_orden("820949CFE11")  # La de 10h extras especiales
    probar_calculo_orden("B2D1C88D2")    # La de 82h extras especiales
    probar_calculo_orden("C52901EB609")  # La de noche que estaba bien
