import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Optional
import requests
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Tecnico, ParteTrabajo, HorasExtras, Feriado
from routers.horas_extras import calcular_horas_extras

load_dotenv()

class SincronizadorAutomatico:
    """Servicio para sincronizar automáticamente datos desde la API de partes de trabajo"""
    
    def __init__(self):
        self.api_url = "https://api.partedetrabajo.com/v1/partes/"
        self.headers = {"X-Auth-Partedetrabajo-Token": os.getenv("API_TOKEN")}
        self.intervalo_segundos = 300  # 5 minutos
        self.activo = False
        self.thread = None
        
    def iniciar_sincronizacion(self):
        """Inicia la sincronización automática en un hilo separado"""
        if not self.activo:
            self.activo = True
            self.thread = threading.Thread(target=self._bucle_sincronizacion, daemon=True)
            self.thread.start()
            print(f"🚀 Sincronización automática iniciada cada {self.intervalo_segundos//60} minutos")
    
    def detener_sincronizacion(self):
        """Detiene la sincronización automática"""
        self.activo = False
        if self.thread:
            self.thread.join(timeout=5)
        print("⏹️ Sincronización automática detenida")
    
    def _bucle_sincronizacion(self):
        """Bucle principal de sincronización que se ejecuta cada 5 minutos"""
        while self.activo:
            try:
                print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Iniciando sincronización automática...")
                resultado = self.sincronizar_partes_trabajo()
                print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Sincronización completada: {resultado}")
            except Exception as e:
                print(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Error en sincronización automática: {e}")
            
            # Esperar el intervalo antes de la próxima sincronización
            time.sleep(self.intervalo_segundos)
    
    def sincronizar_partes_trabajo(self) -> dict:
        """Sincroniza partes de trabajo y calcula horas extras automáticamente"""
        db = SessionLocal()
        stats = {
            "partes_nuevos": 0,
            "partes_actualizados": 0,
            "tecnicos_nuevos": 0,
            "horas_calculadas": 0,
            "errores": 0
        }
        
        try:
            # Obtener TODOS los datos de la API usando paginación con bookmark
            todos_los_partes = self._obtener_todos_los_partes()
            
            # Filtrar solo partes finalizadas (estado = 2)
            partes_finalizadas = [p for p in todos_los_partes if p.get("estado") == 2]
            print(f"🎯 Filtrando solo partes finalizadas: {len(partes_finalizadas)} de {len(todos_los_partes)}")
            
            for parte_data in partes_finalizadas:
                try:
                    self._procesar_parte_trabajo(db, parte_data, stats)
                except Exception as e:
                    print(f"❌ Error procesando parte {parte_data.get('id', 'unknown')}: {e}")
                    stats["errores"] += 1
            
            db.commit()
            return stats
            
        except Exception as e:
            print(f"❌ Error general en sincronización: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def _obtener_todos_los_partes(self) -> list:
        """Obtiene todos los partes usando el sistema de bookmark"""
        todos_los_partes = []
        bookmark = None
        pagina = 1
        max_paginas = 20  # Límite de seguridad
        
        while pagina <= max_paginas:
            try:
                # Construir URL con bookmark si existe
                url = self.api_url
                if bookmark:
                    url += f"?bookmark={bookmark}"
                
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                docs = data.get("docs", [])
                nuevo_bookmark = data.get("bookmark")
                
                if not docs:
                    print(f"📄 Página {pagina}: No hay más documentos")
                    break
                
                print(f"📄 Página {pagina}: {len(docs)} partes obtenidos")
                todos_los_partes.extend(docs)
                
                # Si no hay nuevo bookmark o es igual al anterior, terminamos
                if not nuevo_bookmark or nuevo_bookmark == bookmark:
                    print(f"📄 Página {pagina}: No hay más páginas (bookmark)")
                    break
                
                bookmark = nuevo_bookmark
                pagina += 1
                
            except Exception as e:
                print(f"❌ Error obteniendo página {pagina}: {e}")
                break
        
        print(f"📥 Total partes obtenidos: {len(todos_los_partes)}")
        return todos_los_partes
    
    def _procesar_parte_trabajo(self, db: Session, parte_data: dict, stats: dict):
        """Procesa un parte de trabajo individual - solo partes finalizadas"""
        parte_id = parte_data.get("id")
        if not parte_id:
            return
        
        # Verificar que el parte esté finalizado (estado = 2)
        estado = parte_data.get("estado")
        if estado != 2:
            print(f"⏭️ Parte {parte_id}: Omitido - estado {estado} (no finalizado)")
            return
        
        # Verificar si el parte ya existe
        parte_existente = db.query(ParteTrabajo).filter(
            ParteTrabajo.id_parte_api == parte_id
        ).first()
        
        # Extraer información de TODOS los técnicos
        tecnicos_parte = parte_data.get("tecnicos", [])
        if not tecnicos_parte:
            print(f"⚠️ Parte {parte_id}: No se encontraron técnicos")
            return
        
        # Procesar cada técnico del parte
        tecnicos_procesados = []
        for tecnico_info in tecnicos_parte:
            tecnico_data = {
                "user": tecnico_info.get("user", ""),
                "nombre": tecnico_info.get("nombre", "Técnico"),
                "apellido": "",
                "email": tecnico_info.get("user", ""),
                "tipocuenta": tecnico_info.get("tipocuenta", 1)
            }
            
            tecnico = self._obtener_o_crear_tecnico(db, tecnico_data, stats)
            if tecnico:
                tecnicos_procesados.append(tecnico)
        
        if not tecnicos_procesados:
            print(f"⚠️ Parte {parte_id}: No se pudieron procesar técnicos")
            return
        
        # Usar el primer técnico para el parte principal (compatibilidad)
        tecnico_principal = tecnicos_procesados[0]
        
        # Extraer fechas de trabajo desde los campos correctos
        hora_inicio_str = parte_data.get("horaIni")  # "2025-08-20T14:30"
        hora_fin_str = parte_data.get("horaFin")     # "2025-08-20T17:30"
        
        if not hora_inicio_str:
            print(f"⚠️ Parte {parte_id}: No tiene hora de inicio")
            return
        
        # Para partes finalizadas, debe tener fecha de fin
        if not hora_fin_str:
            print(f"⚠️ Parte {parte_id}: Finalizado pero sin hora de fin")
            return
        
        try:
            # Parsear las fechas - formato: "2025-08-20T14:30"
            fecha_inicio = datetime.fromisoformat(hora_inicio_str)
            fecha_fin = datetime.fromisoformat(hora_fin_str)
        except Exception as e:
            print(f"❌ Error parsing fechas para parte {parte_id}: {e}")
            return
        
        if parte_existente:
            # Para partes finalizadas, verificar si cambió algo importante
            actualizado = False
            if parte_existente.fecha_fin != fecha_fin:
                parte_existente.fecha_fin = fecha_fin
                actualizado = True
            
            if actualizado:
                stats["partes_actualizados"] += 1
                print(f"🔄 Parte {parte_id}: Actualizado")
                # Recalcular horas extras para todos los técnicos
                self._calcular_horas_extras_multiples(db, parte_existente, tecnicos_procesados, stats)
            else:
                print(f"📋 Parte {parte_id}: Ya existe, sin cambios")
        else:
            # Crear nuevo parte de trabajo finalizado
            nuevo_parte = ParteTrabajo(
                id_parte_api=parte_id,
                tecnico_id=tecnico_principal.id,
                cliente_id=parte_data.get("cliente_id"),
                cliente_empresa=parte_data.get("cliente_empresa"),
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                descripcion=parte_data.get("trabajoSolicitado", ""),
                estado="finalizado"  # Sabemos que está finalizado
            )
            
            db.add(nuevo_parte)
            db.flush()  # Para obtener el ID
            stats["partes_nuevos"] += 1
            
            # Mostrar técnicos asignados
            tecnicos_nombres = [f"{t.nombre} {t.apellido}" for t in tecnicos_procesados]
            print(f"➕ Parte {parte_id}: Creado nuevo (finalizado) - Técnicos: {', '.join(tecnicos_nombres)}")
            
            # Calcular horas extras para todos los técnicos
            self._calcular_horas_extras_multiples(db, nuevo_parte, tecnicos_procesados, stats)
    
    def _extraer_info_tecnico(self, parte_data: dict) -> Optional[dict]:
        """Extrae información del técnico desde los datos del parte"""
        # La API devuelve técnicos en el campo 'tecnicos' como array
        tecnicos = parte_data.get("tecnicos", [])
        
        if tecnicos and len(tecnicos) > 0:
            # Tomar el primer técnico (o podrías procesar todos)
            primer_tecnico = tecnicos[0]
            
            # Extraer datos del técnico
            return {
                "user": primer_tecnico.get("user", ""),
                "nombre": primer_tecnico.get("nombre", "Técnico"),
                "apellido": "",  # La API no parece tener apellido separado
                "email": primer_tecnico.get("user", ""),
                "tipocuenta": primer_tecnico.get("tipocuenta", 1)
            }
        
        return None
    
    def _obtener_o_crear_tecnico(self, db: Session, tecnico_info: dict, stats: dict) -> Optional[Tecnico]:
        """Busca un técnico existente o crea uno nuevo"""
        if not tecnico_info:
            return None
        
        # Usar email como identificador único
        email = tecnico_info.get("email") or tecnico_info.get("user")
        nombre_completo = tecnico_info.get("nombre", "")
        
        # Separar nombre y apellido si viene todo junto
        partes_nombre = nombre_completo.split(" ")
        nombre = partes_nombre[0] if partes_nombre else "Técnico"
        apellido = " ".join(partes_nombre[1:]) if len(partes_nombre) > 1 else "Usuario"
        
        # Obtener legajo (parte antes del @)
        legajo = email.split("@")[0] if email else f"T{int(time.time())}"
        
        # Buscar técnico existente por email completo o por legajo parcial
        tecnico = db.query(Tecnico).filter(
            (Tecnico.legajo == email) |  # Email completo
            (Tecnico.legajo == legajo)   # Solo la parte antes del @
        ).first()
        
        if not tecnico:
            # Crear nuevo técnico
            tecnico = Tecnico(
                nombre=nombre,
                apellido=apellido,
                legajo=legajo,
                activo=True
            )
            
            db.add(tecnico)
            db.flush()
            stats["tecnicos_nuevos"] += 1
            print(f"👤 Técnico nuevo: {nombre} {apellido} (Email: {email})")
        
        return tecnico
    
    def _determinar_estado(self, fecha_inicio: datetime, fecha_fin: Optional[datetime], estado_api: int = None) -> str:
        """Determina el estado del parte basado en las fechas y estado de la API"""
        # Mapear estados de la API (basado en lo que vimos: 1, 2, etc.)
        if estado_api == 1:
            return "pendiente"
        elif estado_api == 2:
            return "finalizado"
        elif estado_api == 3:
            return "en_proceso"
        
        # Fallback basado en fechas
        if not fecha_fin:
            return "en_proceso"
        
        if fecha_fin <= datetime.now():
            return "finalizado"
        
        return "pendiente"
    
    def _calcular_horas_extras(self, db: Session, parte: ParteTrabajo, stats: dict):
        """Calcula las horas extras para un parte de trabajo"""
        if not parte.fecha_fin:
            return
        
        try:
            # Verificar si ya existe cálculo
            horas_existente = db.query(HorasExtras).filter(
                HorasExtras.parte_trabajo_id == parte.id
            ).first()
            
            if horas_existente:
                return  # Ya calculado
            
            # Calcular horas extras
            calculo = calcular_horas_extras(parte.fecha_inicio, parte.fecha_fin, db)
            
            # Crear registro
            db_horas = HorasExtras(
                parte_trabajo_id=parte.id,
                tecnico_id=parte.tecnico_id,
                fecha=parte.fecha_inicio.date(),
                hora_inicio=parte.fecha_inicio.time(),
                hora_fin=parte.fecha_fin.time(),
                horas_normales=calculo["horas_normales"],
                horas_extras_normales=calculo["horas_extras_normales"],
                horas_extras_especiales=calculo["horas_extras_especiales"],
                tipo_dia=calculo["tipo_dia"],
                calculado_automaticamente=True
            )
            
            db.add(db_horas)
            stats["horas_calculadas"] += 1
            
            print(f"⏰ Horas calculadas para parte {parte.id_parte_api}: "
                  f"{calculo['horas_normales']}h normales, "
                  f"{calculo['horas_extras_normales']}h extras, "
                  f"{calculo['horas_extras_especiales']}h especiales")
            
        except Exception as e:
            print(f"❌ Error calculando horas para parte {parte.id_parte_api}: {e}")
    
    def _calcular_horas_extras_multiples(self, db: Session, parte: ParteTrabajo, tecnicos: list, stats: dict):
        """Calcula horas extras para múltiples técnicos en un mismo parte"""
        if not parte.fecha_fin:
            return
        
        try:
            # Calcular horas extras una vez
            calculo = calcular_horas_extras(parte.fecha_inicio, parte.fecha_fin, db)
            
            # Crear registro para cada técnico
            for tecnico in tecnicos:
                # Verificar si ya existe cálculo para este técnico y parte
                horas_existente = db.query(HorasExtras).filter(
                    HorasExtras.parte_trabajo_id == parte.id,
                    HorasExtras.tecnico_id == tecnico.id
                ).first()
                
                if horas_existente:
                    continue  # Ya calculado para este técnico
                
                # Crear registro individual
                db_horas = HorasExtras(
                    parte_trabajo_id=parte.id,
                    tecnico_id=tecnico.id,
                    fecha=parte.fecha_inicio.date(),
                    hora_inicio=parte.fecha_inicio.time(),
                    hora_fin=parte.fecha_fin.time(),
                    horas_normales=calculo["horas_normales"],
                    horas_extras_normales=calculo["horas_extras_normales"],
                    horas_extras_especiales=calculo["horas_extras_especiales"],
                    tipo_dia=calculo["tipo_dia"],
                    calculado_automaticamente=True
                )
                
                db.add(db_horas)
                stats["horas_calculadas"] += 1
                
                print(f"⏰ Horas calculadas para {tecnico.nombre} {tecnico.apellido} en parte {parte.id_parte_api}: "
                      f"{calculo['horas_normales']}h normales, "
                      f"{calculo['horas_extras_normales']}h extras, "
                      f"{calculo['horas_extras_especiales']}h especiales")
            
        except Exception as e:
            print(f"❌ Error calculando horas múltiples para parte {parte.id_parte_api}: {e}")

# Instancia global del sincronizador
sincronizador_global = SincronizadorAutomatico()

def iniciar_sincronizacion_automatica():
    """Función para iniciar la sincronización automática"""
    sincronizador_global.iniciar_sincronizacion()

def detener_sincronizacion_automatica():
    """Función para detener la sincronización automática"""
    sincronizador_global.detener_sincronizacion()

def obtener_estado_sincronizacion():
    """Obtiene el estado actual de la sincronización"""
    return {
        "activo": sincronizador_global.activo,
        "intervalo_minutos": sincronizador_global.intervalo_segundos // 60,
        "api_url": sincronizador_global.api_url
    }
