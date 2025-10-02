"""
Script de prueba para verificar la conexión a la base de datos MySQL
y probar la funcionalidad de las alarmas.
"""

import sys
from datetime import datetime
from sqlalchemy.orm import Session
from database import get_mysql_db, mysql_engine
from models_mysql import Measurement
from servicios.alarmas_service import AlarmasService

def test_mysql_connection():
    """Prueba la conexión a MySQL"""
    print("🔌 Probando conexión a MySQL...")
    try:
        # Crear una sesión de prueba
        db_gen = get_mysql_db()
        db = next(db_gen)
        
        # Probar hacer una consulta básica
        from sqlalchemy import text
        result = db.execute(text("SELECT 1 as test")).fetchone()
        print(f"✅ Conexión MySQL exitosa: {result}")
        
        # Verificar si la tabla measurements existe
        try:
            count = db.query(Measurement).count()
            print(f"✅ Tabla measurements existe con {count} registros")
            return True
        except Exception as e:
            print(f"⚠️  Error consultando tabla measurements: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return False
    finally:
        try:
            db.close()
        except:
            pass

def test_alarmas_service():
    """Prueba el servicio de alarmas"""
    print("\n📊 Probando servicio de alarmas...")
    try:
        db_gen = get_mysql_db()
        db = next(db_gen)
        
        # Obtener último dato por vessel
        ultimo_dato = AlarmasService.obtener_ultimo_dato_por_vessel(db)
        print(f"✅ Vessels encontrados: {len(ultimo_dato)}")
        
        if ultimo_dato:
            print("🚢 Algunos vessels:")
            for i, (vessel, timestamp) in enumerate(list(ultimo_dato.items())[:3]):
                print(f"   - {vessel}: {timestamp}")
        
        # Calcular alarmas
        alarmas = AlarmasService.calcular_alarmas_vessels(db)
        print(f"✅ Alarmas calculadas para {alarmas.total_vessels} vessels")
        print(f"📈 Resumen: {alarmas.resumen}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando servicio de alarmas: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            db.close()
        except:
            pass

if __name__ == "__main__":
    print("🧪 Iniciando pruebas de conexión MySQL y alarmas...")
    print("=" * 50)
    
    # Probar conexión
    connection_ok = test_mysql_connection()
    
    if connection_ok:
        # Probar servicios
        service_ok = test_alarmas_service()
        
        if service_ok:
            print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
            print("✅ El sistema de alarmas está listo para usar")
            print("\nEndpoints disponibles:")
            print("- GET /api/alarmas")
            print("- GET /api/alarmas/criticos")  
            print("- GET /api/alarmas/resumen")
            print("- GET /api/alarmas/vessel/{vessel_name}")
        else:
            print("\n⚠️  Conexión OK pero hay problemas con el servicio")
            sys.exit(1)
    else:
        print("\n❌ No se pudo establecer conexión con MySQL")
        print("Verifica:")
        print("- Que el host db.parks.com.py:3306 sea accesible")
        print("- Que las credenciales sean correctas")
        print("- Que la base de datos parks_data existe")
        print("- Que la tabla measurements existe")
        sys.exit(1)