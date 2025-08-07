#!/usr/bin/env python3
import sys
import os

print("=== DIAGNÓSTICO DEL SISTEMA ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path[0]}")

print("\n=== VERIFICANDO IMPORTS ===")
try:
    print("1. Importando database...")
    from database import engine, SessionLocal
    print("   ✅ Database imports OK")
    
    print("2. Importando models...")
    from models import Base, Deposito
    print("   ✅ Models imports OK")
    
    print("3. Importando schemas...")
    import schemas
    print("   ✅ Schemas imports OK")
    
    print("4. Importando main...")
    from main import app
    print("   ✅ Main app imports OK")
    
except Exception as e:
    print(f"   ❌ Error importing: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n=== VERIFICANDO BASE DE DATOS ===")
try:
    print("1. Probando conexión...")
    db = SessionLocal()
    result = db.execute("SELECT 1 as test").fetchone()
    print(f"   ✅ Database connection OK: {result}")
    
    print("2. Verificando tabla depositos...")
    count = db.execute("SELECT COUNT(*) FROM depositos").fetchone()
    print(f"   ✅ Depositos table exists, count: {count[0]}")
    
    db.close()
    print("   ✅ Database test completed")
    
except Exception as e:
    print(f"   ❌ Database error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n=== TEST FINALIZADO ===")
