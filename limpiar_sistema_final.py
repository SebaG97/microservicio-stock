"""
Script para limpiar registros huérfanos y unificar endpoints
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
import models
from sqlalchemy import text

def limpiar_registros_huerfanos():
    """Limpia registros de horas_extras que no tienen parte_trabajo correspondiente"""
    print("🧹 Limpiando registros huérfanos de horas_extras...")
    
    db = SessionLocal()
    try:
        # Contar huérfanos antes
        huerfanos_antes = db.execute(text("""
            SELECT COUNT(*) as count
            FROM horas_extras he
            LEFT JOIN partes_trabajo pt ON he.parte_trabajo_id = pt.id
            WHERE pt.id IS NULL
        """)).fetchone()
        
        print(f"❌ Registros huérfanos encontrados: {huerfanos_antes.count}")
        
        if huerfanos_antes.count > 0:
            respuesta = input("¿Deseas eliminar estos registros huérfanos? (s/N): ")
            if respuesta.lower() in ['s', 'si', 'sí', 'yes', 'y']:
                # Eliminar registros huérfanos
                resultado = db.execute(text("""
                    DELETE FROM horas_extras 
                    WHERE parte_trabajo_id NOT IN (
                        SELECT id FROM partes_trabajo
                    )
                """))
                
                db.commit()
                print(f"✅ Eliminados {resultado.rowcount} registros huérfanos")
            else:
                print("❌ Limpieza cancelada")
        else:
            print("✅ No hay registros huérfanos para limpiar")
            
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        db.rollback()
    finally:
        db.close()

def recalcular_horas_extras_todas():
    """Recalcula las horas extras para todos los partes de trabajo"""
    print("\n🔄 Recalculando horas extras para todos los partes...")
    
    db = SessionLocal()
    try:
        # Primero, limpiar todas las horas extras existentes
        db.execute(text("DELETE FROM horas_extras"))
        
        # Obtener todos los partes con horarios válidos
        partes = db.query(models.ParteTrabajo).filter(
            models.ParteTrabajo.hora_inicio.isnot(None),
            models.ParteTrabajo.hora_fin.isnot(None)
        ).all()
        
        print(f"📊 Recalculando para {len(partes)} partes de trabajo...")
        
        creados = 0
        errores = 0
        
        for parte in partes:
            try:
                # Obtener técnicos asignados a este parte
                for tecnico in parte.tecnicos:
                    # Calcular duración y tipo de día
                    duracion = parte.hora_fin - parte.hora_inicio
                    horas_totales = duracion.total_seconds() / 3600
                    
                    # Validar duración
                    if horas_totales <= 0 or horas_totales > 24:
                        print(f"⚠️ Saltando parte {parte.numero}: duración anómala {horas_totales:.2f}h")
                        continue
                    
                    # Determinar tipo de día
                    dia_semana = parte.fecha.weekday()  # 0=lunes, 6=domingo
                    if dia_semana == 6:  # domingo
                        tipo_dia = "domingo"
                    elif dia_semana == 5:  # sábado
                        tipo_dia = "sabado"
                    else:
                        tipo_dia = "laboral"
                    
                    # Calcular horas normales y extras (lógica simplificada)
                    horas_normales = min(8, horas_totales)  # Máximo 8 horas normales
                    horas_extras_normales = max(0, horas_totales - 8)
                    horas_extras_especiales = 0
                    
                    # En domingo o días especiales, todas son extras especiales
                    if tipo_dia in ["domingo", "feriado"]:
                        horas_extras_especiales = horas_totales
                        horas_extras_normales = 0
                        horas_normales = 0
                    
                    # Crear registro de horas extras
                    nueva_hora_extra = models.HorasExtras(
                        parte_trabajo_id=parte.id,
                        tecnico_id=tecnico.id,
                        fecha=parte.fecha.date(),
                        hora_inicio=parte.hora_inicio.time(),
                        hora_fin=parte.hora_fin.time(),
                        horas_normales=horas_normales,
                        horas_extras_normales=horas_extras_normales,
                        horas_extras_especiales=horas_extras_especiales,
                        tipo_dia=tipo_dia,
                        calculado_automaticamente=True
                    )
                    
                    db.add(nueva_hora_extra)
                    creados += 1
                    
            except Exception as e:
                print(f"❌ Error procesando parte {parte.numero}: {e}")
                errores += 1
                continue
        
        db.commit()
        print(f"✅ Recálculo completado:")
        print(f"   📝 Registros creados: {creados}")
        print(f"   ❌ Errores: {errores}")
        
    except Exception as e:
        print(f"❌ Error durante el recálculo: {e}")
        db.rollback()
    finally:
        db.close()

def verificar_consistencia_final():
    """Verifica la consistencia final del sistema"""
    print("\n🔍 Verificando consistencia final...")
    
    db = SessionLocal()
    try:
        # Estadísticas básicas
        total_partes = db.query(models.ParteTrabajo).count()
        total_horas_extras = db.query(models.HorasExtras).count()
        
        # Verificar integridad
        huerfanos = db.execute(text("""
            SELECT COUNT(*) as count
            FROM horas_extras he
            LEFT JOIN partes_trabajo pt ON he.parte_trabajo_id = pt.id
            WHERE pt.id IS NULL
        """)).fetchone()
        
        # Verificar duplicados
        duplicados = db.execute(text("""
            SELECT COUNT(*) as count
            FROM (
                SELECT parte_trabajo_id, tecnico_id, fecha, COUNT(*) as cnt
                FROM horas_extras 
                GROUP BY parte_trabajo_id, tecnico_id, fecha
                HAVING COUNT(*) > 1
            ) as dups
        """)).fetchone()
        
        print(f"📊 Estado final del sistema:")
        print(f"   📋 Total partes de trabajo: {total_partes}")
        print(f"   ⏰ Total registros horas extras: {total_horas_extras}")
        print(f"   🔗 Registros huérfanos: {huerfanos.count}")
        print(f"   🔄 Duplicados: {duplicados.count}")
        
        if huerfanos.count == 0 and duplicados.count == 0:
            print("✅ Sistema completamente consistente")
        else:
            print("⚠️ Aún hay inconsistencias que requieren atención")
            
    finally:
        db.close()

def main():
    """Función principal"""
    print("🔧 Limpieza Final del Sistema de Horas Extras")
    print("=" * 50)
    
    # 1. Limpiar huérfanos
    limpiar_registros_huerfanos()
    
    # 2. Preguntar si recalcular todo
    respuesta = input("\n¿Deseas recalcular todas las horas extras desde cero? (s/N): ")
    if respuesta.lower() in ['s', 'si', 'sí', 'yes', 'y']:
        recalcular_horas_extras_todas()
    
    # 3. Verificar consistencia final
    verificar_consistencia_final()
    
    print("\n✅ Limpieza final completada")

if __name__ == "__main__":
    main()
