from database import SessionLocal
from models import Tecnico, ParteTrabajo, HorasExtras

def listar_tecnicos_disponibles():
    """Lista todos los técnicos disponibles con sus IDs para el frontend"""
    
    db = SessionLocal()
    
    try:
        print("🔍 Técnicos disponibles en el sistema:")
        print("=" * 60)
        
        tecnicos = db.query(Tecnico).filter(Tecnico.activo == True).all()
        
        for tecnico in tecnicos:
            # Contar partes asignados
            partes_count = db.query(ParteTrabajo).filter(ParteTrabajo.tecnico_id == tecnico.id).count()
            # Contar registros de horas
            horas_count = db.query(HorasExtras).filter(HorasExtras.tecnico_id == tecnico.id).count()
            
            print(f"ID: {tecnico.id:2d} | {tecnico.nombre} {tecnico.apellido}")
            print(f"      Legajo: {tecnico.legajo}")
            print(f"      Partes: {partes_count} | Horas extras: {horas_count}")
            print("-" * 60)
        
        print(f"\n📊 Total técnicos activos: {len(tecnicos)}")
        
        # Mostrar URLs de ejemplo para el frontend
        if tecnicos:
            primer_tecnico = tecnicos[0]
            print(f"\n🌐 Ejemplos de endpoints para el frontend:")
            print(f"Técnicos: http://localhost:8000/api/horas-extras/tecnicos/")
            print(f"Reporte: http://localhost:8000/api/horas-extras/reporte/?fecha_inicio=2025-07-21&fecha_fin=2025-08-20")
            print(f"Partes del técnico {primer_tecnico.id}: http://localhost:8000/api/horas-extras/partes/{primer_tecnico.id}/?fecha_inicio=2025-07-21&fecha_fin=2025-08-20")
            print(f"Detalle del técnico {primer_tecnico.id}: http://localhost:8000/api/horas-extras/detalle/{primer_tecnico.id}?fecha_inicio=2025-07-21&fecha_fin=2025-08-20")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    listar_tecnicos_disponibles()
