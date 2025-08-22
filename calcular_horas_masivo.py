#!/usr/bin/env python3
"""
Script para calcular automáticamente las horas extras de todos los partes de trabajo existentes
"""
from database import SessionLocal
from models import ParteTrabajo, HorasExtras, Tecnico, Feriado
from routers.horas_extras import calcular_horas_extras

def calcular_todas_las_horas():
    """Calcula las horas extras para todos los partes de trabajo finalizados"""
    db = SessionLocal()
    
    try:
        print("Calculando horas extras para todos los partes de trabajo...")
        
        # Obtener todos los partes finalizados con fecha de fin
        partes = db.query(ParteTrabajo).filter(
            ParteTrabajo.fecha_fin.isnot(None),
            ParteTrabajo.estado == "finalizado"
        ).all()
        
        calculados = 0
        errores = 0
        
        for parte in partes:
            try:
                # Verificar si ya existe cálculo
                horas_existente = db.query(HorasExtras).filter(
                    HorasExtras.parte_trabajo_id == parte.id
                ).first()
                
                if horas_existente:
                    print(f"⏭️  Parte {parte.id_parte_api} ya tiene horas calculadas")
                    continue
                
                # Calcular horas extras
                calculo = calcular_horas_extras(parte.fecha_inicio, parte.fecha_fin, db)
                
                # Crear registro
                db_horas = HorasExtras(
                    parte_trabajo_id=parte.id,
                    tecnico_id=parte.tecnico_id,
                    fecha=parte.fecha_inicio.date(),
                    hora_inicio=parte.fecha_inicio.time(),
                    hora_fin=parte.fecha_fin.time(),
                    horas_normales=calculo["horas_normales"],
                    horas_extras_normales=calculo["horas_extras_normales"],
                    horas_extras_especiales=calculo["horas_extras_especiales"],
                    tipo_dia=calculo["tipo_dia"],
                    calculado_automaticamente=True
                )
                
                db.add(db_horas)
                db.commit()
                
                print(f"✅ Parte {parte.id_parte_api}: {calculo['horas_normales']}h normales, "
                      f"{calculo['horas_extras_normales']}h extras, "
                      f"{calculo['horas_extras_especiales']}h especiales ({calculo['tipo_dia']})")
                
                calculados += 1
                
            except Exception as e:
                print(f"❌ Error calculando parte {parte.id_parte_api}: {e}")
                errores += 1
                db.rollback()
        
        print(f"\n📊 Resumen:")
        print(f"   Partes procesados: {len(partes)}")
        print(f"   Horas calculadas: {calculados}")
        print(f"   Errores: {errores}")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    calcular_todas_las_horas()
