#!/usr/bin/env python3
"""
Script para poblar TODOS los partes de trabajo desde la API externa 
usando el sincronizador existente pero con la nueva estructura
"""

from servicios.sincronizador_automatico import SincronizadorAutomatico
from database import get_db
from models import ParteTrabajo, Tecnico
from sqlalchemy.orm import Session
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def obtener_o_crear_tecnico_mejorado(db: Session, tecnico_data):
    """Versión mejorada para obtener o crear técnicos"""
    
    email = tecnico_data.get('user')  # El campo 'user' es el email
    nombre_completo = tecnico_data.get('nombre', '')
    
    # Separar nombre y apellido
    partes_nombre = nombre_completo.strip().split(' ', 1)
    nombre = partes_nombre[0] if partes_nombre else 'Sin nombre'
    apellido = partes_nombre[1] if len(partes_nombre) > 1 else ''
    
    # Buscar técnico existente por email primero
    if email:
        tecnico = db.query(Tecnico).filter(Tecnico.email == email).first()
        if tecnico:
            # Actualizar datos si es necesario
            if not tecnico.nombre or tecnico.nombre != nombre:
                tecnico.nombre = nombre
            if not tecnico.apellido or tecnico.apellido != apellido:
                tecnico.apellido = apellido
            if tecnico.tipocuenta != tecnico_data.get('tipocuenta'):
                tecnico.tipocuenta = tecnico_data.get('tipocuenta')
            return tecnico
    
    # Buscar por nombre completo si no tiene email
    if not email and nombre:
        tecnico = db.query(Tecnico).filter(
            Tecnico.nombre == nombre,
            Tecnico.apellido == apellido
        ).first()
        if tecnico:
            return tecnico
    
    # Crear legajo único
    legajo_base = email.split('@')[0] if email else nombre.lower().replace(' ', '')
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
    
    print(f"   👥 Técnico creado: {nombre} {apellido} ({email or 'sin email'})")
    return nuevo_tecnico

def convertir_fecha_iso(fecha_str):
    """Convierte fecha de string ISO a datetime"""
    try:
        if not fecha_str:
            return None
        
        # Limpiar timezone info
        if '+' in fecha_str:
            fecha_str = fecha_str.split('+')[0]
        elif fecha_str.endswith('Z'):
            fecha_str = fecha_str[:-1]
        
        # Formatos ISO comunes
        formatos = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
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

def poblar_todos_los_partes():
    """Obtiene TODOS los partes de la API y los inserta en la nueva estructura"""
    
    print("🚀 Iniciando población completa de partes de trabajo...")
    
    # Verificar que tenemos el token de API
    api_token = os.getenv("API_TOKEN")
    if not api_token:
        print("❌ ERROR: No se encontró API_TOKEN en las variables de entorno")
        print("   Por favor configura API_TOKEN en tu archivo .env")
        return
    
    # Crear instancia del sincronizador
    sincronizador = SincronizadorAutomatico()
    
    print("📡 Obteniendo TODOS los partes de trabajo de la API...")
    try:
        # Obtener todos los partes de la API
        todos_los_partes = sincronizador._obtener_todos_los_partes()
        print(f"📥 Total partes obtenidos de la API: {len(todos_los_partes)}")
        
        if not todos_los_partes:
            print("⚠️ No se obtuvieron partes de trabajo de la API")
            return
        
        # Filtrar solo partes finalizados (opcional)
        partes_finalizados = [p for p in todos_los_partes if p.get('estado') == 2]
        print(f"🎯 Partes finalizados para procesar: {len(partes_finalizados)}")
        
        # Usar todos los partes o solo finalizados (cambia según necesites)
        partes_a_procesar = partes_finalizados  # Cambiar a todos_los_partes si quieres todos
        
    except Exception as e:
        print(f"❌ Error obteniendo datos de la API: {e}")
        return
    
    # Procesar e insertar en la base de datos
    db = next(get_db())
    try:
        partes_nuevos = 0
        partes_actualizados = 0
        partes_saltados = 0
        tecnicos_nuevos = 0
        errores = 0
        
        print(f"🏗️ Procesando {len(partes_a_procesar)} partes de trabajo...")
        
        for i, parte_data in enumerate(partes_a_procesar, 1):
            try:
                # CORRECCIÓN: Usar 'id' en lugar de '_id'
                id_parte_api = parte_data.get('id')  # Cambiar de '_id' a 'id'
                numero = parte_data.get('numero')
                
                if not id_parte_api:
                    print(f"⚠️ Parte {i}/{len(partes_a_procesar)}: Sin ID, saltando...")
                    partes_saltados += 1
                    continue
                
                if i % 10 == 0:  # Progreso cada 10 partes
                    print(f"📊 Progreso: {i}/{len(partes_a_procesar)} partes procesados...")
                
                # Verificar si ya existe
                parte_existente = db.query(ParteTrabajo).filter(
                    ParteTrabajo.id_parte_api == id_parte_api
                ).first()
                
                # Procesar técnicos
                tecnicos_asignados = []
                tecnicos_data = parte_data.get('tecnicos', [])
                
                for tecnico_data in tecnicos_data:
                    tecnico = obtener_o_crear_tecnico_mejorado(db, tecnico_data)
                    if tecnico:
                        tecnicos_asignados.append(tecnico)
                        if tecnico.id is None:  # Es nuevo
                            tecnicos_nuevos += 1
                
                # Datos comunes del parte
                datos_parte = {
                    'numero': numero,
                    'ejercicio': parte_data.get('ejercicio'),
                    'fecha': convertir_fecha_iso(parte_data.get('fecha')) or datetime.now(),
                    'hora_inicio': convertir_fecha_iso(parte_data.get('horaIni')),
                    'hora_fin': convertir_fecha_iso(parte_data.get('horaFin')),
                    'kilometraje': parte_data.get('kilometraje'),
                    'trabajo_solicitado': parte_data.get('trabajoSolicitado'),
                    'notas': parte_data.get('notas', ''),
                    'notas_internas': parte_data.get('notasInternas', ''),
                    'notas_internas_administracion': parte_data.get('notasInternasAdministracion', ''),
                    'estado': parte_data.get('estado'),
                    'dni_firma': parte_data.get('dniFirma', ''),
                    'persona_firmante': parte_data.get('personaFirmante', ''),
                    'firmado': parte_data.get('firmado', False),
                    'archivado': parte_data.get('archivado', False),
                    
                    # Datos del cliente
                    'cliente_codigo_interno': parte_data.get('cliente_codigoInterno'),
                    'cliente_id': parte_data.get('cliente_id'),
                    'cliente_empresa': parte_data.get('cliente_empresa'),
                    'cliente_cif': parte_data.get('cliente_cif', ''),
                    'cliente_direccion': parte_data.get('cliente_direccion', ''),
                    'cliente_provincia': parte_data.get('cliente_provincia', ''),
                    'cliente_localidad': parte_data.get('cliente_localidad', ''),
                    'cliente_pais': parte_data.get('cliente_pais', ''),
                    'cliente_telefono': parte_data.get('cliente_telefono', ''),
                    'cliente_email': parte_data.get('cliente_email', ''),
                    'cliente_erp_id': parte_data.get('cliente_erp_id', ''),
                    
                    'proyecto_id': parte_data.get('proyecto_id', ''),
                    'erp_id': parte_data.get('erp_id', '')
                }
                
                if parte_existente:
                    # Actualizar parte existente
                    for campo, valor in datos_parte.items():
                        setattr(parte_existente, campo, valor)
                    
                    # Actualizar técnicos asignados
                    parte_existente.tecnicos = tecnicos_asignados
                    
                    partes_actualizados += 1
                    
                else:
                    # Crear nuevo parte
                    nuevo_parte = ParteTrabajo(
                        id_parte_api=id_parte_api,
                        **datos_parte
                    )
                    
                    # Asignar técnicos
                    nuevo_parte.tecnicos = tecnicos_asignados
                    
                    db.add(nuevo_parte)
                    partes_nuevos += 1
                
                # Commit cada 20 partes para evitar transacciones muy largas
                if i % 20 == 0:
                    db.commit()
                
            except Exception as e:
                print(f"❌ Error procesando parte {i} (ID: {parte_data.get('_id', 'desconocido')}): {e}")
                db.rollback()
                errores += 1
                continue
        
        # Commit final
        db.commit()
        
        print(f"\n🎉 Población completa terminada:")
        print(f"   📋 Partes nuevos: {partes_nuevos}")
        print(f"   🔄 Partes actualizados: {partes_actualizados}")
        print(f"   ⏭️ Partes saltados: {partes_saltados}")
        print(f"   👥 Técnicos nuevos: {tecnicos_nuevos}")
        print(f"   ❌ Errores: {errores}")
        
        # Estadísticas finales
        total_partes = db.query(ParteTrabajo).count()
        total_tecnicos = db.query(Tecnico).count()
        
        print(f"\n📊 Estadísticas finales de la base de datos:")
        print(f"   📋 Total partes de trabajo: {total_partes}")
        print(f"   👥 Total técnicos: {total_tecnicos}")
        
        # Mostrar algunos ejemplos
        print(f"\n📋 Ejemplos de partes poblados:")
        ejemplos = db.query(ParteTrabajo).limit(5).all()
        for parte in ejemplos:
            print(f"   - Parte {parte.numero}: {parte.trabajo_solicitado} ({len(parte.tecnicos)} técnicos)")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Script de población completa de partes de trabajo")
    print("   Este script obtendrá TODOS los partes de la API externa")
    print("   y los insertará en la nueva estructura de base de datos.\n")
    
    # Confirmación de seguridad
    confirmar = input("¿Deseas continuar? (s/N): ").lower().strip()
    if confirmar != 's':
        print("❌ Operación cancelada")
        exit()
    
    poblar_todos_los_partes()
    print("\n✅ Proceso completado!")
