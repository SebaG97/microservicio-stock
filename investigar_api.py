#!/usr/bin/env python3
"""
Script para investigar la estructura de datos de la API
"""

from servicios.sincronizador_automatico import SincronizadorAutomatico
import json

def investigar_estructura_api():
    """Investiga cómo vienen los datos de la API"""
    
    print("🔍 Investigando estructura de datos de la API...")
    
    sincronizador = SincronizadorAutomatico()
    
    try:
        # Obtener una muestra pequeña
        todos_los_partes = sincronizador._obtener_todos_los_partes()
        
        if not todos_los_partes:
            print("❌ No se obtuvieron datos de la API")
            return
        
        print(f"📊 Total partes obtenidos: {len(todos_los_partes)}")
        
        # Analizar el primer parte
        primer_parte = todos_los_partes[0]
        print(f"\n🔍 Estructura del primer parte:")
        print(f"   Tipo: {type(primer_parte)}")
        print(f"   Claves disponibles: {list(primer_parte.keys()) if isinstance(primer_parte, dict) else 'No es dict'}")
        
        # Mostrar datos en formato JSON bonito
        print(f"\n📋 Primer parte completo:")
        print(json.dumps(primer_parte, indent=2, default=str, ensure_ascii=False))
        
        # Buscar diferentes variaciones del ID
        posibles_ids = ['_id', 'id', 'ID', 'parte_id', 'parteId', 'numero']
        print(f"\n🔑 Buscando campos de ID en el primer parte:")
        for campo in posibles_ids:
            valor = primer_parte.get(campo)
            if valor:
                print(f"   ✅ {campo}: {valor}")
            else:
                print(f"   ❌ {campo}: No encontrado")
        
        # Analizar algunos más para ver patrones
        print(f"\n📊 Análisis de los primeros 3 partes:")
        for i, parte in enumerate(todos_los_partes[:3], 1):
            print(f"\n   Parte {i}:")
            for campo in posibles_ids:
                valor = parte.get(campo)
                if valor:
                    print(f"     {campo}: {valor}")
        
    except Exception as e:
        print(f"❌ Error investigando API: {e}")

if __name__ == "__main__":
    investigar_estructura_api()
