import requests
import os
from dotenv import load_dotenv
import json

# Cargar variables de entorno
load_dotenv()

# Configuración de la API
API_URL = "https://api.partedetrabajo.com/v1/partes/"
HEADERS = {"X-Auth-Partedetrabajo-Token": os.getenv("API_TOKEN")}

def obtener_todos_los_partes():
    """Obtiene todos los partes usando el sistema de bookmark"""
    print("🔍 Obteniendo todos los partes usando bookmark...")
    
    todos_los_partes = []
    bookmark = None
    pagina = 1
    
    try:
        while True:
            print(f"📄 Página {pagina}...")
            
            # Construir URL con bookmark si existe
            url = API_URL
            if bookmark:
                url += f"?bookmark={bookmark}"
            
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            docs = data.get("docs", [])
            nuevo_bookmark = data.get("bookmark")
            
            print(f"  - Documentos obtenidos: {len(docs)}")
            print(f"  - Bookmark: {nuevo_bookmark}")
            
            if not docs:
                print("  ✅ No hay más documentos")
                break
            
            todos_los_partes.extend(docs)
            
            # Si no hay nuevo bookmark o es igual al anterior, terminamos
            if not nuevo_bookmark or nuevo_bookmark == bookmark:
                print("  ✅ No hay más páginas (bookmark)")
                break
            
            bookmark = nuevo_bookmark
            pagina += 1
            
            # Límite de seguridad
            if pagina > 20:
                print("  ⚠️ Límite de seguridad alcanzado (20 páginas)")
                break
        
        print(f"\n📊 Resumen total:")
        print(f"  - Total partes obtenidos: {len(todos_los_partes)}")
        
        # Analizar estados
        estados = {}
        for doc in todos_los_partes:
            estado = doc.get("estado", "No definido")
            estados[estado] = estados.get(estado, 0) + 1
        
        print(f"  - Estados:")
        for estado, count in estados.items():
            estado_desc = {0: "Aviso", 1: "En proceso", 2: "Finalizado"}.get(estado, f"Estado {estado}")
            print(f"    * {estado_desc}: {count} partes")
        
        # Partes finalizados
        finalizados = [d for d in todos_los_partes if d.get("estado") == 2]
        print(f"\n✅ Total partes finalizados: {len(finalizados)}")
        
        # Técnicos únicos
        tecnicos_unicos = set()
        for parte in finalizados:
            for tecnico in parte.get("tecnicos", []):
                tecnicos_unicos.add(tecnico.get("user", "Sin user"))
        
        print(f"👤 Técnicos únicos en partes finalizados: {len(tecnicos_unicos)}")
        for tecnico in sorted(tecnicos_unicos):
            print(f"  - {tecnico}")
            
        return todos_los_partes
        
    except Exception as e:
        print(f"❌ Error obteniendo partes: {e}")
        return todos_los_partes

if __name__ == "__main__":
    partes = obtener_todos_los_partes()
