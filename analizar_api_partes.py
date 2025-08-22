#!/usr/bin/env python3
"""
Script para analizar los datos que devuelve la API de partes de trabajo
y identificar dónde están los datos de técnicos y horarios
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def analizar_api_partes():
    """Analiza la estructura de datos de la API de partes de trabajo"""
    API_URL = "https://api.partedetrabajo.com/v1/partes/"
    HEADERS = {"X-Auth-Partedetrabajo-Token": os.getenv("API_TOKEN")}
    
    try:
        print("🔍 Analizando API de partes de trabajo...")
        print(f"URL: {API_URL}")
        
        response = requests.get(API_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        partes = data.get("docs", [])
        
        print(f"📊 Total de partes encontrados: {len(partes)}")
        
        if partes:
            print("\n🔬 Analizando estructura del primer parte:")
            primer_parte = partes[0]
            
            print("🗂️ Campos principales:")
            for key, value in primer_parte.items():
                tipo = type(value).__name__
                if isinstance(value, list) and value:
                    ejemplo = f"[{len(value)} elementos, ejemplo: {str(value[0])[:100]}...]"
                elif isinstance(value, dict):
                    ejemplo = f"{{dict con {len(value)} campos}}"
                else:
                    ejemplo = str(value)[:100]
                print(f"   {key}: {tipo} = {ejemplo}")
            
            print("\n👤 Buscando información de técnicos...")
            campos_tecnico = []
            for key, value in primer_parte.items():
                if any(palabra in key.lower() for palabra in ['tecnico', 'asignado', 'responsable', 'usuario', 'worker', 'employee']):
                    campos_tecnico.append((key, value))
            
            if campos_tecnico:
                print("   Campos relacionados con técnicos encontrados:")
                for key, value in campos_tecnico:
                    print(f"      {key}: {value}")
            else:
                print("   ⚠️ No se encontraron campos obvios de técnicos")
            
            print("\n⏰ Buscando información de fechas/horarios...")
            campos_fecha = []
            for key, value in primer_parte.items():
                if any(palabra in key.lower() for palabra in ['fecha', 'hora', 'time', 'inicio', 'fin', 'start', 'end', 'created', 'updated']):
                    campos_fecha.append((key, value))
            
            if campos_fecha:
                print("   Campos relacionados con fechas encontrados:")
                for key, value in campos_fecha:
                    print(f"      {key}: {value}")
            
            print(f"\n📋 Ejemplo completo del primer parte:")
            print(json.dumps(primer_parte, indent=2, ensure_ascii=False, default=str))
            
            # Analizar varios partes para patrones
            print(f"\n🔄 Analizando patrones en los primeros 5 partes...")
            for i, parte in enumerate(partes[:5]):
                print(f"\n--- Parte {i+1}: {parte.get('id', 'sin_id')} ---")
                
                # Buscar técnico
                tecnico_encontrado = None
                for key in ['tecnico', 'asignado_a', 'responsable', 'usuario', 'created_by']:
                    if key in parte and parte[key]:
                        tecnico_encontrado = (key, parte[key])
                        break
                
                if tecnico_encontrado:
                    print(f"   Técnico en '{tecnico_encontrado[0]}': {tecnico_encontrado[1]}")
                else:
                    print("   ⚠️ No se encontró técnico")
                
                # Buscar fechas
                fecha_inicio = parte.get('fecha_inicio') or parte.get('created_at') or parte.get('start_time')
                fecha_fin = parte.get('fecha_fin') or parte.get('completed_at') or parte.get('end_time')
                
                print(f"   Fecha inicio: {fecha_inicio}")
                print(f"   Fecha fin: {fecha_fin}")
                
                # Estado
                estado = parte.get('estado') or parte.get('status')
                print(f"   Estado: {estado}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None
    except Exception as e:
        print(f"❌ Error general: {e}")
        return None

if __name__ == "__main__":
    resultado = analizar_api_partes()
    
    if resultado:
        print("\n✅ Análisis completado. Revisa la salida para identificar:")
        print("   1. ¿Dónde está la información del técnico?")
        print("   2. ¿Qué formato tienen las fechas de inicio y fin?")
        print("   3. ¿Hay algún campo de estado o progreso?")
        print("   4. ¿Hay información adicional en metadatos?")
    else:
        print("❌ No se pudo analizar la API")
