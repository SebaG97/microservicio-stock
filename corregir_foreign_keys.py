"""
Script para corregir foreign keys incorrectas en horas_extras
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
from sqlalchemy import text

def corregir_foreign_keys():
    """Corrige las foreign keys de horas_extras para apuntar a las tablas correctas"""
    print("🔧 Corrigiendo foreign keys de horas_extras...")
    
    try:
        with engine.connect() as conn:
            # 1. Eliminar constraints existentes
            print("🗑️ Eliminando foreign keys incorrectas...")
            
            # Obtener nombres de constraints existentes
            result = conn.execute(text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'horas_extras' 
                AND constraint_type = 'FOREIGN KEY'
            """))
            
            constraints = [row[0] for row in result]
            print(f"📋 Constraints encontradas: {constraints}")
            
            # Eliminar cada constraint
            for constraint in constraints:
                conn.execute(text(f"ALTER TABLE horas_extras DROP CONSTRAINT IF EXISTS {constraint}"))
                print(f"   ✅ Eliminada: {constraint}")
            
            # 2. Crear foreign keys correctas
            print("\n🔗 Creando foreign keys correctas...")
            
            # Foreign key hacia partes_trabajo
            conn.execute(text("""
                ALTER TABLE horas_extras 
                ADD CONSTRAINT horas_extras_parte_trabajo_id_fkey 
                FOREIGN KEY (parte_trabajo_id) REFERENCES partes_trabajo(id) 
                ON DELETE CASCADE
            """))
            print("   ✅ FK parte_trabajo_id -> partes_trabajo.id")
            
            # Foreign key hacia tecnicos
            conn.execute(text("""
                ALTER TABLE horas_extras 
                ADD CONSTRAINT horas_extras_tecnico_id_fkey 
                FOREIGN KEY (tecnico_id) REFERENCES tecnicos(id) 
                ON DELETE CASCADE
            """))
            print("   ✅ FK tecnico_id -> tecnicos.id")
            
            conn.commit()
            print("✅ Foreign keys corregidas exitosamente")
            
    except Exception as e:
        print(f"❌ Error corrigiendo foreign keys: {e}")

def eliminar_tablas_backup():
    """Elimina las tablas backup que ya no se necesitan"""
    print("\n🗑️ Eliminando tablas backup obsoletas...")
    
    tablas_backup = [
        'partes_trabajo_backup',
        'tecnicos_backup', 
        'parte_trabajo_tecnicos_backup'
    ]
    
    try:
        with engine.connect() as conn:
            for tabla in tablas_backup:
                # Verificar si existe
                result = conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{tabla}'
                    )
                """))
                
                if result.fetchone()[0]:
                    conn.execute(text(f"DROP TABLE {tabla} CASCADE"))
                    print(f"   🗑️ Eliminada: {tabla}")
                else:
                    print(f"   ℹ️ No existe: {tabla}")
            
            conn.commit()
            print("✅ Tablas backup eliminadas")
            
    except Exception as e:
        print(f"❌ Error eliminando tablas backup: {e}")

def verificar_estructura_final():
    """Verifica que la estructura esté correcta"""
    print("\n🔍 Verificando estructura final...")
    
    try:
        with engine.connect() as conn:
            # Verificar foreign keys
            result = conn.execute(text("""
                SELECT 
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name = 'horas_extras'
            """))
            
            print("📋 Foreign keys en horas_extras:")
            for row in result:
                print(f"   - {row[2]} -> {row[3]}.{row[4]}")
            
            # Contar registros
            db = SessionLocal()
            try:
                from models import HorasExtras, ParteTrabajo, Tecnico
                
                total_horas = db.query(HorasExtras).count()
                total_partes = db.query(ParteTrabajo).count()
                total_tecnicos = db.query(Tecnico).count()
                
                print(f"\n📊 Estadísticas:")
                print(f"   ⏰ Horas extras: {total_horas}")
                print(f"   📋 Partes trabajo: {total_partes}")
                print(f"   👥 Técnicos: {total_tecnicos}")
                
            finally:
                db.close()
                
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")

def main():
    """Función principal"""
    print("🔧 Corrección de Foreign Keys - Sistema Horas Extras")
    print("=" * 55)
    
    # 1. Corregir foreign keys
    corregir_foreign_keys()
    
    # 2. Eliminar tablas backup
    respuesta = input("\n¿Deseas eliminar las tablas backup obsoletas? (s/N): ")
    if respuesta.lower() in ['s', 'si', 'sí', 'yes', 'y']:
        eliminar_tablas_backup()
    
    # 3. Verificar estructura final
    verificar_estructura_final()
    
    print("\n✅ Corrección de estructura completada")

if __name__ == "__main__":
    main()
