#!/usr/bin/env python3
"""
Script para probar los endpoints de movimientos múltiples
"""
import requests
import json

import requests
import json

# URL base del API
BASE_URL = "http://localhost:8001"

def probar_movimiento_multiple():
    """Probar movimiento múltiple (egreso de varios productos)"""
    url = f"{BASE_URL}/api/stock/movimientos/multiple/"
    
    data = {
        "deposito_id": 2,
        "tipo": "egreso",
        "items": [
            {
                "producto_id": 1,
                "cantidad": 2,
                "precio_unitario": 150.0,
                "observaciones": "Venta cliente A"
            },
            {
                "producto_id": 2,
                "cantidad": 1,
                "precio_unitario": 80.0,
                "observaciones": "Venta cliente A"
            }
        ],
        "motivo": "venta_cliente",
        "cliente_id": "12345",
        "cliente_empresa": "ACME Corp"
    }
    
    print("🔄 Probando movimiento múltiple (egreso):")
    print(f"   Datos: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"\n📊 Respuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ {result['mensaje']}")
            print(f"   📦 Depósito: {result['deposito_id']}")
            print(f"   📊 Items procesados: {result['items_procesados']}")
            print(f"   ✅ Exitosos: {result['items_exitosos']}")
            print(f"   ❌ Fallidos: {result['items_fallidos']}")
            if result['total_valor']:
                print(f"   💰 Valor total: ${result['total_valor']}")
            
            print(f"\n   📋 Detalle por item:")
            for item in result['resultados']:
                status = "✅" if item['exitoso'] else "❌"
                print(f"     {status} {item['descripcion'][:30]}...")
                print(f"         Cantidad: {item['cantidad']}")
                print(f"         Stock: {item['stock_anterior']} → {item['stock_actual']}")
                if not item['exitoso']:
                    print(f"         Error: {item['error']}")
        else:
            error = response.json()
            print(f"   ❌ Error: {error.get('detail', 'Error desconocido')}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Error: No se pudo conectar al servidor")
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")

def probar_transferencia_multiple():
    """Probar transferencia múltiple entre depósitos"""
    url = f"{BASE_URL}/api/stock/movimientos/transferencia-multiple/"
    
    data = {
        "deposito_origen_id": 2,
        "deposito_destino_id": 5,
        "items": [
            {"producto_id": 1, "cantidad": 1},
            {"producto_id": 2, "cantidad": 2}
        ],
        "motivo": "reubicacion_productos"
    }
    
    print("\n🔄 Probando transferencia múltiple:")
    print(f"   Datos: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"\n📊 Respuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ {result['mensaje']}")
            print(f"   📦 De depósito {result['deposito_origen_id']} a depósito {result['deposito_destino_id']}")
            print(f"   📊 Items procesados: {result['items_procesados']}")
            print(f"   ✅ Exitosos: {result['items_exitosos']}")
            print(f"   ❌ Fallidos: {result['items_fallidos']}")
            
            print(f"\n   📋 Detalle por item:")
            for item in result['resultados']:
                status = "✅" if item['exitoso'] else "❌"
                print(f"     {status} {item['descripcion'][:30]}...")
                print(f"         Cantidad: {item['cantidad']}")
                print(f"         Origen: {item['stock_origen_anterior']} → {item['stock_origen_actual']}")
                print(f"         Destino: {item['stock_destino_anterior']} → {item['stock_destino_actual']}")
                if not item['exitoso']:
                    print(f"         Error: {item['error']}")
        else:
            error = response.json()
            print(f"   ❌ Error: {error.get('detail', 'Error desconocido')}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Error: No se pudo conectar al servidor")
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")

def probar_movimiento_ingreso():
    """Probar movimiento múltiple de ingreso"""
    url = f"{BASE_URL}/api/stock/movimientos/multiple/"
    
    data = {
        "deposito_id": 2,
        "tipo": "ingreso",
        "items": [
            {
                "producto_id": 1,
                "cantidad": 10,
                "precio_unitario": 120.0,
                "observaciones": "Compra a proveedor X"
            },
            {
                "producto_id": 2,
                "cantidad": 5,
                "precio_unitario": 75.0,
                "observaciones": "Compra a proveedor X"
            }
        ],
        "motivo": "compra_proveedor",
        "cliente_empresa": "Proveedor XYZ SA"
    }
    
    print("\n🔄 Probando movimiento múltiple (ingreso):")
    print(f"   Datos: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"\n📊 Respuesta del servidor:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ {result['mensaje']}")
            print(f"   💰 Valor total compra: ${result['total_valor']}")
        else:
            error = response.json()
            print(f"   ❌ Error: {error.get('detail', 'Error desconocido')}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Error: No se pudo conectar al servidor")
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")

if __name__ == "__main__":
    print("🚀 Probando endpoints de movimientos múltiples\n")
    
    print("="*60)
    print("TEST 1: MOVIMIENTO MÚLTIPLE (EGRESO)")
    print("="*60)
    probar_movimiento_multiple()
    
    print("\n" + "="*60)
    print("TEST 2: TRANSFERENCIA MÚLTIPLE")
    print("="*60)
    probar_transferencia_multiple()
    
    print("\n" + "="*60)
    print("TEST 3: MOVIMIENTO MÚLTIPLE (INGRESO)")
    print("="*60)
    probar_movimiento_ingreso()
    
    print("\n✅ Todas las pruebas completadas!")