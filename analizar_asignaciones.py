from database import SessionLocal
from models import Tecnico, ParteTrabajo, HorasExtras
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de la API
API_URL = "https://api.partedetrabajo.com/v1/partes/"
HEADERS = {"X-Auth-Partedetrabajo-Token": os.getenv("API_TOKEN")}

def analizar_asignaciones():
    """Analiza las asignaciones de técnicos vs lo que dice la API"""
    
    db = SessionLocal()
    
    print("🔍 Analizando asignaciones de técnicos...")
    
    # Obtener algunos partes de la API para verificar
    response = requests.get(API_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    partes_api = response.json().get("docs", [])
    
    # Analizar técnicos en API vs BD
    tecnicos_api = set()
    asignaciones_api = {}
    
    for parte in partes_api:
        if parte.get("estado") == 2:  # Solo finalizados
            parte_id = parte.get("id")
            tecnicos_parte = parte.get("tecnicos", [])
            
            for tecnico in tecnicos_parte:
                user = tecnico.get("user", "")
                tecnicos_api.add(user)
                
                if user not in asignaciones_api:
                    asignaciones_api[user] = []
                asignaciones_api[user].append(parte_id)
    
    print(f"👥 Técnicos únicos en API: {len(tecnicos_api)}")
    for user in sorted(tecnicos_api):
        count = len(asignaciones_api.get(user, []))
        print(f"  - {user}: {count} partes")
    
    # Verificar técnicos en BD
    print(f"\n👥 Técnicos en BD:")
    tecnicos_bd = db.query(Tecnico).all()
    for tecnico in tecnicos_bd:
        partes_count = db.query(ParteTrabajo).filter(ParteTrabajo.tecnico_id == tecnico.id).count()
        horas_count = db.query(HorasExtras).filter(HorasExtras.tecnico_id == tecnico.id).count()
        print(f"  - {tecnico.nombre} {tecnico.apellido} (Legajo: {tecnico.legajo}): {partes_count} partes, {horas_count} horas")
    
    # Verificar algunos partes específicos para ver mal asignación
    print(f"\n🔍 Verificando asignaciones específicas:")
    
    # Tomar los primeros 5 partes finalizados de la API
    partes_finalizados = [p for p in partes_api if p.get("estado") == 2][:5]
    
    for parte in partes_finalizados:
        parte_id = parte.get("id")
        tecnicos_api_parte = [t.get("user", "") for t in parte.get("tecnicos", [])]
        
        # Buscar en BD
        parte_bd = db.query(ParteTrabajo).filter(ParteTrabajo.id_parte_api == parte_id).first()
        
        if parte_bd:
            tecnico_bd = db.query(Tecnico).filter(Tecnico.id == parte_bd.tecnico_id).first()
            tecnico_bd_legajo = tecnico_bd.legajo if tecnico_bd else "No encontrado"
            
            print(f"  Parte {parte_id}:")
            print(f"    API: {tecnicos_api_parte}")
            print(f"    BD:  {tecnico_bd_legajo} ({tecnico_bd.nombre if tecnico_bd else 'N/A'})")
            
            # Verificar si coincide
            match = any(legajo in tecnico_bd_legajo for legajo in tecnicos_api_parte)
            print(f"    ✅ Coincide: {match}")
    
    db.close()

if __name__ == "__main__":
    analizar_asignaciones()
