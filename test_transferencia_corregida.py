#!/usr/bin/env python3
"""
Script para probar el endpoint de transferencias corregido
"""
import requests
import json

def probar_transferencia_json():
    """Probar transferencia usando JSON en el body"""
    url = "http://localhost:8001/api/stock/movimientos/transferencia/"
    
    # Datos de la transferencia
    transferencia_data = {
        "producto_id": 2,
        "deposito_origen_id": 2,
        "deposito_destino_id": 5,
        "cantidad": 1,
        "motivo": "transferencia_deposito"
    }
    
    print("🔄 Probando transferencia con JSON body:")
    print(f"   Datos: {json.dumps(transferencia_data, indent=2)}")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=transferencia_data, headers=headers)
        
        print(f"\n📊 Respuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ {result['mensaje']}")
            print(f"   📦 Producto ID: {result['producto_id']}")
            print(f"   📍 De depósito {result['deposito_origen_id']} a depósito {result['deposito_destino_id']}")
            print(f"   📊 Cantidad transferida: {result['cantidad']}")
            print(f"   🏪 Stock origen actual: {result['stock_origen_actual']}")
            print(f"   🏪 Stock destino actual: {result['stock_destino_actual']}")
        else:
            try:
                error = response.json()
                print(f"   ❌ Error: {error.get('detail', 'Error desconocido')}")
            except:
                print(f"   ❌ Error: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("   ❌ Error: No se pudo conectar al servidor. ¿Está ejecutándose en http://localhost:8001?")
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")

def probar_validaciones():
    """Probar las validaciones del endpoint"""
    url = "http://localhost:8001/api/stock/movimientos/transferencia/"
    headers = {"Content-Type": "application/json"}
    
    print("\n" + "="*60)
    print("🧪 PROBANDO VALIDACIONES")
    print("="*60)
    
    # Prueba 1: Cantidad negativa
    print("\n1️⃣ Probando cantidad negativa:")
    data = {"producto_id": 2, "deposito_origen_id": 2, "deposito_destino_id": 5, "cantidad": -1}
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 400:
            error = response.json()
            print(f"   ✅ Validación correcta: {error.get('detail')}")
        else:
            print(f"   ❌ Validación falló: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Servidor no disponible")
    
    # Prueba 2: Depósitos iguales
    print("\n2️⃣ Probando depósitos iguales:")
    data = {"producto_id": 2, "deposito_origen_id": 2, "deposito_destino_id": 2, "cantidad": 1}
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 400:
            error = response.json()
            print(f"   ✅ Validación correcta: {error.get('detail')}")
        else:
            print(f"   ❌ Validación falló: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Servidor no disponible")
    
    # Prueba 3: Producto inexistente
    print("\n3️⃣ Probando producto inexistente:")
    data = {"producto_id": 99999, "deposito_origen_id": 2, "deposito_destino_id": 5, "cantidad": 1}
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 404:
            error = response.json()
            print(f"   ✅ Validación correcta: {error.get('detail')}")
        else:
            print(f"   ❌ Validación falló: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Servidor no disponible")

if __name__ == "__main__":
    print("🚀 Probando el endpoint de transferencias corregido\n")
    probar_transferencia_json()
    probar_validaciones()
    print("\n✅ Pruebas completadas!")