"""
Script de migración para el módulo de Caja Chica

Este script:
1. Agrega el campo RUC a la tabla proveedores
2. Crea las nuevas tablas para caja chica
3. Verifica que todo esté correcto

Ejecutar con:
python migration_caja_chica.py
"""

from database import engine, get_db
from models import Base, Proveedor, CajaChica, GastoCajaChica, GastoProducto
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
import sys

def verificar_campo_ruc():
    """Verifica si el campo RUC ya existe en la tabla proveedores"""
    inspector = inspect(engine)
    columns = inspector.get_columns('proveedores')
    column_names = [col['name'] for col in columns]
    return 'ruc' in column_names

def agregar_campo_ruc():
    """Agrega el campo RUC a la tabla proveedores si no existe"""
    try:
        with engine.connect() as connection:
            # Verificar si la columna ya existe
            if not verificar_campo_ruc():
                print("📝 Agregando campo RUC a tabla proveedores...")
                connection.execute(text("ALTER TABLE proveedores ADD COLUMN ruc VARCHAR UNIQUE;"))
                connection.commit()
                print("✅ Campo RUC agregado correctamente")
            else:
                print("✅ Campo RUC ya existe en tabla proveedores")
    except Exception as e:
        print(f"❌ Error agregando campo RUC: {e}")
        return False
    return True

def crear_tablas_caja_chica():
    """Crea las nuevas tablas del módulo de caja chica"""
    try:
        print("🏗️ Creando tablas del módulo caja chica...")
        
        # Esto creará solo las tablas nuevas que no existan
        Base.metadata.create_all(bind=engine, checkfirst=True)
        
        print("✅ Tablas de caja chica creadas correctamente")
        return True
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        return False

def verificar_tablas():
    """Verifica que todas las tablas necesarias existen"""
    inspector = inspect(engine)
    tablas_existentes = inspector.get_table_names()
    
    tablas_necesarias = [
        'caja_chica',
        'gastos_caja_chica', 
        'gastos_productos'
    ]
    
    print("🔍 Verificando tablas...")
    for tabla in tablas_necesarias:
        if tabla in tablas_existentes:
            print(f"   ✅ {tabla}")
        else:
            print(f"   ❌ {tabla} - NO EXISTE")
            return False
    
    return True

def crear_caja_chica_inicial():
    """Crear una caja chica inicial de ejemplo (opcional)"""
    try:
        db = next(get_db())
        
        # Verificar si ya existe una caja chica
        existing_caja = db.query(CajaChica).first()
        if existing_caja:
            print("✅ Ya existe una caja chica registrada")
            return True
        
        respuesta = input("¿Deseas crear una caja chica inicial? (s/n): ").lower()
        if respuesta == 's':
            try:
                monto = float(input("Ingresa el monto inicial de caja chica: $"))
                
                nueva_caja = CajaChica(
                    monto_inicial=monto,
                    saldo_actual=monto,
                    activo=True
                )
                
                db.add(nueva_caja)
                db.commit()
                db.refresh(nueva_caja)
                
                print(f"✅ Caja chica inicial creada con ${monto:,.2f}")
                return True
                
            except ValueError:
                print("❌ Monto inválido, saltando creación de caja chica inicial")
                return True
        else:
            print("⏭️ Saltando creación de caja chica inicial")
            return True
            
    except Exception as e:
        print(f"❌ Error creando caja chica inicial: {e}")
        return False
    finally:
        db.close()

def main():
    print("=== MIGRACIÓN MÓDULO CAJA CHICA ===\n")
    
    # 1. Agregar campo RUC a proveedores
    if not agregar_campo_ruc():
        print("❌ Error en migración, deteniendo...")
        sys.exit(1)
    
    # 2. Crear nuevas tablas
    if not crear_tablas_caja_chica():
        print("❌ Error creando tablas, deteniendo...")
        sys.exit(1)
    
    # 3. Verificar que todo esté bien
    if not verificar_tablas():
        print("❌ Error en verificación de tablas")
        sys.exit(1)
    
    # 4. Opcionalmente crear caja chica inicial
    crear_caja_chica_inicial()
    
    print("\n=== MIGRACIÓN COMPLETADA ===")
    print("✅ El módulo de caja chica está listo para usar")
    print("\n📚 Consulta la documentación en: DOCUMENTACION_CAJA_CHICA.md")
    print("🧪 Prueba el módulo con: python test_caja_chica.py")
    print("🚀 Inicia el servidor con: uvicorn main:app --reload")

if __name__ == "__main__":
    main()