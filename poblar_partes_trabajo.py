#!/usr/bin/env python3
"""
Script para poblar la nueva tabla de partes de trabajo con datos de la API externa
"""

import requests
from database import get_db
from models import ParteTrabajo, Tecnico
from sqlalchemy.orm import Session
from datetime import datetime
import json

def obtener_partes_api():
    """Obtiene todos los partes de trabajo de la API externa"""
    
    print("📡 Obteniendo partes de trabajo de la API externa...")
    
    # URL base de la API externa (ajusta según sea necesario)
    api_url = "https://tu-api-externa.com/partes-trabajo"  # Cambia por la URL real
    
    # Si tienes autenticación, agrégala aquí
    headers = {
        "accept": "application/json",
        # "Authorization": "Bearer tu-token-aqui"
    }
    
    todos_los_partes = []
    pagina = 1
    
    try:
        while True:
            print(f"📄 Obteniendo página {pagina}...")
            
            # Parámetros para paginación (ajusta según tu API)
            params = {
                "page": pagina,
                "limit": 25,  # Ajusta según tu API
                "estado": "finalizado"  # O el filtro que necesites
            }
            
            response = requests.get(api_url, headers=headers, params=params, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Error en la API: {response.status_code}")
                break
            
            data = response.json()
            
            # Ajusta según la estructura de respuesta de tu API
            if isinstance(data, list):
                partes = data
            elif isinstance(data, dict) and 'data' in data:
                partes = data['data']
            elif isinstance(data, dict) and 'results' in data:
                partes = data['results']
            else:
                partes = [data] if data else []
            
            if not partes:
                print(f"📄 Página {pagina}: No hay más partes")
                break
            
            todos_los_partes.extend(partes)
            print(f"📄 Página {pagina}: {len(partes)} partes obtenidos")
            
            # Si hay menos partes que el límite, es la última página
            if len(partes) < params["limit"]:
                break
            
            pagina += 1
    
    except requests.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return []
    
    print(f"📥 Total partes obtenidos: {len(todos_los_partes)}")
    return todos_los_partes

def obtener_o_crear_tecnico(db: Session, tecnico_data):
    """Obtiene o crea un técnico basado en los datos del JSON"""
    
    email = tecnico_data.get('user')  # El campo 'user' es el email
    nombre_completo = tecnico_data.get('nombre', '')
    
    # Separar nombre y apellido
    partes_nombre = nombre_completo.split(' ', 1)
    nombre = partes_nombre[0] if partes_nombre else 'Sin nombre'
    apellido = partes_nombre[1] if len(partes_nombre) > 1 else ''
    
    # Buscar técnico existente por email
    if email:
        tecnico = db.query(Tecnico).filter(Tecnico.email == email).first()
        if tecnico:
            return tecnico
    
    # Crear legajo único si no existe
    legajo_base = email.split('@')[0] if email else nombre.lower()
    legajo = legajo_base
    contador = 1
    
    while db.query(Tecnico).filter(Tecnico.legajo == legajo).first():
        legajo = f"{legajo_base}_{contador}"
        contador += 1
    
    # Crear nuevo técnico
    nuevo_tecnico = Tecnico(
        nombre=nombre,
        apellido=apellido,
        legajo=legajo,
        email=email,
        tipocuenta=tecnico_data.get('tipocuenta'),
        activo=True
    )
    
    db.add(nuevo_tecnico)
    db.flush()  # Para obtener el ID sin hacer commit
    
    print(f"   👥 Técnico creado: {nombre} {apellido} ({email})")
    return nuevo_tecnico

def convertir_fecha(fecha_str):
    """Convierte fecha de string ISO a datetime"""
    try:
        if not fecha_str:
            return None
        
        # Remover timezone info si existe
        if '+' in fecha_str:
            fecha_str = fecha_str.split('+')[0]
        elif fecha_str.endswith('Z'):
            fecha_str = fecha_str[:-1]
        
        # Formatos posibles
        formatos = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d"
        ]
        
        for formato in formatos:
            try:
                return datetime.strptime(fecha_str, formato)
            except ValueError:
                continue
        
        print(f"⚠️ No se pudo convertir fecha: {fecha_str}")
        return None
        
    except Exception as e:
        print(f"⚠️ Error convirtiendo fecha {fecha_str}: {e}")
        return None

def poblar_partes_trabajo():
    """Poblar la base de datos con partes de trabajo de la API"""
    
    print("🏗️ Iniciando población de partes de trabajo...")
    
    # Para esta demo, voy a usar datos de ejemplo
    # Reemplaza esto con la llamada real a obtener_partes_api()
    partes_ejemplo = [
        {
            "id": "CC395D5D5F2",
            "fecha": "2025-08-22T16:05:54",
            "horaIni": "2025-08-22T15:00",
            "horaFin": "2025-08-22T16:45",
            "kilometraje": None,
            "trabajoSolicitado": "Adquisición de datos",
            "notas": "",
            "notasInternas": "",
            "notasInternasAdministracion": "0002743",
            "estado": 2,
            "dniFirma": "",
            "personaFirmante": "Fernando Makoto Takakura",
            "firmado": True,
            "archivado": False,
            "tecnicos": [
                {"user": "luis.gonzalez@parks.com.py", "nombre": "Luis González", "tipocuenta": 1},
                {"user": "carmelo.orue@parks.com.py", "nombre": "Carmelo Orué", "tipocuenta": 1},
                {"user": "edgar.ortega@parks.com.py", "nombre": "Edgar Ortega", "tipocuenta": 1}
            ],
            "cliente_codigoInterno": "Lynx",
            "cliente_id": "B69FCF55D9F",
            "cliente_empresa": "Hidrovias do Brasil (Lynx)",
            "cliente_cif": "",
            "cliente_direccion": "",
            "proyecto_id": "",
            "ejercicio": "2025",
            "numero": 113,
            "erp_id": ""
        }
        # Aquí irían más partes de trabajo de la API real
    ]
    
    # Para producción, usar esto:
    # partes_api = obtener_partes_api()
    
    db = next(get_db())
    try:
        partes_nuevos = 0
        partes_actualizados = 0
        errores = 0
        
        for parte_data in partes_ejemplo:  # Cambiar a partes_api para producción
            try:
                id_parte_api = parte_data.get('id')
                if not id_parte_api:
                    print("⚠️ Parte sin ID, saltando...")
                    continue
                
                print(f"🔄 Procesando parte {id_parte_api}...")
                
                # Verificar si ya existe
                parte_existente = db.query(ParteTrabajo).filter(
                    ParteTrabajo.id_parte_api == id_parte_api
                ).first()
                
                # Procesar técnicos
                tecnicos_asignados = []
                for tecnico_data in parte_data.get('tecnicos', []):
                    tecnico = obtener_o_crear_tecnico(db, tecnico_data)
                    tecnicos_asignados.append(tecnico)
                
                if parte_existente:
                    # Actualizar parte existente
                    parte_existente.numero = parte_data.get('numero')
                    parte_existente.ejercicio = parte_data.get('ejercicio')
                    parte_existente.fecha = convertir_fecha(parte_data.get('fecha'))
                    parte_existente.hora_inicio = convertir_fecha(parte_data.get('horaIni'))
                    parte_existente.hora_fin = convertir_fecha(parte_data.get('horaFin'))
                    parte_existente.kilometraje = parte_data.get('kilometraje')
                    parte_existente.trabajo_solicitado = parte_data.get('trabajoSolicitado')
                    parte_existente.notas = parte_data.get('notas')
                    parte_existente.notas_internas = parte_data.get('notasInternas')
                    parte_existente.notas_internas_administracion = parte_data.get('notasInternasAdministracion')
                    parte_existente.estado = parte_data.get('estado')
                    parte_existente.dni_firma = parte_data.get('dniFirma')
                    parte_existente.persona_firmante = parte_data.get('personaFirmante')
                    parte_existente.firmado = parte_data.get('firmado', False)
                    parte_existente.archivado = parte_data.get('archivado', False)
                    
                    # Datos del cliente
                    parte_existente.cliente_codigo_interno = parte_data.get('cliente_codigoInterno')
                    parte_existente.cliente_id = parte_data.get('cliente_id')
                    parte_existente.cliente_empresa = parte_data.get('cliente_empresa')
                    parte_existente.cliente_cif = parte_data.get('cliente_cif')
                    parte_existente.cliente_direccion = parte_data.get('cliente_direccion')
                    parte_existente.proyecto_id = parte_data.get('proyecto_id')
                    parte_existente.erp_id = parte_data.get('erp_id')
                    
                    # Actualizar técnicos asignados
                    parte_existente.tecnicos = tecnicos_asignados
                    
                    print(f"   ✅ Parte {parte_data.get('numero', 'N/A')} actualizado")
                    partes_actualizados += 1
                    
                else:
                    # Crear nuevo parte
                    nuevo_parte = ParteTrabajo(
                        id_parte_api=id_parte_api,
                        numero=parte_data.get('numero'),
                        ejercicio=parte_data.get('ejercicio'),
                        fecha=convertir_fecha(parte_data.get('fecha')) or datetime.now(),
                        hora_inicio=convertir_fecha(parte_data.get('horaIni')),
                        hora_fin=convertir_fecha(parte_data.get('horaFin')),
                        kilometraje=parte_data.get('kilometraje'),
                        trabajo_solicitado=parte_data.get('trabajoSolicitado'),
                        notas=parte_data.get('notas'),
                        notas_internas=parte_data.get('notasInternas'),
                        notas_internas_administracion=parte_data.get('notasInternasAdministracion'),
                        estado=parte_data.get('estado'),
                        dni_firma=parte_data.get('dniFirma'),
                        persona_firmante=parte_data.get('personaFirmante'),
                        firmado=parte_data.get('firmado', False),
                        archivado=parte_data.get('archivado', False),
                        
                        # Datos del cliente
                        cliente_codigo_interno=parte_data.get('cliente_codigoInterno'),
                        cliente_id=parte_data.get('cliente_id'),
                        cliente_empresa=parte_data.get('cliente_empresa'),
                        cliente_cif=parte_data.get('cliente_cif'),
                        cliente_direccion=parte_data.get('cliente_direccion'),
                        proyecto_id=parte_data.get('proyecto_id'),
                        erp_id=parte_data.get('erp_id')
                    )
                    
                    # Asignar técnicos
                    nuevo_parte.tecnicos = tecnicos_asignados
                    
                    db.add(nuevo_parte)
                    print(f"   ✅ Parte {parte_data.get('numero', 'N/A')} creado")
                    partes_nuevos += 1
                
                # Commit cada parte para evitar perder datos en caso de error
                db.commit()
                
            except Exception as e:
                print(f"❌ Error procesando parte {parte_data.get('id', 'desconocido')}: {e}")
                db.rollback()
                errores += 1
                continue
        
        print(f"\n🎉 Población completada:")
        print(f"   📋 Partes nuevos: {partes_nuevos}")
        print(f"   🔄 Partes actualizados: {partes_actualizados}")
        print(f"   ❌ Errores: {errores}")
        
        # Mostrar estadísticas finales
        total_partes = db.query(ParteTrabajo).count()
        total_tecnicos = db.query(Tecnico).count()
        
        print(f"\n📊 Estadísticas de la base de datos:")
        print(f"   📋 Total partes de trabajo: {total_partes}")
        print(f"   👥 Total técnicos: {total_tecnicos}")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Iniciando población de partes de trabajo...")
    print("\n⚠️ IMPORTANTE: Ajusta la URL de la API externa en la función obtener_partes_api()")
    print("   Por ahora usará datos de ejemplo.\n")
    
    poblar_partes_trabajo()
    print("\n✅ Proceso completado!")
