import requests
import os
from dotenv import load_dotenv
import json

# Cargar variables de entorno
load_dotenv()

# Configuración de la API
API_URL = "https://api.partedetrabajo.com/v1/partes/"
HEADERS = {"X-Auth-Partedetrabajo-Token": os.getenv("API_TOKEN")}

def analizar_paginacion():
    """Analiza la paginación de la API para obtener todos los partes"""
    print("🔍 Analizando paginación de la API...")
    
    try:
        # Primera llamada para ver la estructura
        response = requests.get(API_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print("📋 Estructura de respuesta:")
        print(f"  - Claves principales: {list(data.keys())}")
        
        # Información de paginación
        total_docs = data.get("totalDocs", "No disponible")
        limit = data.get("limit", "No disponible")
        page = data.get("page", "No disponible")
        total_pages = data.get("totalPages", "No disponible")
        has_next = data.get("hasNextPage", "No disponible")
        has_prev = data.get("hasPrevPage", "No disponible")
        
        print(f"\n📊 Información de paginación:")
        print(f"  - Total documentos: {total_docs}")
        print(f"  - Límite por página: {limit}")
        print(f"  - Página actual: {page}")
        print(f"  - Total páginas: {total_pages}")
        print(f"  - Tiene siguiente: {has_next}")
        print(f"  - Tiene anterior: {has_prev}")
        
        docs = data.get("docs", [])
        print(f"  - Documentos en esta página: {len(docs)}")
        
        # Analizar estados
        estados = {}
        for doc in docs:
            estado = doc.get("estado", "No definido")
            estados[estado] = estados.get(estado, 0) + 1
        
        print(f"\n📈 Estados en página actual:")
        for estado, count in estados.items():
            print(f"  - Estado {estado}: {count} partes")
        
        # Si hay más páginas, probar con parámetros
        if has_next:
            print(f"\n🔄 Probando página 2...")
            response2 = requests.get(f"{API_URL}?page=2", headers=HEADERS, timeout=30)
            if response2.status_code == 200:
                data2 = response2.json()
                docs2 = data2.get("docs", [])
                print(f"  - Documentos en página 2: {len(docs2)}")
        
        # Probar con límite más alto
        print(f"\n🔄 Probando con límite más alto...")
        response_limit = requests.get(f"{API_URL}?limit=100", headers=HEADERS, timeout=30)
        if response_limit.status_code == 200:
            data_limit = response_limit.json()
            docs_limit = data_limit.get("docs", [])
            print(f"  - Documentos con limit=100: {len(docs_limit)}")
            
            # Contar estados con límite alto
            estados_limit = {}
            for doc in docs_limit:
                estado = doc.get("estado", "No definido")
                estados_limit[estado] = estados_limit.get(estado, 0) + 1
            
            print(f"\n📈 Estados con limit=100:")
            for estado, count in estados_limit.items():
                print(f"  - Estado {estado}: {count} partes")
                
            # Mostrar algunos partes finalizados
            finalizados = [d for d in docs_limit if d.get("estado") == 2]
            print(f"\n✅ Algunos partes finalizados (estado=2):")
            for i, parte in enumerate(finalizados[:5]):
                print(f"  {i+1}. ID: {parte.get('id')} - Técnicos: {len(parte.get('tecnicos', []))}")
        
        return data
        
    except Exception as e:
        print(f"❌ Error analizando API: {e}")
        return None

if __name__ == "__main__":
    analizar_paginacion()
