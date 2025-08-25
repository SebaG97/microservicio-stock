#!/usr/bin/env python3
"""
Script para inicializar/recrear la base de datos con la nueva estructura 
que soporta múltiples técnicos por parte de trabajo
"""

from database import engine, get_db
from models import Base, ParteTrabajo, Tecnico, parte_trabajo_tecnicos
from sqlalchemy.orm import Session
from sqlalchemy import text
import os

def recrear_base_datos():
    """Recrea la base de datos con la nueva estructura"""
    
    print("🔄 Inicializando base de datos con nueva estructura...")
    
    try:
        # Crear todas las tablas según los modelos actualizados
        print("📋 Creando tablas con SQLAlchemy...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente")
        
        # Verificar que las tablas se crearon correctamente
        with engine.connect() as conn:
            # Verificar tabla partes_trabajo
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'partes_trabajo'
                ORDER BY ordinal_position
            """))
            columnas_partes = result.fetchall()
            
            print(f"\n📋 Columnas en partes_trabajo ({len(columnas_partes)}):")
            for col in columnas_partes:
                print(f"   - {col[0]}: {col[1]}")
            
            # Verificar tabla tecnicos
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'tecnicos'
                ORDER BY ordinal_position
            """))
            columnas_tecnicos = result.fetchall()
            
            print(f"\n📋 Columnas en tecnicos ({len(columnas_tecnicos)}):")
            for col in columnas_tecnicos:
                print(f"   - {col[0]}: {col[1]}")
            
            # Verificar tabla de asociación
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'parte_trabajo_tecnicos'
                ORDER BY ordinal_position
            """))
            columnas_asociacion = result.fetchall()
            
            print(f"\n📋 Columnas en parte_trabajo_tecnicos ({len(columnas_asociacion)}):")
            for col in columnas_asociacion:
                print(f"   - {col[0]}: {col[1]}")
        
        # Insertar algunos técnicos de ejemplo basados en el JSON que proporcionaste
        print("\n👥 Insertando técnicos de ejemplo...")
        db = next(get_db())
        try:
            tecnicos_ejemplo = [
                Tecnico(
                    nombre="Luis",
                    apellido="González", 
                    legajo="LG001",
                    email="luis.gonzalez@parks.com.py",
                    tipocuenta=1,
                    activo=True
                ),
                Tecnico(
                    nombre="Carmelo",
                    apellido="Orué",
                    legajo="CO002", 
                    email="carmelo.orue@parks.com.py",
                    tipocuenta=1,
                    activo=True
                ),
                Tecnico(
                    nombre="Edgar",
                    apellido="Ortega",
                    legajo="EO003",
                    email="edgar.ortega@parks.com.py", 
                    tipocuenta=1,
                    activo=True
                )
            ]
            
            for tecnico in tecnicos_ejemplo:
                # Verificar si ya existe
                existing = db.query(Tecnico).filter(Tecnico.email == tecnico.email).first()
                if not existing:
                    db.add(tecnico)
                    print(f"   ✅ Agregado: {tecnico.nombre} {tecnico.apellido}")
                else:
                    print(f"   ⚠️  Ya existe: {tecnico.nombre} {tecnico.apellido}")
            
            db.commit()
            print("✅ Técnicos de ejemplo insertados")
            
        except Exception as e:
            print(f"❌ Error insertando técnicos: {e}")
            db.rollback()
        finally:
            db.close()
        
        print("\n🎉 Base de datos inicializada correctamente!")
        print("\n📋 La nueva estructura permite:")
        print("   ✅ Múltiples técnicos por parte de trabajo")
        print("   ✅ Campo 'numero' para el número del parte")
        print("   ✅ Campos completos según el JSON de la API")
        print("   ✅ Información completa del cliente")
        print("   ✅ Coordenadas y timestamps")
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        raise

if __name__ == "__main__":
    recrear_base_datos()
