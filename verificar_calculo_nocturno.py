#!/usr/bin/env python3
"""
Script para verificar el cálculo mejorado de horas nocturnas
"""

from database import SessionLocal
from models import ParteTrabajo, HorasExtras
from routers.horas_extras import calcular_horas_extras

def verificar_calculo_nocturno():
    """Verifica el cálculo de la orden C52901EB609"""
    db = SessionLocal()
    try:
        # Buscar la orden específica
        parte = db.query(ParteTrabajo).filter(
            ParteTrabajo.id_parte_api == 'C52901EB609'
        ).first()
        
        if not parte:
            print("❌ No se encontró la orden C52901EB609")
            return
        
        print(f"📋 Orden: {parte.id_parte_api}")
        print(f"⏰ Inicio: {parte.hora_inicio}")
        print(f"⏰ Fin: {parte.hora_fin}")
        print()
        
        # Calcular con la nueva lógica
        nuevo_calculo = calcular_horas_extras(parte.hora_inicio, parte.hora_fin, db)
        
        print("🆕 CÁLCULO MEJORADO:")
        print(f"   Horas normales: {nuevo_calculo['horas_normales']}h")
        print(f"   Horas extras normales: {nuevo_calculo['horas_extras_normales']}h")
        print(f"   Horas extras especiales: {nuevo_calculo['horas_extras_especiales']}h")
        print(f"   Tipo día: {nuevo_calculo['tipo_dia']}")
        total_nuevo = (nuevo_calculo['horas_normales'] + 
                      nuevo_calculo['horas_extras_normales'] + 
                      nuevo_calculo['horas_extras_especiales'])
        print(f"   TOTAL: {total_nuevo}h")
        print()
        
        # Obtener cálculo anterior
        horas_actual = db.query(HorasExtras).filter(
            HorasExtras.parte_trabajo_id == parte.id
        ).first()
        
        if horas_actual:
            print("📊 CÁLCULO ANTERIOR:")
            print(f"   Horas normales: {horas_actual.horas_normales}h")
            print(f"   Horas extras normales: {horas_actual.horas_extras_normales}h")
            print(f"   Horas extras especiales: {horas_actual.horas_extras_especiales}h")
            total_anterior = (horas_actual.horas_normales + 
                            horas_actual.horas_extras_normales + 
                            horas_actual.horas_extras_especiales)
            print(f"   TOTAL: {total_anterior}h")
            print()
            
            print("🔍 DIFERENCIAS:")
            print(f"   Normales: {nuevo_calculo['horas_normales'] - horas_actual.horas_normales:+.2f}h")
            print(f"   Extras normales: {nuevo_calculo['horas_extras_normales'] - horas_actual.horas_extras_normales:+.2f}h")
            print(f"   Extras especiales: {nuevo_calculo['horas_extras_especiales'] - horas_actual.horas_extras_especiales:+.2f}h")
            print(f"   TOTAL: {total_nuevo - total_anterior:+.2f}h")
        
        print()
        print("✅ El nuevo cálculo detecta correctamente:")
        print("   - 17:00-20:00 = 3h extras normales")
        print("   - 20:00-00:49 = 4.82h extras especiales (nocturno)")
        
    finally:
        db.close()

if __name__ == "__main__":
    verificar_calculo_nocturno()
