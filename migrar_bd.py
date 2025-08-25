#!/usr/bin/env python3
"""
Script para migrar la base de datos a la nueva estructura que soporta:
- Múltiples técnicos por parte de trabajo
- Campo número y ejercicio
- Campos adicionales del JSON de la API
"""

import os
import sqlite3
from database import engine, get_db
from models import Base, ParteTrabajo, Tecnico
from sqlalchemy.orm import Session

def migrar_base_datos():
    """Migra la base de datos a la nueva estructura"""
    
    print("🔄 Iniciando migración de base de datos...")
    
    # Hacer backup de la base de datos actual
    if os.path.exists("stock.db"):
        print("📦 Creando backup de la base de datos...")
        os.system("cp stock.db stock_backup.db")
        print("✅ Backup creado: stock_backup.db")
    
    # Conectar a la base de datos SQLite directamente para migraciones
    conn = sqlite3.connect("stock.db")
    cursor = conn.cursor()
    
    try:
        # 1. Verificar si ya existen las nuevas columnas en partes_trabajo
        cursor.execute("PRAGMA table_info(partes_trabajo)")
        columnas_actuales = [col[1] for col in cursor.fetchall()]
        print(f"📋 Columnas actuales en partes_trabajo: {columnas_actuales}")
        
        # 2. Agregar nuevas columnas a la tabla partes_trabajo si no existen
        nuevas_columnas = [
            ("numero", "INTEGER"),
            ("ejercicio", "TEXT"),
            ("fecha", "TEXT"),  # Renombrado de fecha_inicio
            ("hora_inicio", "TEXT"),
            ("hora_fin", "TEXT"),
            ("kilometraje", "REAL"),
            ("trabajo_solicitado", "TEXT"),
            ("notas", "TEXT"),
            ("notas_internas", "TEXT"),
            ("notas_internas_administracion", "TEXT"),
            ("estado", "INTEGER"),
            ("dni_firma", "TEXT"),
            ("persona_firmante", "TEXT"),
            ("firmado", "BOOLEAN DEFAULT 0"),
            ("archivado", "BOOLEAN DEFAULT 0"),
            ("cliente_codigo_interno", "TEXT"),
            ("cliente_cif", "TEXT"),
            ("cliente_direccion", "TEXT"),
            ("cliente_provincia", "TEXT"),
            ("cliente_localidad", "TEXT"),
            ("cliente_pais", "TEXT"),
            ("cliente_telefono", "TEXT"),
            ("cliente_email", "TEXT"),
            ("cliente_erp_id", "TEXT"),
            ("proyecto_id", "TEXT"),
            ("erp_id", "TEXT")
        ]
        
        for columna, tipo in nuevas_columnas:
            if columna not in columnas_actuales:
                try:
                    cursor.execute(f"ALTER TABLE partes_trabajo ADD COLUMN {columna} {tipo}")
                    print(f"✅ Agregada columna: {columna}")
                except sqlite3.OperationalError as e:
                    print(f"⚠️  Error agregando columna {columna}: {e}")
        
        # 3. Agregar nuevas columnas a la tabla tecnicos si no existen
        cursor.execute("PRAGMA table_info(tecnicos)")
        columnas_tecnicos = [col[1] for col in cursor.fetchall()]
        print(f"📋 Columnas actuales en tecnicos: {columnas_tecnicos}")
        
        nuevas_columnas_tecnicos = [
            ("email", "TEXT UNIQUE"),
            ("tipocuenta", "INTEGER")
        ]
        
        for columna, tipo in nuevas_columnas_tecnicos:
            if columna not in columnas_tecnicos:
                try:
                    cursor.execute(f"ALTER TABLE tecnicos ADD COLUMN {columna} {tipo}")
                    print(f"✅ Agregada columna a tecnicos: {columna}")
                except sqlite3.OperationalError as e:
                    print(f"⚠️  Error agregando columna {columna} a tecnicos: {e}")
        
        # 4. Crear tabla de asociación parte_trabajo_tecnicos si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parte_trabajo_tecnicos (
                parte_trabajo_id INTEGER,
                tecnico_id INTEGER,
                PRIMARY KEY (parte_trabajo_id, tecnico_id),
                FOREIGN KEY (parte_trabajo_id) REFERENCES partes_trabajo (id),
                FOREIGN KEY (tecnico_id) REFERENCES tecnicos (id)
            )
        """)
        print("✅ Tabla parte_trabajo_tecnicos creada/verificada")
        
        # 5. Migrar datos existentes de tecnico_id a la nueva tabla de asociación
        cursor.execute("SELECT id, tecnico_id FROM partes_trabajo WHERE tecnico_id IS NOT NULL")
        partes_con_tecnico = cursor.fetchall()
        
        for parte_id, tecnico_id in partes_con_tecnico:
            cursor.execute("""
                INSERT OR IGNORE INTO parte_trabajo_tecnicos (parte_trabajo_id, tecnico_id)
                VALUES (?, ?)
            """, (parte_id, tecnico_id))
        
        print(f"✅ Migrados {len(partes_con_tecnico)} registros a parte_trabajo_tecnicos")
        
        # 6. Actualizar fecha_inicio a fecha si existe
        if "fecha_inicio" in columnas_actuales:
            cursor.execute("UPDATE partes_trabajo SET fecha = fecha_inicio WHERE fecha IS NULL")
            print("✅ Migrado fecha_inicio a fecha")
        
        conn.commit()
        print("✅ Migración completada exitosamente")
        
        # 7. Mostrar estadísticas
        cursor.execute("SELECT COUNT(*) FROM partes_trabajo")
        total_partes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tecnicos")
        total_tecnicos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM parte_trabajo_tecnicos")
        total_asignaciones = cursor.fetchone()[0]
        
        print(f"\n📊 Estadísticas de la base de datos:")
        print(f"   - Partes de trabajo: {total_partes}")
        print(f"   - Técnicos: {total_tecnicos}")
        print(f"   - Asignaciones técnico-parte: {total_asignaciones}")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
    
    # 8. Recrear las tablas con SQLAlchemy para asegurar consistencia
    print("\n🔄 Recreando estructura con SQLAlchemy...")
    Base.metadata.create_all(bind=engine)
    print("✅ Estructura actualizada con SQLAlchemy")

if __name__ == "__main__":
    migrar_base_datos()
    print("\n🎉 Migración completada. La base de datos está lista para almacenar múltiples técnicos por parte de trabajo.")
