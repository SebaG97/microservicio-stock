#!/usr/bin/env python3
"""
Script para probar la API sin cerrar el servidor
"""

import requests
import json

def probar_api():
    """Prueba la API de partes de trabajo"""
    
    base_url = "http://localhost:8002/api"
    
    print("🧪 Probando API de partes de trabajo...")
    
    # 1. Probar listado de partes de trabajo
    print("\n1️⃣ Listando partes de trabajo...")
    try:
        response = requests.get(f"{base_url}/partes-trabajo/?limit=5")
        if response.status_code == 200:
            partes = response.json()
            print(f"✅ Encontrados {len(partes)} partes de trabajo")
            
            for parte in partes:
                print(f"   📋 Parte {parte.get('numero', 'N/A')}: {parte.get('trabajo_solicitado', 'Sin descripción')}")
                print(f"      👥 Técnicos: {len(parte.get('tecnicos', []))}")
                for tecnico in parte.get('tecnicos', []):
                    print(f"         - {tecnico.get('nombre', 'N/A')} ({tecnico.get('user', 'N/A')})")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 2. Probar un parte específico
    print("\n2️⃣ Consultando parte específico (ID=1)...")
    try:
        response = requests.get(f"{base_url}/partes-trabajo/1")
        if response.status_code == 200:
            parte = response.json()
            print(f"✅ Parte encontrado:")
            print(f"   📋 Número: {parte.get('numero')}")
            print(f"   👤 Cliente: {parte.get('cliente_empresa')}")
            print(f"   📝 Trabajo: {parte.get('trabajo_solicitado')}")
            print(f"   👥 Técnicos asignados: {len(parte.get('tecnicos', []))}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 3. Probar filtros
    print("\n3️⃣ Probando filtro por número...")
    try:
        response = requests.get(f"{base_url}/partes-trabajo/?numero=113")
        if response.status_code == 200:
            partes = response.json()
            print(f"✅ Filtro por número 113: {len(partes)} resultados")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 4. Listar técnicos disponibles
    print("\n4️⃣ Listando técnicos disponibles...")
    try:
        # Esto requeriría un endpoint de tecnicos, por ahora solo mostramos los del parte
        print("   ℹ️ Ver técnicos en los partes de trabajo arriba")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎉 Pruebas completadas!")

if __name__ == "__main__":
    probar_api()
