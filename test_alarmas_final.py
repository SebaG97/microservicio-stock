"""
Script de prueba para el sistema de alarmas usando datos existentes
"""
from database import get_mysql_db
from servicios.alarmas_service import AlarmasService
import sys

def test_alarmas():
    print("🧪 Probando sistema de alarmas...")
    
    try:
        # Obtener una sesión de la base de datos MySQL
        db_generator = get_mysql_db()
        db = next(db_generator)
        
        print("✅ Conexión MySQL establecida")
        
        # Probar el servicio de alarmas
        print("\n📊 Calculando alarmas...")
        alarmas_result = AlarmasService.calcular_alarmas_vessels(db)
        
        print(f"\n📈 RESUMEN DE ALARMAS:")
        print(f"Total vessels: {alarmas_result.total_vessels}")
        print(f"Resumen por estado: {alarmas_result.resumen}")
        
        print(f"\n🚢 PRIMEROS 10 VESSELS:")
        for i, alarma in enumerate(alarmas_result.alarmas[:10], 1):
            print(f"{i:2d}. {alarma.vessel_name:<15} | {alarma.estado_alarma.value:<8} | {alarma.horas_sin_datos:6.1f}h | {alarma.ultimo_dato}")
        
        if alarmas_result.total_vessels > 10:
            print(f"... y {alarmas_result.total_vessels - 10} vessels más")
        
        # Mostrar solo vessels críticos
        print(f"\n🚨 VESSELS CRÍTICOS (>12h):")
        vessels_criticos = AlarmasService.obtener_vessels_criticos(db, 12.0)
        
        if vessels_criticos:
            for vessel in vessels_criticos:
                print(f"⚠️  {vessel.vessel_name:<15} | {vessel.horas_sin_datos:6.1f}h sin datos | Último: {vessel.ultimo_dato}")
        else:
            print("✅ No hay vessels en estado crítico")
        
        print("\n✅ Prueba completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            db.close()
        except:
            pass
    
    return True

if __name__ == "__main__":
    success = test_alarmas()
    sys.exit(0 if success else 1)