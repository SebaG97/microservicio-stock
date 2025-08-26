"""
Script final para recalcular horas extras con la estructura corregida
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, time, timedelta
from database import SessionLocal
import models
from sqlalchemy import text

def recalcular_horas_extras_corregido():
    """Recalcula las horas extras para todos los partes de trabajo con lógica mejorada"""
    print("🔄 Recalculando horas extras con estructura corregida...")
    
    db = SessionLocal()
    try:
        # Limpiar todas las horas extras existentes
        db.execute(text("DELETE FROM horas_extras"))
        db.commit()
        
        # Obtener todos los partes con horarios válidos
        partes = db.query(models.ParteTrabajo).filter(
            models.ParteTrabajo.hora_inicio.isnot(None),
            models.ParteTrabajo.hora_fin.isnot(None)
        ).all()
        
        print(f"📊 Procesando {len(partes)} partes de trabajo...")
        
        creados = 0
        saltados = 0
        errores = 0
        
        for parte in partes:
            try:
                # Validar duración básica
                duracion = parte.hora_fin - parte.hora_inicio
                horas_totales = duracion.total_seconds() / 3600
                
                # Saltar partes con duración anómala
                if horas_totales <= 0 or horas_totales > 24:
                    print(f"⚠️ Saltando parte {parte.numero}: duración anómala {horas_totales:.2f}h")
                    saltados += 1
                    continue
                
                # Procesar cada técnico asignado
                for tecnico in parte.tecnicos:
                    # Determinar tipo de día
                    dia_semana = parte.fecha.weekday()  # 0=lunes, 6=domingo
                    if dia_semana == 6:  # domingo
                        tipo_dia = "domingo"
                    elif dia_semana == 5:  # sábado
                        tipo_dia = "sabado"
                    else:
                        tipo_dia = "laboral"
                    
                    # Calcular horas normales y extras
                    if tipo_dia == "laboral":
                        # Lunes a viernes: 8 horas normales máximo
                        horas_normales = min(8, horas_totales)
                        horas_extras_normales = max(0, horas_totales - 8)
                        horas_extras_especiales = 0
                    elif tipo_dia == "sabado":
                        # Sábado: 4 horas normales máximo
                        horas_normales = min(4, horas_totales)
                        horas_extras_normales = max(0, horas_totales - 4)
                        horas_extras_especiales = 0
                    else:  # domingo
                        # Domingo: todas son horas extras especiales
                        horas_normales = 0
                        horas_extras_normales = 0
                        horas_extras_especiales = horas_totales
                    
                    # Crear registro de horas extras
                    nueva_hora_extra = models.HorasExtras(
                        parte_trabajo_id=parte.id,
                        tecnico_id=tecnico.id,
                        fecha=parte.fecha.date(),
                        hora_inicio=parte.hora_inicio.time(),
                        hora_fin=parte.hora_fin.time(),
                        horas_normales=round(horas_normales, 2),
                        horas_extras_normales=round(horas_extras_normales, 2),
                        horas_extras_especiales=round(horas_extras_especiales, 2),
                        tipo_dia=tipo_dia,
                        calculado_automaticamente=True
                    )
                    
                    db.add(nueva_hora_extra)
                    creados += 1
                    
                # Commit cada 20 partes para evitar transacciones muy largas
                if creados % 40 == 0:
                    db.commit()
                    print(f"📈 Procesados {creados} registros...")
                    
            except Exception as e:
                print(f"❌ Error procesando parte {parte.numero}: {e}")
                errores += 1
                continue
        
        # Commit final
        db.commit()
        
        print(f"\n✅ Recálculo completado:")
        print(f"   📝 Registros creados: {creados}")
        print(f"   ⏭️ Partes saltados: {saltados}")
        print(f"   ❌ Errores: {errores}")
        
        return creados, saltados, errores
        
    except Exception as e:
        print(f"❌ Error durante el recálculo: {e}")
        db.rollback()
        return 0, 0, 1
    finally:
        db.close()

def generar_reporte_horas_extras():
    """Genera un reporte detallado de las horas extras calculadas"""
    print("\n📊 Generando reporte de horas extras...")
    
    db = SessionLocal()
    try:
        # Estadísticas por tipo de día
        stats = db.execute(text("""
            SELECT 
                tipo_dia,
                COUNT(*) as registros,
                SUM(horas_normales) as total_normales,
                SUM(horas_extras_normales) as total_extras_normales,
                SUM(horas_extras_especiales) as total_extras_especiales
            FROM horas_extras
            GROUP BY tipo_dia
            ORDER BY tipo_dia
        """)).fetchall()
        
        print("📈 Estadísticas por tipo de día:")
        for stat in stats:
            print(f"   {stat.tipo_dia.capitalize()}:")
            print(f"     - Registros: {stat.registros}")
            print(f"     - Horas normales: {stat.total_normales:.2f}")
            print(f"     - Horas extras normales: {stat.total_extras_normales:.2f}")
            print(f"     - Horas extras especiales: {stat.total_extras_especiales:.2f}")
        
        # Top técnicos con más horas extras
        top_tecnicos = db.execute(text("""
            SELECT 
                t.nombre,
                t.apellido,
                COUNT(he.id) as partes_trabajados,
                SUM(he.horas_extras_normales + he.horas_extras_especiales) as total_horas_extras
            FROM horas_extras he
            JOIN tecnicos t ON he.tecnico_id = t.id
            GROUP BY t.id, t.nombre, t.apellido
            ORDER BY total_horas_extras DESC
            LIMIT 10
        """)).fetchall()
        
        print(f"\n👥 Top 10 técnicos con más horas extras:")
        for i, tecnico in enumerate(top_tecnicos, 1):
            print(f"   {i:2}. {tecnico.nombre} {tecnico.apellido}: {tecnico.total_horas_extras:.2f}h ({tecnico.partes_trabajados} partes)")
        
    finally:
        db.close()

def main():
    """Función principal"""
    print("🔧 Recálculo Final de Horas Extras")
    print("=" * 40)
    
    # 1. Recalcular horas extras
    creados, saltados, errores = recalcular_horas_extras_corregido()
    
    # 2. Generar reporte si se crearon registros
    if creados > 0:
        generar_reporte_horas_extras()
    
    print(f"\n🎯 Resumen final:")
    print(f"   ✅ Registros creados: {creados}")
    print(f"   ⏭️ Partes saltados: {saltados}")
    print(f"   ❌ Errores: {errores}")
    
    if errores == 0 and creados > 0:
        print("\n🎉 Sistema de horas extras unificado y funcional!")
    else:
        print("\n⚠️ Revisa los errores reportados")

if __name__ == "__main__":
    main()
