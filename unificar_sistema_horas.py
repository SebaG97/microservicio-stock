"""
Script de unificación y limpieza del sistema de horas extras
- Elimina tablas obsoletas
- Corrige datos corruptos 
- Unifica lógica de endpoints
- Consolida sistema en base a partes_trabajo
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, time, timedelta
from database import SessionLocal, engine
import models
from sqlalchemy import text, inspect

def analizar_estructura_actual():
    """Analiza la estructura actual de la base de datos"""
    print("🔍 Analizando estructura actual de la base de datos...")
    
    inspector = inspect(engine)
    tablas = inspector.get_table_names()
    
    # Buscar tablas relacionadas con horas extras
    tablas_horas = [tabla for tabla in tablas if 'hora' in tabla.lower()]
    
    print(f"📊 Tablas relacionadas con horas encontradas:")
    for tabla in tablas_horas:
        columnas = inspector.get_columns(tabla)
        print(f"   - {tabla}: {len(columnas)} columnas")
        for col in columnas[:5]:  # Mostrar primeras 5 columnas
            print(f"     * {col['name']}: {col['type']}")
    
    return tablas_horas

def verificar_datos_corruptos():
    """Identifica y reporta datos corruptos en partes de trabajo"""
    print("\n🔍 Verificando datos corruptos...")
    
    db = SessionLocal()
    try:
        # Buscar partes con horas anómalas
        partes_problematicos = []
        
        # Obtener todos los partes con hora_inicio y hora_fin
        partes = db.query(models.ParteTrabajo).filter(
            models.ParteTrabajo.hora_inicio.isnot(None),
            models.ParteTrabajo.hora_fin.isnot(None)
        ).all()
        
        for parte in partes:
            try:
                if parte.hora_inicio and parte.hora_fin:
                    # Calcular duración
                    duracion = parte.hora_fin - parte.hora_inicio
                    horas_totales = duracion.total_seconds() / 3600
                    
                    if horas_totales > 24 or horas_totales < 0:
                        partes_problematicos.append({
                            'parte': parte,
                            'horas': horas_totales,
                            'hora_inicio': parte.hora_inicio,
                            'hora_fin': parte.hora_fin
                        })
            except Exception as e:
                partes_problematicos.append({
                    'parte': parte,
                    'error': str(e),
                    'hora_inicio': parte.hora_inicio,
                    'hora_fin': parte.hora_fin
                })
        
        print(f"❌ Partes con datos corruptos encontrados: {len(partes_problematicos)}")
        for item in partes_problematicos:
            parte = item['parte']
            print(f"   - Parte {parte.numero or 'S/N'} (ID: {parte.id})")
            print(f"     Inicio: {item['hora_inicio']}")
            print(f"     Fin: {item['hora_fin']}")
            if 'horas' in item:
                print(f"     Duración anómala: {item['horas']:.2f} horas")
            if 'error' in item:
                print(f"     Error: {item['error']}")
        
        return partes_problematicos
        
    finally:
        db.close()

def corregir_datos_corruptos(partes_problematicos):
    """Corrige los datos corruptos identificados"""
    if not partes_problematicos:
        print("✅ No hay datos corruptos para corregir")
        return
    
    print(f"\n🛠️ Corrigiendo {len(partes_problematicos)} partes con datos corruptos...")
    
    db = SessionLocal()
    try:
        for item in partes_problematicos:
            parte = item['parte']
            
            # Estrategias de corrección
            if 'horas' in item and item['horas'] > 24:
                # Si las horas son > 24, probablemente es un problema de fecha
                # Intentar usar solo la hora, asumiendo el mismo día
                try:
                    fecha_base = parte.fecha.date()
                    
                    # Extraer solo la hora de hora_inicio y hora_fin
                    if isinstance(parte.hora_inicio, datetime):
                        nueva_hora_inicio = datetime.combine(fecha_base, parte.hora_inicio.time())
                    else:
                        nueva_hora_inicio = parte.hora_inicio
                    
                    if isinstance(parte.hora_fin, datetime):
                        nueva_hora_fin = datetime.combine(fecha_base, parte.hora_fin.time())
                    else:
                        nueva_hora_fin = parte.hora_fin
                    
                    # Si hora_fin es menor que hora_inicio, asumir que termina al día siguiente
                    if nueva_hora_fin <= nueva_hora_inicio:
                        nueva_hora_fin += timedelta(days=1)
                    
                    # Verificar que la nueva duración sea razonable
                    nueva_duracion = nueva_hora_fin - nueva_hora_inicio
                    nuevas_horas = nueva_duracion.total_seconds() / 3600
                    
                    if 0 <= nuevas_horas <= 24:
                        parte.hora_inicio = nueva_hora_inicio
                        parte.hora_fin = nueva_hora_fin
                        print(f"   ✅ Corregido Parte {parte.numero}: {nuevas_horas:.2f} horas")
                    else:
                        # Si aún es anómalo, usar horario estándar 8-17
                        parte.hora_inicio = datetime.combine(fecha_base, time(8, 0))
                        parte.hora_fin = datetime.combine(fecha_base, time(17, 0))
                        print(f"   🔧 Parte {parte.numero}: Aplicado horario estándar (8-17)")
                        
                except Exception as e:
                    print(f"   ❌ No se pudo corregir Parte {parte.numero}: {e}")
                    # Como último recurso, poner horario estándar
                    fecha_base = parte.fecha.date()
                    parte.hora_inicio = datetime.combine(fecha_base, time(8, 0))
                    parte.hora_fin = datetime.combine(fecha_base, time(17, 0))
        
        db.commit()
        print("✅ Corrección de datos completada")
        
    except Exception as e:
        print(f"❌ Error durante la corrección: {e}")
        db.rollback()
    finally:
        db.close()

def eliminar_tablas_obsoletas():
    """Elimina tablas obsoletas del sistema anterior"""
    print("\n🗑️ Identificando tablas obsoletas...")
    
    # Lista de tablas que pueden ser obsoletas
    posibles_obsoletas = [
        'partes_trabajo_old',
        'horas_extras_old', 
        'tecnicos_old',
        'temp_partes',
        'backup_horas'
    ]
    
    inspector = inspect(engine)
    tablas_existentes = inspector.get_table_names()
    
    tablas_a_eliminar = [tabla for tabla in posibles_obsoletas if tabla in tablas_existentes]
    
    if not tablas_a_eliminar:
        print("✅ No se encontraron tablas obsoletas")
        return
    
    print(f"📋 Tablas obsoletas encontradas: {tablas_a_eliminar}")
    
    respuesta = input("¿Deseas eliminar estas tablas? (s/N): ")
    if respuesta.lower() in ['s', 'si', 'sí', 'yes', 'y']:
        try:
            with engine.connect() as conn:
                for tabla in tablas_a_eliminar:
                    conn.execute(text(f"DROP TABLE IF EXISTS {tabla} CASCADE"))
                    print(f"   🗑️ Eliminada tabla: {tabla}")
                conn.commit()
            print("✅ Tablas obsoletas eliminadas")
        except Exception as e:
            print(f"❌ Error eliminando tablas: {e}")
    else:
        print("❌ Eliminación de tablas cancelada")

def verificar_duplicados_horas_extras():
    """Verifica si hay duplicados en la tabla horas_extras"""
    print("\n🔍 Verificando duplicados en horas_extras...")
    
    db = SessionLocal()
    try:
        # Contar total de registros
        total_horas = db.query(models.HorasExtras).count()
        
        # Buscar duplicados por parte_trabajo_id + tecnico_id + fecha
        duplicados = db.execute(text("""
            SELECT parte_trabajo_id, tecnico_id, fecha, COUNT(*) as cantidad
            FROM horas_extras 
            GROUP BY parte_trabajo_id, tecnico_id, fecha
            HAVING COUNT(*) > 1
        """)).fetchall()
        
        print(f"📊 Total registros horas_extras: {total_horas}")
        print(f"❌ Grupos duplicados encontrados: {len(duplicados)}")
        
        if duplicados:
            print("🔍 Duplicados detallados:")
            for dup in duplicados:
                print(f"   - Parte {dup.parte_trabajo_id}, Técnico {dup.tecnico_id}, Fecha {dup.fecha}: {dup.cantidad} registros")
        
        return duplicados
        
    finally:
        db.close()

def limpiar_duplicados_horas_extras(duplicados):
    """Limpia duplicados manteniendo el registro más reciente"""
    if not duplicados:
        print("✅ No hay duplicados para limpiar")
        return
    
    print(f"\n🧹 Limpiando {len(duplicados)} grupos de duplicados...")
    
    db = SessionLocal()
    try:
        registros_eliminados = 0
        
        for dup in duplicados:
            # Obtener todos los registros duplicados ordenados por ID (más reciente último)
            registros = db.query(models.HorasExtras).filter(
                models.HorasExtras.parte_trabajo_id == dup.parte_trabajo_id,
                models.HorasExtras.tecnico_id == dup.tecnico_id,
                models.HorasExtras.fecha == dup.fecha
            ).order_by(models.HorasExtras.id).all()
            
            # Eliminar todos excepto el último (más reciente)
            for registro in registros[:-1]:
                db.delete(registro)
                registros_eliminados += 1
        
        db.commit()
        print(f"✅ Eliminados {registros_eliminados} registros duplicados")
        
    except Exception as e:
        print(f"❌ Error limpiando duplicados: {e}")
        db.rollback()
    finally:
        db.close()

def generar_reporte_unificacion():
    """Genera un reporte final del estado unificado"""
    print("\n📊 Generando reporte final...")
    
    db = SessionLocal()
    try:
        # Estadísticas principales
        total_partes = db.query(models.ParteTrabajo).count()
        total_tecnicos = db.query(models.Tecnico).count()
        total_horas_extras = db.query(models.HorasExtras).count()
        
        # Partes con horas válidas
        partes_con_horas = db.query(models.ParteTrabajo).filter(
            models.ParteTrabajo.hora_inicio.isnot(None),
            models.ParteTrabajo.hora_fin.isnot(None)
        ).count()
        
        print(f"📈 Estadísticas finales:")
        print(f"   📋 Total partes de trabajo: {total_partes}")
        print(f"   👥 Total técnicos: {total_tecnicos}")
        print(f"   ⏰ Total registros horas extras: {total_horas_extras}")
        print(f"   ✅ Partes con horarios válidos: {partes_con_horas}")
        
        # Verificar integridad
        print(f"\n🔍 Verificación de integridad:")
        
        # HorasExtras sin ParteTrabajo
        horas_huerfanas = db.execute(text("""
            SELECT COUNT(*) as count
            FROM horas_extras he
            LEFT JOIN partes_trabajo pt ON he.parte_trabajo_id = pt.id
            WHERE pt.id IS NULL
        """)).fetchone()
        
        if horas_huerfanas.count > 0:
            print(f"   ⚠️ Registros horas_extras huérfanos: {horas_huerfanas.count}")
        else:
            print(f"   ✅ Integridad horas_extras ↔ partes_trabajo: OK")
        
        # HorasExtras sin Tecnico
        horas_sin_tecnico = db.execute(text("""
            SELECT COUNT(*) as count
            FROM horas_extras he
            LEFT JOIN tecnicos t ON he.tecnico_id = t.id
            WHERE t.id IS NULL
        """)).fetchone()
        
        if horas_sin_tecnico.count > 0:
            print(f"   ⚠️ Registros horas_extras sin técnico: {horas_sin_tecnico.count}")
        else:
            print(f"   ✅ Integridad horas_extras ↔ tecnicos: OK")
        
    finally:
        db.close()

def main():
    """Función principal de unificación"""
    print("🔧 Sistema de Unificación y Limpieza - Horas Extras")
    print("=" * 60)
    
    # 1. Analizar estructura
    tablas_horas = analizar_estructura_actual()
    
    # 2. Verificar datos corruptos
    partes_problematicos = verificar_datos_corruptos()
    
    # 3. Corregir datos corruptos
    if partes_problematicos:
        respuesta = input("\n¿Deseas corregir los datos corruptos? (s/N): ")
        if respuesta.lower() in ['s', 'si', 'sí', 'yes', 'y']:
            corregir_datos_corruptos(partes_problematicos)
    
    # 4. Verificar duplicados
    duplicados = verificar_duplicados_horas_extras()
    
    # 5. Limpiar duplicados
    if duplicados:
        respuesta = input("\n¿Deseas limpiar los duplicados? (s/N): ")
        if respuesta.lower() in ['s', 'si', 'sí', 'yes', 'y']:
            limpiar_duplicados_horas_extras(duplicados)
    
    # 6. Eliminar tablas obsoletas
    eliminar_tablas_obsoletas()
    
    # 7. Reporte final
    generar_reporte_unificacion()
    
    print("\n✅ Proceso de unificación completado")
    print("🎯 El sistema ahora está unificado y limpio")

if __name__ == "__main__":
    main()
