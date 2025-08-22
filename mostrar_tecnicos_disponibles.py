from database import SessionLocal
from models import Tecnico, ParteTrabajo, HorasExtras

def mostrar_tecnicos_disponibles():
    """Muestra todos los técnicos disponibles con sus IDs"""
    
    db = SessionLocal()
    
    try:
        print("📋 TÉCNICOS DISPONIBLES EN EL SISTEMA:")
        print("="*50)
        
        tecnicos = db.query(Tecnico).all()
        
        for tecnico in tecnicos:
            # Contar partes y horas
            partes_count = db.query(ParteTrabajo).filter(ParteTrabajo.tecnico_id == tecnico.id).count()
            horas_count = db.query(HorasExtras).filter(HorasExtras.tecnico_id == tecnico.id).count()
            
            print(f"ID: {tecnico.id:2d} | {tecnico.nombre} {tecnico.apellido}")
            print(f"     Legajo: {tecnico.legajo}")
            print(f"     Partes: {partes_count}, Horas extras: {horas_count}")
            print(f"     Endpoint: /api/horas-extras/partes/{tecnico.id}/?fecha_inicio=2025-07-21&fecha_fin=2025-08-20")
            print("-" * 50)
        
        print(f"\n✅ Total: {len(tecnicos)} técnicos disponibles")
        print(f"\n🌐 Endpoints principales:")
        print(f"   GET /api/horas-extras/tecnicos/")
        print(f"   GET /api/horas-extras/reporte/?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD")
        print(f"   GET /api/horas-extras/partes/{{tecnico_id}}/?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD")
        print(f"   GET /api/horas-extras/detalle/{{tecnico_id}}?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    mostrar_tecnicos_disponibles()
