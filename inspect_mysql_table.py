"""
Script para inspeccionar la estructura de la tabla measurements existente
"""
import pymysql
from sqlalchemy import create_engine, text

# Configuración MySQL
MYSQL_HOST = 'db.parks.com.py'
MYSQL_PORT = '3306'
MYSQL_DB = 'parks_data'
MYSQL_USER = 'root'
MYSQL_PASS = 'ps1sw9751'

try:
    # Conexión directa con pymysql para inspección
    connection = pymysql.connect(
        host=MYSQL_HOST,
        port=int(MYSQL_PORT),
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB,
        charset='utf8mb4'
    )
    
    print("✅ Conexión MySQL exitosa!")
    
    with connection.cursor() as cursor:
        # Ver estructura de la tabla measurements
        print("\n📋 ESTRUCTURA DE LA TABLA 'measurements':")
        cursor.execute("DESCRIBE measurements")
        columns = cursor.fetchall()
        
        for column in columns:
            print(f"  - {column[0]} | {column[1]} | {'NULL' if column[2] == 'YES' else 'NOT NULL'} | {column[3] or ''}")
        
        print("\n📊 DATOS DE MUESTRA:")
        cursor.execute("SELECT * FROM measurements LIMIT 5")
        rows = cursor.fetchall()
        
        if rows:
            # Mostrar nombres de columnas
            cursor.execute("SHOW COLUMNS FROM measurements")
            column_info = cursor.fetchall()
            column_names = [col[0] for col in column_info]
            print(f"Columnas: {column_names}")
            
            for i, row in enumerate(rows, 1):
                print(f"  Fila {i}: {row}")
        else:
            print("  No hay datos en la tabla")
        
        print("\n🔢 CONTEO DE REGISTROS:")
        cursor.execute("SELECT COUNT(*) FROM measurements")
        count = cursor.fetchone()[0]
        print(f"  Total registros: {count}")
        
        print("\n🚢 VESSELS ÚNICOS:")
        cursor.execute("SELECT DISTINCT vessel_name FROM measurements LIMIT 10")
        vessels = cursor.fetchall()
        for vessel in vessels:
            print(f"  - {vessel[0]}")
            
        print("\n📅 RANGO DE FECHAS:")
        cursor.execute("SELECT MIN(timestamp) as min_date, MAX(timestamp) as max_date FROM measurements")
        date_range = cursor.fetchone()
        print(f"  Desde: {date_range[0]}")
        print(f"  Hasta: {date_range[1]}")
    
    connection.close()
    print("\n✅ Inspección completada")
    
except Exception as e:
    print(f"❌ Error: {e}")