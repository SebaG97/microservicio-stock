"""
Script para corregir las fechas de los partes de trabajo
Actualiza las fechas con los datos originales de la API externa
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import re
from database import SessionLocal
import models
from servicios.sincronizador_automatico import SincronizadorAutomatico

def convertir_fecha_iso_mejorado(fecha_str):
    """Convierte fecha de string ISO a datetime, manejando timezones"""
    try:
        if not fecha_str:
            return None
        
        # Limpiar timezone info (tanto +XX:XX como -XX:XX)
        if '+' in fecha_str:
            fecha_str = fecha_str.split('+')[0]
        elif '-03:00' in fecha_str:
            fecha_str = fecha_str.replace('-03:00', '')
        elif fecha_str.endswith('Z'):
            fecha_str = fecha_str[:-1]
        
        # Remover cualquier timezone restante al final
        fecha_str = re.sub(r'[+-]\d{2}:\d{2}$', '', fecha_str)
        
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

def corregir_fechas_partes():
    """Corrige las fechas de los partes de trabajo con datos de la API"""
    db = SessionLocal()
    sincronizador = SincronizadorAutomatico()
    
    try:
        print("🔄 Obteniendo datos de la API externa...")
        partes_api = sincronizador._obtener_todos_los_partes()
        
        if not partes_api:
            print("❌ No se pudieron obtener datos de la API")
            return
        
        print(f"📊 Procesando {len(partes_api)} partes de trabajo...")
        
        actualizados = 0
        errores = 0
        
        for i, parte_data in enumerate(partes_api, 1):
            try:
                parte_id_api = parte_data.get("id")
                if not parte_id_api:
                    continue
                
                # Buscar el parte en la BD local
                parte_local = db.query(models.ParteTrabajo).filter(
                    models.ParteTrabajo.id_parte_api == parte_id_api
                ).first()
                
                if not parte_local:
                    print(f"⚠️ Parte no encontrado en BD: {parte_id_api}")
                    continue
                
                # Obtener y convertir la fecha original
                fecha_original_str = parte_data.get("fecha")
                if not fecha_original_str:
                    print(f"⚠️ Parte sin fecha en API: {parte_id_api}")
                    continue
                
                fecha_original = convertir_fecha_iso_mejorado(fecha_original_str)
                if not fecha_original:
                    print(f"❌ No se pudo convertir fecha para {parte_id_api}: {fecha_original_str}")
                    errores += 1
                    continue
                
                # Actualizar la fecha si es diferente
                if parte_local.fecha != fecha_original:
                    fecha_anterior = parte_local.fecha
                    parte_local.fecha = fecha_original
                    
                    print(f"📅 Parte {parte_local.numero or 'S/N'} (ID: {parte_id_api})")
                    print(f"   Fecha anterior: {fecha_anterior}")
                    print(f"   Fecha corregida: {fecha_original}")
                    
                    actualizados += 1
                
                # También actualizar hora_inicio y hora_fin si están disponibles
                if "horaIni" in parte_data:
                    hora_ini = convertir_fecha_iso_mejorado(parte_data["horaIni"])
                    if hora_ini and parte_local.hora_inicio != hora_ini:
                        parte_local.hora_inicio = hora_ini
                
                if "horaFin" in parte_data:
                    hora_fin = convertir_fecha_iso_mejorado(parte_data["horaFin"])
                    if hora_fin and parte_local.hora_fin != hora_fin:
                        parte_local.hora_fin = hora_fin
                
                # Commit cada 10 registros
                if i % 10 == 0:
                    db.commit()
                    print(f"📈 Procesados {i}/{len(partes_api)} partes...")
                
            except Exception as e:
                print(f"❌ Error procesando parte {parte_id_api}: {e}")
                errores += 1
                continue
        
        # Commit final
        db.commit()
        
        print(f"\n✅ Corrección de fechas completada:")
        print(f"   📅 Fechas actualizadas: {actualizados}")
        print(f"   ❌ Errores: {errores}")
        print(f"   📊 Total procesados: {len(partes_api)}")
        
        # Verificar algunos ejemplos
        print(f"\n📋 Ejemplos de fechas corregidas:")
        ejemplos = db.query(models.ParteTrabajo).order_by(models.ParteTrabajo.numero.desc()).limit(5).all()
        for parte in ejemplos:
            print(f"   - Parte {parte.numero}: {parte.fecha.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Error durante la corrección: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Script de corrección de fechas de partes de trabajo")
    print("   Este script actualizará las fechas con los datos originales de la API")
    print()
    
    respuesta = input("¿Deseas continuar? (s/N): ")
    if respuesta.lower() in ['s', 'si', 'sí', 'yes', 'y']:
        corregir_fechas_partes()
    else:
        print("❌ Operación cancelada")
