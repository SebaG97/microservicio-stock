#!/usr/bin/env python3
"""
Script para probar el nuevo endpoint de transferencias
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def obtener_depositos():
    """Obtener lista de depósitos disponibles"""
    response = requests.get(f"{BASE_URL}/depositos")
    if response.status_code == 200:
        return response.json()
    return []

def obtener_productos():
    """Obtener lista de productos disponibles"""
    response = requests.get(f"{BASE_URL}/productos")
    if response.status_code == 200:
        return response.json()
    return []

def obtener_stock():
    """Obtener stock actual"""
    response = requests.get(f"{BASE_URL}/stock")
    if response.status_code == 200:
        return response.json()
    return []

def probar_transferencia(producto_id, dep_origen_id, dep_destino_id, cantidad):
    """Probar una transferencia de stock"""
    url = f"{BASE_URL}/stock/movimientos/transferencia/"
    params = {
        "producto_id": producto_id,
        "deposito_origen_id": dep_origen_id,
        "deposito_destino_id": dep_destino_id,
        "cantidad": cantidad
    }
    
    print(f"🔄 Probando transferencia:")
    print(f"  - Producto ID: {producto_id}")
    print(f"  - De depósito {dep_origen_id} a depósito {dep_destino_id}")
    print(f"  - Cantidad: {cantidad}")
    
    response = requests.post(url, params=params)
    
    print(f"📊 Respuesta del servidor:")
    print(f"  - Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"  - ✅ Transferencia exitosa!")
        print(f"  - Stock origen actual: {result.get('stock_origen_actual')}")
        print(f"  - Stock destino actual: {result.get('stock_destino_actual')}")
    else:
        try:
            error = response.json()
            print(f"  - ❌ Error: {error.get('detail', 'Error desconocido')}")
        except:
            print(f"  - ❌ Error: {response.text}")
    
    return response

def main():
    print("🚀 Probando el nuevo endpoint de transferencias\n")
    
    # Obtener información disponible
    print("📋 Obteniendo información disponible...")
    depositos = obtener_depositos()
    productos = obtener_productos()
    stock = obtener_stock()
    
    print(f"\n📦 Depósitos disponibles:")
    for dep in depositos[:5]:  # Solo mostrar los primeros 5
        print(f"  - ID {dep['id']}: {dep['nombre']}")
    
    print(f"\n📦 Productos disponibles:")
    for prod in productos[:5]:  # Solo mostrar los primeros 5
        print(f"  - ID {prod['id']}: {prod['descripcion'][:50]}...")
    
    print(f"\n📊 Stock actual:")
    for s in stock[:10]:  # Solo mostrar los primeros 10
        print(f"  - Producto {s['producto_id']}, Depósito {s['deposito_id']}: {s['existencia']} unidades")
    
    if not stock:
        print("❌ No hay stock disponible para hacer pruebas")
        return
    
    # Buscar un stock con cantidad > 1 para hacer prueba
    stock_disponible = [s for s in stock if s['existencia'] > 1]
    
    if not stock_disponible:
        print("❌ No hay stock suficiente (>1) para hacer pruebas de transferencia")
        return
    
    # Tomar el primer stock disponible
    test_stock = stock_disponible[0]
    producto_id = test_stock['producto_id']
    deposito_origen = test_stock['deposito_id']
    
    # Buscar un depósito destino diferente
    deposito_destino = None
    for dep in depositos:
        if dep['id'] != deposito_origen:
            deposito_destino = dep['id']
            break
    
    if not deposito_destino:
        print("❌ No se encontró un depósito destino diferente al origen")
        return
    
    print(f"\n" + "="*60)
    print("🧪 PRUEBA 1: Transferencia válida")
    print("="*60)
    
    # Probar transferencia válida (1 unidad)
    probar_transferencia(producto_id, deposito_origen, deposito_destino, 1)
    
    print(f"\n" + "="*60)
    print("🧪 PRUEBA 2: Transferencia con stock insuficiente")
    print("="*60)
    
    # Probar transferencia con stock insuficiente
    cantidad_excesiva = test_stock['existencia'] + 100
    probar_transferencia(producto_id, deposito_origen, deposito_destino, cantidad_excesiva)
    
    print(f"\n" + "="*60)
    print("🧪 PRUEBA 3: Transferencia con depósitos iguales")
    print("="*60)
    
    # Probar transferencia con mismo depósito origen y destino
    probar_transferencia(producto_id, deposito_origen, deposito_origen, 1)
    
    print(f"\n✅ Pruebas completadas!")

if __name__ == "__main__":
    main()