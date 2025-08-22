from database import SessionLocal
from models import Tecnico, ParteTrabajo, HorasExtras

def limpiar_y_resincronizar():
    """Limpia los datos y prepara para una nueva sincronización"""
    
    db = SessionLocal()
    
    try:
        # Mostrar estado actual
        tecnicos_count = db.query(Tecnico).count()
        partes_count = db.query(ParteTrabajo).count()
        horas_count = db.query(HorasExtras).count()
        
        print(f"📊 Estado actual:")
        print(f"  - Técnicos: {tecnicos_count}")
        print(f"  - Partes: {partes_count}")
        print(f"  - Horas: {horas_count}")
        
        # Eliminar registros para una sincronización fresca
        print(f"\n🧹 Limpiando datos...")
        
        # Eliminar horas extras
        db.query(HorasExtras).delete()
        print(f"  ✅ Horas extras eliminadas")
        
        # Eliminar partes de trabajo
        db.query(ParteTrabajo).delete()
        print(f"  ✅ Partes de trabajo eliminados")
        
        # Eliminar técnicos
        db.query(Tecnico).delete()
        print(f"  ✅ Técnicos eliminados")
        
        db.commit()
        
        print(f"\n🚀 Base de datos limpia. Ahora el sincronizador puede crear todo desde cero.")
        print(f"   Reinicia el servidor para que la sincronización automática procese todos los datos.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    limpiar_y_resincronizar()
