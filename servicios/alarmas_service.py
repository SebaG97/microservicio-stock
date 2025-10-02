"""
Servicio para gestionar las alarmas de vessels basado en la última recepción de datos.

Reglas de alarma:
- Verde: Datos recientes (menos de 2 horas)
- Amarillo: 2-8 horas sin datos nuevos
- Naranja: 8-12 horas sin datos nuevos  
- Rojo: Más de 12 horas sin datos nuevos
"""

from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from models_mysql import Measurement
from schemas import AlarmaVessel, EstadoAlarma, ListaAlarmas


class AlarmasService:
    """Servicio para calcular y gestionar las alarmas de vessels"""
    
    @staticmethod
    def calcular_estado_alarma(horas_sin_datos: float) -> EstadoAlarma:
        """
        Calcula el estado de alarma basado en las horas sin datos
        
        Args:
            horas_sin_datos: Número de horas desde el último dato recibido
            
        Returns:
            EstadoAlarma correspondiente
        """
        if horas_sin_datos < 2:
            return EstadoAlarma.VERDE
        elif horas_sin_datos < 8:
            return EstadoAlarma.AMARILLO
        elif horas_sin_datos < 12:
            return EstadoAlarma.NARANJA
        else:
            return EstadoAlarma.ROJO
    
    @staticmethod
    def generar_mensaje_alarma(vessel_name: str, horas_sin_datos: float, estado: EstadoAlarma) -> str:
        """
        Genera un mensaje descriptivo para la alarma
        
        Args:
            vessel_name: Nombre del vessel
            horas_sin_datos: Horas sin recibir datos
            estado: Estado de la alarma
            
        Returns:
            Mensaje descriptivo
        """
        if estado == EstadoAlarma.VERDE:
            return f"Vessel {vessel_name} operando normalmente"
        elif estado == EstadoAlarma.AMARILLO:
            return f"Vessel {vessel_name}: {horas_sin_datos:.1f}h sin datos - Advertencia"
        elif estado == EstadoAlarma.NARANJA:
            return f"Vessel {vessel_name}: {horas_sin_datos:.1f}h sin datos - Atención requerida"
        else:  # ROJO
            return f"Vessel {vessel_name}: {horas_sin_datos:.1f}h sin datos - CRÍTICO"
    
    @staticmethod
    def obtener_ultimo_dato_por_vessel(db: Session) -> Dict[str, datetime]:
        """
        Obtiene el timestamp del último dato recibido para cada vessel
        
        Args:
            db: Sesión de base de datos MySQL
            
        Returns:
            Diccionario con vessel_name como clave y último timestamp como valor
        """
        # Subconsulta para obtener el máximo timestamp por vessel
        subq = db.query(
            Measurement.vessel_name,
            func.max(Measurement.timestamp).label('ultimo_timestamp')
        ).group_by(Measurement.vessel_name).subquery()
        
        # Consulta principal para obtener los registros completos
        resultados = db.query(subq.c.vessel_name, subq.c.ultimo_timestamp).all()
        
        return {resultado.vessel_name: resultado.ultimo_timestamp for resultado in resultados}
    
    @staticmethod
    def calcular_alarmas_vessels(db: Session) -> ListaAlarmas:
        """
        Calcula todas las alarmas para todos los vessels
        
        Args:
            db: Sesión de base de datos MySQL
            
        Returns:
            ListaAlarmas con todos los vessels y sus estados
        """
        now = datetime.now()
        ultimo_dato_por_vessel = AlarmasService.obtener_ultimo_dato_por_vessel(db)
        
        alarmas = []
        resumen = {"verde": 0, "amarillo": 0, "naranja": 0, "rojo": 0}
        
        for vessel_name, ultimo_timestamp in ultimo_dato_por_vessel.items():
            # Calcular horas sin datos
            tiempo_diferencia = now - ultimo_timestamp
            horas_sin_datos = tiempo_diferencia.total_seconds() / 3600
            
            # Determinar estado de alarma
            estado_alarma = AlarmasService.calcular_estado_alarma(horas_sin_datos)
            
            # Generar mensaje
            mensaje = AlarmasService.generar_mensaje_alarma(vessel_name, horas_sin_datos, estado_alarma)
            
            # Crear alarma
            alarma = AlarmaVessel(
                vessel_name=vessel_name,
                ultimo_dato=ultimo_timestamp,
                horas_sin_datos=round(horas_sin_datos, 2),
                estado_alarma=estado_alarma,
                mensaje=mensaje
            )
            
            alarmas.append(alarma)
            resumen[estado_alarma.value] += 1
        
        # Ordenar por estado de alarma (críticos primero) y luego por horas sin datos
        orden_prioridad = {EstadoAlarma.ROJO: 0, EstadoAlarma.NARANJA: 1, 
                          EstadoAlarma.AMARILLO: 2, EstadoAlarma.VERDE: 3}
        
        alarmas.sort(key=lambda x: (orden_prioridad[x.estado_alarma], -x.horas_sin_datos))
        
        return ListaAlarmas(
            total_vessels=len(alarmas),
            alarmas=alarmas,
            resumen=resumen
        )
    
    @staticmethod
    def obtener_vessels_criticos(db: Session, max_horas: float = 12.0) -> List[AlarmaVessel]:
        """
        Obtiene solo los vessels en estado crítico (más de X horas sin datos)
        
        Args:
            db: Sesión de base de datos MySQL
            max_horas: Número máximo de horas para considerar crítico (default: 12)
            
        Returns:
            Lista de alarmas en estado crítico
        """
        todas_alarmas = AlarmasService.calcular_alarmas_vessels(db)
        return [alarma for alarma in todas_alarmas.alarmas 
                if alarma.horas_sin_datos >= max_horas]