"""
Script para probar los endpoints de alarmas via HTTP
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def test_endpoint(endpoint, description):
    """Prueba un endpoint y muestra el resultado"""
    print(f"\n{'='*60}")
    print(f"🧪 PROBANDO: {description}")
    print(f"📡 URL: {BASE_URL}{endpoint}")
    print('='*60)
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Respuesta exitosa:")
            
            # Mostrar respuesta formateada según el endpoint
            if endpoint == "/alarmas":
                print(f"📊 Total vessels: {data['total_vessels']}")
                print(f"📈 Resumen: {data['resumen']}")
                print(f"🚢 Primeros 5 vessels:")
                for i, alarma in enumerate(data['alarmas'][:5], 1):
                    print(f"  {i}. {alarma['vessel_name']:<15} | {alarma['estado_alarma']:<8} | {alarma['horas_sin_datos']:6.1f}h")
                    
            elif endpoint == "/alarmas/criticos":
                print(f"🚨 Vessels críticos encontrados: {len(data)}")
                for vessel in data[:5]:  # Mostrar solo los primeros 5
                    print(f"  ⚠️  {vessel['vessel_name']:<15} | {vessel['horas_sin_datos']:6.1f}h sin datos")
                    
            elif endpoint == "/alarmas/resumen":
                print(f"📊 Total vessels: {data['total_vessels']}")
                print(f"📈 Por estado: {data['conteo_por_estado']}")
                print(f"📊 Porcentajes: {data['porcentajes']}")
                print(f"✅ Operativos: {data['vessels_operativos']}")
                print(f"⚠️  Con problemas: {data['vessels_con_problemas']}")
                
            else:
                # Para endpoints individuales o otros
                print(json.dumps(data, indent=2, default=str))
                
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión - ¿El servidor está ejecutándose?")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🚀 PROBANDO ENDPOINTS DE ALARMAS")
    print("=" * 60)
    
    # Lista de endpoints a probar
    tests = [
        ("/alarmas", "Obtener todas las alarmas"),
        ("/alarmas/resumen", "Obtener resumen de alarmas"),
        ("/alarmas/criticos", "Obtener vessels críticos (>12h)"),
        ("/alarmas/criticos?horas=24", "Obtener vessels críticos (>24h)"),
        ("/alarmas/vessel/TIO KIKE", "Obtener alarma de vessel específico")
    ]
    
    for endpoint, description in tests:
        test_endpoint(endpoint, description)
    
    print(f"\n{'='*60}")
    print("✅ PRUEBAS COMPLETADAS")
    print("=" * 60)

if __name__ == "__main__":
    main()