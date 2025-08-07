#!/usr/bin/env python3
import os
import sys

# Forzar variables de entorno
os.environ['DB_HOST'] = '192.168.100.218'
os.environ['DB_PORT'] = '6543'
os.environ['DB_DATABASE'] = 'postgres'
os.environ['DB_USERNAME'] = 'postgres'
os.environ['DB_PASSWORD'] = '12345'

print("=== VARIABLES DE ENTORNO FORZADAS ===")
print(f"DB_HOST: {os.environ.get('DB_HOST')}")
print(f"DB_PORT: {os.environ.get('DB_PORT')}")
print(f"DB_DATABASE: {os.environ.get('DB_DATABASE')}")

# Ahora importar y probar la conexión
try:
    from database import engine, SessionLocal
    print("✅ Engine creado correctamente")
    
    # Probar conexión
    db = SessionLocal()
    result = db.execute("SELECT 1 as test").fetchone()
    print(f"✅ Conexión exitosa: {result}")
    db.close()
    
    # Importar main
    from main import app
    print("✅ App cargada correctamente")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
