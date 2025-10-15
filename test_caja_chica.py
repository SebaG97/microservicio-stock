"""
Script de prueba para el módulo de Caja Chica

Este script demuestra cómo usar todas las funcionalidades del nuevo módulo:
1. Crear/actualizar caja chica
2. Registrar gastos con productos
3. Ver listados y saldos
4. Crear proveedores con RUC

Ejecutar con:
python test_caja_chica.py
"""

import requests
import json
from datetime import date, datetime

BASE_URL = "http://localhost:8000/api"

def test_caja_chica():
    print("=== PRUEBA DEL MÓDULO CAJA CHICA ===\n")
    
    # 1. Crear una caja chica inicial
    print("1. Creando caja chica inicial...")
    caja_data = {
        "monto_inicial": 50000.0
    }
    
    response = requests.post(f"{BASE_URL}/caja-chica/", json=caja_data)
    if response.status_code == 200:
        caja_chica = response.json()
        print(f"✅ Caja chica creada - ID: {caja_chica['id']}, Saldo: ${caja_chica['saldo_actual']:,.2f}")
    else:
        print(f"❌ Error creando caja chica: {response.text}")
        return
    
    # 2. Crear un proveedor con RUC
    print("\n2. Creando proveedor con RUC...")
    proveedor_data = {
        "nombre": "Ferretería San José",
        "ruc": "80123456-7"
    }
    
    response = requests.post(f"{BASE_URL}/proveedores/", json=proveedor_data)
    if response.status_code == 200:
        proveedor = response.json()
        print(f"✅ Proveedor creado - ID: {proveedor['id']}, RUC: {proveedor['ruc']}")
    else:
        print(f"❌ Error creando proveedor: {response.text}")
        return
    
    # 3. Obtener lista de productos y depósitos para el gasto
    print("\n3. Obteniendo productos disponibles...")
    
    response_productos = requests.get(f"{BASE_URL}/productos/")
    response_depositos = requests.get(f"{BASE_URL}/depositos/")
    
    if response_productos.status_code == 200 and response_depositos.status_code == 200:
        productos = response_productos.json()
        depositos = response_depositos.json()
        
        if len(productos) > 0 and len(depositos) > 0:
            print(f"✅ Encontrados {len(productos)} productos y {len(depositos)} depósitos")
            producto_id = productos[0]['id']
            deposito_id = depositos[0]['id']
            print(f"   Usando producto ID: {producto_id}, depósito ID: {deposito_id}")
        else:
            print("⚠️  No hay productos o depósitos disponibles. Creando gasto sin productos...")
            producto_id = None
            deposito_id = None
    else:
        print("⚠️  Error obteniendo productos/depósitos. Creando gasto sin productos...")
        producto_id = None
        deposito_id = None
    
    # 4. Crear un gasto con productos (si hay disponibles)
    print("\n4. Registrando gasto de caja chica...")
    
    gasto_data = {
        "proveedor_id": proveedor['id'],
        "numero_factura": "001-001-0000001",
        "fecha_factura": date.today().isoformat(),
        "descripcion": "Compra de materiales de ferretería",
        "productos": []
    }
    
    if producto_id and deposito_id:
        gasto_data["productos"] = [
            {
                "producto_id": producto_id,
                "deposito_id": deposito_id,
                "cantidad": 5.0,
                "precio_unitario": 150.0
            }
        ]
    
    response = requests.post(f"{BASE_URL}/gastos/", json=gasto_data)
    if response.status_code == 200:
        gasto = response.json()
        print(f"✅ Gasto registrado - ID: {gasto['id']}, Monto: ${gasto['monto_total']:,.2f}")
        if gasto['productos']:
            print(f"   📦 Incluye {len(gasto['productos'])} productos en stock")
    else:
        print(f"❌ Error registrando gasto: {response.text}")
        return
    
    # 5. Crear un segundo gasto solo con descripción (sin productos)
    print("\n5. Registrando gasto sin productos...")
    
    gasto_simple_data = {
        "proveedor_nombre": "Combustibles El Rápido",
        "numero_factura": "002-001-0000001", 
        "fecha_factura": date.today().isoformat(),
        "descripcion": "Combustible para vehículos",
        "productos": []  # Sin productos
    }
    
    # Para gastos sin productos, necesitamos crear un gasto manualmente
    # Este endpoint necesitará ser ajustado para manejar gastos sin productos
    
    # 6. Obtener resumen de caja chica
    print("\n6. Obteniendo resumen de caja chica...")
    
    response = requests.get(f"{BASE_URL}/caja-chica/resumen")
    if response.status_code == 200:
        resumen = response.json()
        caja = resumen['caja_chica']
        print(f"✅ RESUMEN DE CAJA CHICA:")
        print(f"   💰 Monto inicial: ${caja['monto_inicial']:,.2f}")
        print(f"   💳 Saldo actual: ${caja['saldo_actual']:,.2f}")
        print(f"   📊 Total gastado: ${resumen['gastos_totales']:,.2f}")
        print(f"   📅 Gastos del mes: ${resumen['gastos_del_mes']:,.2f}")
    else:
        print(f"❌ Error obteniendo resumen: {response.text}")
    
    # 7. Listar todos los gastos
    print("\n7. Listando gastos registrados...")
    
    response = requests.get(f"{BASE_URL}/gastos/")
    if response.status_code == 200:
        gastos = response.json()
        print(f"✅ Encontrados {len(gastos)} gastos:")
        for i, gasto in enumerate(gastos, 1):
            proveedor_nombre = gasto.get('proveedor', {}).get('nombre') if gasto.get('proveedor') else gasto.get('proveedor_nombre', 'Sin proveedor')
            print(f"   {i}. Factura: {gasto['numero_factura']} - {proveedor_nombre} - ${gasto['monto_total']:,.2f}")
    else:
        print(f"❌ Error listando gastos: {response.text}")
    
    print("\n=== PRUEBA COMPLETADA ===")
    print("\n📋 ENDPOINTS DISPONIBLES:")
    print("   POST   /api/caja-chica/                    - Crear/actualizar caja chica")
    print("   GET    /api/caja-chica/actual             - Obtener caja chica activa")
    print("   PUT    /api/caja-chica/{id}              - Actualizar monto de caja chica")
    print("   GET    /api/caja-chica/resumen            - Obtener resumen completo")
    print("   POST   /api/gastos/                       - Registrar nuevo gasto")
    print("   GET    /api/gastos/                       - Listar gastos (filtros: mes, año)")
    print("   GET    /api/gastos/{id}                   - Obtener gasto específico")
    print("   PUT    /api/gastos/{id}                   - Actualizar gasto")
    print("   DELETE /api/gastos/{id}                   - Eliminar gasto (revierte stock)")
    print("   POST   /api/proveedores/                  - Crear proveedor rápido")
    print("   GET    /api/gastos/productos/{gasto_id}   - Obtener productos de un gasto")

if __name__ == "__main__":
    try:
        test_caja_chica()
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor. Asegúrate de que esté ejecutándose en localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")