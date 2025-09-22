"""
Probar la nueva detección automática de trabajo de oficina vs nocturno
"""
from datetime import datetime
from database import get_db
from models import ParteTrabajo
from routers.horas_extras import calcular_horas_extras, es_trabajo_oficina_multidia

def probar_deteccion_automatica():
    """Probar la detección automática con varias órdenes"""
    db = next(get_db())
    
    # Casos de prueba
    casos = [
        {
            'id': '820949CFE11',
            'descripcion': 'Trabajo de oficina multi-día (26/08 10:00 → 27/08 13:15)',
            'esperado': 'oficina_multidia'
        },
        {
            'id': 'C52901EB609', 
            'descripcion': 'Trabajo nocturno real (18/09 17:00 → 19/09 00:49)',
            'esperado': 'continuo_multidia'
        },
        {
            'id': 'B2D1C88D2',
            'descripcion': 'Trabajo de oficina 5 días (21/07 08:00 → 25/07 17:00)',
            'esperado': 'oficina_multidia'
        }
    ]
    
    print("🧪 PROBANDO DETECCIÓN AUTOMÁTICA DE PATRONES DE TRABAJO\n")
    
    for caso in casos:
        orden = db.query(ParteTrabajo).filter(ParteTrabajo.id_parte_api == caso['id']).first()
        if not orden:
            print(f"❌ Orden {caso['id']} no encontrada")
            continue
        
        print(f"🔍 {caso['descripcion']}")
        print(f"   Orden: {orden.id_parte_api}")
        print(f"   ⏰ {orden.hora_inicio} → {orden.hora_fin}")
        
        # Detectar tipo de trabajo
        es_oficina = es_trabajo_oficina_multidia(orden.hora_inicio, orden.hora_fin)
        
        # Calcular horas
        resultado = calcular_horas_extras(orden.hora_inicio, orden.hora_fin, db)
        
        print(f"   🤖 Detección automática: {'Trabajo de oficina' if es_oficina else 'Trabajo continuo/nocturno'}")
        print(f"   📊 Resultado: {resultado['tipo_dia']}")
        print(f"   ⏱️  Normales: {resultado['horas_normales']}h")
        print(f"       Extras normales: {resultado['horas_extras_normales']}h") 
        print(f"       Extras especiales: {resultado['horas_extras_especiales']}h")
        
        # Verificar si coincide con lo esperado
        deteccion_correcta = (
            (es_oficina and caso['esperado'] == 'oficina_multidia') or
            (not es_oficina and caso['esperado'] == 'continuo_multidia')
        )
        
        print(f"   ✅ Detección: {'CORRECTA' if deteccion_correcta else 'INCORRECTA'}")
        print("-" * 70)
    
    db.close()

if __name__ == "__main__":
    probar_deteccion_automatica()
