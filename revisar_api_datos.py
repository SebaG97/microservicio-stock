"""
Revisar qué datos vienen realmente de la API para el campo numero
"""
import requests

def revisar_datos_api():
    """Ver qué campos tiene realmente la API"""
    try:
        # URL de la API
        url = "https://gestordeservicios.es/molab/api/partes-trabajo"
        headers = {"Accept": "application/json"}
        
        print("🔍 REVISANDO DATOS DE LA API...\n")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            partes = data.get("data", [])
            
            if partes:
                print("📋 ESTRUCTURA DE UN PARTE DE TRABAJO:")
                primer_parte = partes[0]
                
                for key, value in primer_parte.items():
                    print(f"  {key}: {value}")
                
                print(f"\n🔍 CAMPOS RELEVANTES:")
                print(f"  ¿Tiene 'numero'? {'numero' in primer_parte}")
                print(f"  ¿Tiene 'ejercicio'? {'ejercicio' in primer_parte}")
                
                if 'numero' in primer_parte:
                    print(f"  Valor de numero: {primer_parte['numero']}")
                if 'ejercicio' in primer_parte:
                    print(f"  Valor de ejercicio: {primer_parte['ejercicio']}")
                    
            else:
                print("❌ No se encontraron partes en la respuesta")
        else:
            print(f"❌ Error en API: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    revisar_datos_api()
