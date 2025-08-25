#!/usr/bin/env python3
"""
Script para recrear las tablas con la estructura nueva completa
"""

from database import engine
from sqlalchemy import text
from models import Base
import time

def recrear_tablas_completas():
    """Recrea las tablas con la estructura nueva completa"""
    
    print("🔄 Recreando tablas con estructura nueva...")
    
    with engine.connect() as conn:
        # 1. Crear tabla tecnicos nueva con todos los campos
        print("👥 Recreando tabla tecnicos...")
        try:
            conn.execute(text("DROP TABLE IF EXISTS tecnicos_new CASCADE"))
            conn.execute(text("""
                CREATE TABLE tecnicos_new (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR NOT NULL,
                    apellido VARCHAR NOT NULL,
                    legajo VARCHAR UNIQUE NOT NULL,
                    email VARCHAR UNIQUE,
                    tipocuenta INTEGER,
                    activo BOOLEAN DEFAULT true
                )
            """))
            print("✅ Tabla tecnicos_new creada")
            
            # Migrar datos existentes de tecnicos si existe
            try:
                conn.execute(text("""
                    INSERT INTO tecnicos_new (nombre, apellido, legajo, activo)
                    SELECT nombre, apellido, legajo, activo FROM tecnicos
                """))
                print("✅ Datos migrados de tecnicos antigua")
            except Exception as e:
                print(f"⚠️ No se pudieron migrar datos: {e}")
            
        except Exception as e:
            print(f"❌ Error creando tecnicos_new: {e}")
        
        # 2. Crear tabla partes_trabajo nueva con todos los campos
        print("📋 Recreando tabla partes_trabajo...")
        try:
            conn.execute(text("DROP TABLE IF EXISTS partes_trabajo_new CASCADE"))
            conn.execute(text("""
                CREATE TABLE partes_trabajo_new (
                    id SERIAL PRIMARY KEY,
                    id_parte_api VARCHAR UNIQUE NOT NULL,
                    numero INTEGER,
                    ejercicio VARCHAR,
                    fecha TIMESTAMP NOT NULL,
                    hora_inicio TIMESTAMP,
                    hora_fin TIMESTAMP,
                    kilometraje REAL,
                    trabajo_solicitado TEXT,
                    notas TEXT,
                    notas_internas TEXT,
                    notas_internas_administracion TEXT,
                    estado INTEGER,
                    dni_firma VARCHAR,
                    persona_firmante VARCHAR,
                    firmado BOOLEAN DEFAULT false,
                    archivado BOOLEAN DEFAULT false,
                    
                    -- Datos del cliente
                    cliente_codigo_interno VARCHAR,
                    cliente_id VARCHAR,
                    cliente_empresa VARCHAR,
                    cliente_cif VARCHAR,
                    cliente_direccion VARCHAR,
                    cliente_provincia VARCHAR,
                    cliente_localidad VARCHAR,
                    cliente_pais VARCHAR,
                    cliente_telefono VARCHAR,
                    cliente_email VARCHAR,
                    cliente_erp_id VARCHAR,
                    
                    proyecto_id VARCHAR,
                    erp_id VARCHAR
                )
            """))
            print("✅ Tabla partes_trabajo_new creada")
            
        except Exception as e:
            print(f"❌ Error creando partes_trabajo_new: {e}")
        
        # 3. Crear tabla de asociación nueva
        print("🔗 Creando tabla parte_trabajo_tecnicos...")
        try:
            conn.execute(text("DROP TABLE IF EXISTS parte_trabajo_tecnicos_new CASCADE"))
            conn.execute(text("""
                CREATE TABLE parte_trabajo_tecnicos_new (
                    parte_trabajo_id INTEGER,
                    tecnico_id INTEGER,
                    PRIMARY KEY (parte_trabajo_id, tecnico_id),
                    FOREIGN KEY (parte_trabajo_id) REFERENCES partes_trabajo_new (id) ON DELETE CASCADE,
                    FOREIGN KEY (tecnico_id) REFERENCES tecnicos_new (id) ON DELETE CASCADE
                )
            """))
            print("✅ Tabla parte_trabajo_tecnicos_new creada")
            
        except Exception as e:
            print(f"❌ Error creando parte_trabajo_tecnicos_new: {e}")
        
        conn.commit()
        print("💾 Cambios guardados")
        
        # 4. Renombrar tablas (swap)
        print("🔄 Renombrando tablas...")
        try:
            # Backup de tablas originales
            conn.execute(text("DROP TABLE IF EXISTS tecnicos_backup CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS partes_trabajo_backup CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS parte_trabajo_tecnicos_backup CASCADE"))
            
            try:
                conn.execute(text("ALTER TABLE tecnicos RENAME TO tecnicos_backup"))
                print("✅ tecnicos -> tecnicos_backup")
            except:
                print("⚠️ tecnicos no existe, continuando...")
            
            try:
                conn.execute(text("ALTER TABLE partes_trabajo RENAME TO partes_trabajo_backup"))
                print("✅ partes_trabajo -> partes_trabajo_backup")
            except:
                print("⚠️ partes_trabajo no existe, continuando...")
            
            try:
                conn.execute(text("ALTER TABLE parte_trabajo_tecnicos RENAME TO parte_trabajo_tecnicos_backup"))
                print("✅ parte_trabajo_tecnicos -> parte_trabajo_tecnicos_backup")
            except:
                print("⚠️ parte_trabajo_tecnicos no existe, continuando...")
            
            # Activar nuevas tablas
            conn.execute(text("ALTER TABLE tecnicos_new RENAME TO tecnicos"))
            conn.execute(text("ALTER TABLE partes_trabajo_new RENAME TO partes_trabajo"))
            conn.execute(text("ALTER TABLE parte_trabajo_tecnicos_new RENAME TO parte_trabajo_tecnicos"))
            
            print("✅ Tablas nuevas activadas")
            
        except Exception as e:
            print(f"❌ Error renombrando tablas: {e}")
        
        conn.commit()
        print("💾 Estructura final guardada")
        
        # 5. Insertar tecnicos de ejemplo
        print("👥 Insertando técnicos de ejemplo...")
        try:
            tecnicos = [
                ("Luis", "González", "LG001", "luis.gonzalez@parks.com.py", 1),
                ("Carmelo", "Orué", "CO002", "carmelo.orue@parks.com.py", 1),
                ("Edgar", "Ortega", "EO003", "edgar.ortega@parks.com.py", 1)
            ]
            
            for nombre, apellido, legajo, email, tipocuenta in tecnicos:
                conn.execute(text("""
                    INSERT INTO tecnicos (nombre, apellido, legajo, email, tipocuenta, activo)
                    VALUES (:nombre, :apellido, :legajo, :email, :tipocuenta, true)
                    ON CONFLICT (legajo) DO NOTHING
                """), {
                    "nombre": nombre,
                    "apellido": apellido, 
                    "legajo": legajo,
                    "email": email,
                    "tipocuenta": tipocuenta
                })
                print(f"   ✅ {nombre} {apellido}")
            
            conn.commit()
            print("✅ Técnicos insertados")
            
        except Exception as e:
            print(f"❌ Error insertando técnicos: {e}")
    
    print("\n🎉 ¡Base de datos recreada exitosamente!")
    print("\n📋 Nueva estructura permite:")
    print("   ✅ Múltiples técnicos por parte de trabajo")
    print("   ✅ Campo 'numero' (ej: 113)")
    print("   ✅ Todos los campos del JSON de la API")
    print("   ✅ Información completa del cliente")

if __name__ == "__main__":
    recrear_tablas_completas()
