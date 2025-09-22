"""
Revisar datos de las órdenes de trabajo
"""
from database import get_db
from models import ParteTrabajo

def revisar_datos_partes():
    """Revisar qué datos reales tenemos en la BD"""
    db = next(get_db())
    
    partes = db.query(ParteTrabajo).limit(5).all()
    
    print("🔍 MUESTRA DE DATOS EN BD:")
    for parte in partes:
        print(f"  ID BD: {parte.id}")
        print(f"  id_parte_api: {parte.id_parte_api}")
        print(f"  numero: {parte.numero}")
        print(f"  ejercicio: {parte.ejercicio}")
        print(f"  fecha: {parte.fecha}")
        print("  ---")
    
    # Contar cuántos tienen numero null
    total = db.query(ParteTrabajo).count()
    con_numero = db.query(ParteTrabajo).filter(ParteTrabajo.numero.isnot(None)).count()
    sin_numero = total - con_numero
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"  Total órdenes: {total}")
    print(f"  Con número: {con_numero}")
    print(f"  Sin número (null): {sin_numero}")
    
    db.close()

if __name__ == "__main__":
    revisar_datos_partes()
