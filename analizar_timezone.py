"""
Script para analizar los timestamps y zona horaria de la base de datos
"""
import pymysql
from datetime import datetime, timezone, timedelta
import pytz

# Configuración MySQL
MYSQL_HOST = 'db.parks.com.py'
MYSQL_PORT = '3306'
MYSQL_DB = 'parks_data'
MYSQL_USER = 'root'
MYSQL_PASS = 'ps1sw9751'

try:
    connection = pymysql.connect(
        host=MYSQL_HOST,
        port=int(MYSQL_PORT),
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB,
        charset='utf8mb4'
    )
    
    print("🔍 ANÁLISIS DE TIMESTAMPS Y ZONA HORARIA")
    print("=" * 50)
    
    # Hora actual en diferentes zonas
    utc_now = datetime.now(timezone.utc)
    local_now = datetime.now()  # Hora local del sistema
    paraguay_tz = pytz.timezone('America/Asuncion')  # UTC-3
    paraguay_now = utc_now.astimezone(paraguay_tz)
    
    print(f"🕐 Hora actual UTC:      {utc_now.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"🕐 Hora local sistema:   {local_now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🕐 Hora Paraguay (UTC-3): {paraguay_now.strftime('%Y-%m-%d %H:%M:%S')} {paraguay_now.tzinfo}")
    
    with connection.cursor() as cursor:
        print(f"\n📊 ÚLTIMOS TIMESTAMPS DE LA BASE DE DATOS:")
        cursor.execute("""
            SELECT vessel_name, MAX(timestamp) as ultimo_timestamp
            FROM measurements 
            GROUP BY vessel_name 
            ORDER BY ultimo_timestamp DESC 
            LIMIT 10
        """)
        
        resultados = cursor.fetchall()
        
        print(f"{'Vessel':<15} | {'Timestamp BD (UTC)':<20} | {'Hace (horas)':<12} | {'Paraguay time'}")
        print("-" * 80)
        
        for vessel, timestamp_bd in resultados:
            # El timestamp de la BD está en UTC
            timestamp_utc = timestamp_bd.replace(tzinfo=timezone.utc)
            timestamp_paraguay = timestamp_utc.astimezone(paraguay_tz)
            
            # Calcular diferencia usando UTC
            diferencia = utc_now - timestamp_utc
            horas_diferencia = diferencia.total_seconds() / 3600
            
            print(f"{vessel:<15} | {timestamp_bd} | {horas_diferencia:8.1f}h | {timestamp_paraguay.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # También verificar algunos timestamps recientes
        print(f"\n📅 MUESTRAS DE TIMESTAMPS RECIENTES:")
        cursor.execute("""
            SELECT vessel_name, timestamp, received_at 
            FROM measurements 
            WHERE timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        
        recientes = cursor.fetchall()
        if recientes:
            print(f"{'Vessel':<15} | {'Timestamp':<20} | {'Received_at':<20}")
            print("-" * 60)
            for vessel, ts, received in recientes:
                received_str = received.strftime('%Y-%m-%d %H:%M:%S') if received else "NULL"
                print(f"{vessel:<15} | {ts} | {received_str}")
        else:
            print("No hay datos en las últimas 24 horas")
    
    connection.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()