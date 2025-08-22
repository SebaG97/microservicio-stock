#!/usr/bin/env python3
from database import SessionLocal
from models import Tecnico, Feriado, ParteTrabajo, HorasExtras
from datetime import datetime, date, time

def init_horas_extras_data():
    """Inicializa datos de ejemplo para el sistema de horas extras"""
    db = SessionLocal()
    
    try:
        print("Inicializando datos para sistema de horas extras...")
        
        # Crear técnicos de ejemplo
        if not db.query(Tecnico).first():
            print("Creando técnicos de ejemplo...")
            tecnicos = [
                Tecnico(nombre="Juan", apellido="Pérez", legajo="T001", activo=True),
                Tecnico(nombre="María", apellido="González", legajo="T002", activo=True),
                Tecnico(nombre="Carlos", apellido="Rodríguez", legajo="T003", activo=True),
                Tecnico(nombre="Ana", apellido="López", legajo="T004", activo=True),
                Tecnico(nombre="Pedro", apellido="Martínez", legajo="T005", activo=True),
            ]
            for tecnico in tecnicos:
                db.add(tecnico)
        
        # Crear feriados de ejemplo (2025)
        if not db.query(Feriado).first():
            print("Creando feriados de ejemplo...")
            feriados = [
                Feriado(fecha=date(2025, 1, 1), nombre="Año Nuevo"),
                Feriado(fecha=date(2025, 2, 24), nombre="Carnaval"),
                Feriado(fecha=date(2025, 2, 25), nombre="Carnaval"),
                Feriado(fecha=date(2025, 3, 24), nombre="Día Nacional de la Memoria"),
                Feriado(fecha=date(2025, 4, 2), nombre="Día del Veterano"),
                Feriado(fecha=date(2025, 4, 18), nombre="Viernes Santo"),
                Feriado(fecha=date(2025, 5, 1), nombre="Día del Trabajador"),
                Feriado(fecha=date(2025, 5, 25), nombre="Revolución de Mayo"),
                Feriado(fecha=date(2025, 6, 16), nombre="Paso a la Inmortalidad de Güemes"),
                Feriado(fecha=date(2025, 6, 20), nombre="Paso a la Inmortalidad de Belgrano"),
                Feriado(fecha=date(2025, 7, 9), nombre="Día de la Independencia"),
                Feriado(fecha=date(2025, 8, 15), nombre="Paso a la Inmortalidad de San Martín"),
                Feriado(fecha=date(2025, 10, 13), nombre="Día del Respeto a la Diversidad Cultural"),
                Feriado(fecha=date(2025, 11, 21), nombre="Día de la Soberanía Nacional"),
                Feriado(fecha=date(2025, 12, 8), nombre="Inmaculada Concepción"),
                Feriado(fecha=date(2025, 12, 25), nombre="Navidad"),
            ]
            for feriado in feriados:
                db.add(feriado)
        
        # Crear algunos partes de trabajo de ejemplo
        if not db.query(ParteTrabajo).first():
            print("Creando partes de trabajo de ejemplo...")
            
            # Obtener técnicos
            tecnicos = db.query(Tecnico).all()
            
            if tecnicos:
                partes_ejemplo = [
                    # Trabajo normal (lunes 8-17)
                    ParteTrabajo(
                        id_parte_api="PART001",
                        tecnico_id=tecnicos[0].id,
                        cliente_id="CLI001",
                        cliente_empresa="Empresa ABC",
                        fecha_inicio=datetime(2025, 1, 6, 8, 0),  # lunes 8:00
                        fecha_fin=datetime(2025, 1, 6, 17, 0),   # lunes 17:00
                        descripcion="Mantenimiento preventivo",
                        estado="finalizado"
                    ),
                    # Trabajo con horas extras normales (lunes 8-19)
                    ParteTrabajo(
                        id_parte_api="PART002",
                        tecnico_id=tecnicos[1].id,
                        cliente_id="CLI002",
                        cliente_empresa="Empresa XYZ",
                        fecha_inicio=datetime(2025, 1, 6, 8, 0),  # lunes 8:00
                        fecha_fin=datetime(2025, 1, 6, 19, 0),   # lunes 19:00
                        descripcion="Reparación urgente",
                        estado="finalizado"
                    ),
                    # Trabajo nocturno (horas especiales)
                    ParteTrabajo(
                        id_parte_api="PART003",
                        tecnico_id=tecnicos[2].id,
                        cliente_id="CLI003",
                        cliente_empresa="Empresa 123",
                        fecha_inicio=datetime(2025, 1, 6, 22, 0),  # lunes 22:00
                        fecha_fin=datetime(2025, 1, 7, 2, 0),     # martes 2:00
                        descripcion="Emergencia nocturna",
                        estado="finalizado"
                    ),
                    # Trabajo fin de semana (domingo - horas especiales)
                    ParteTrabajo(
                        id_parte_api="PART004",
                        tecnico_id=tecnicos[3].id,
                        cliente_id="CLI004",
                        cliente_empresa="Empresa ABC",
                        fecha_inicio=datetime(2025, 1, 5, 10, 0),  # domingo 10:00
                        fecha_fin=datetime(2025, 1, 5, 14, 0),    # domingo 14:00
                        descripcion="Soporte fin de semana",
                        estado="finalizado"
                    ),
                    # Trabajo sábado normal
                    ParteTrabajo(
                        id_parte_api="PART005",
                        tecnico_id=tecnicos[4].id,
                        cliente_id="CLI005",
                        cliente_empresa="Empresa XYZ",
                        fecha_inicio=datetime(2025, 1, 4, 8, 0),  # sábado 8:00
                        fecha_fin=datetime(2025, 1, 4, 12, 0),   # sábado 12:00
                        descripcion="Mantenimiento semanal",
                        estado="finalizado"
                    ),
                    # Trabajo sábado con horas extras
                    ParteTrabajo(
                        id_parte_api="PART006",
                        tecnico_id=tecnicos[0].id,
                        cliente_id="CLI006",
                        cliente_empresa="Empresa 123",
                        fecha_inicio=datetime(2025, 1, 4, 8, 0),  # sábado 8:00
                        fecha_fin=datetime(2025, 1, 4, 15, 0),   # sábado 15:00
                        descripcion="Instalación especial",
                        estado="finalizado"
                    ),
                ]
                
                for parte in partes_ejemplo:
                    db.add(parte)
        
        db.commit()
        print("✅ Datos de horas extras inicializados correctamente")
        
        # Mostrar resumen
        print(f"Técnicos: {db.query(Tecnico).count()}")
        print(f"Feriados: {db.query(Feriado).count()}")
        print(f"Partes de trabajo: {db.query(ParteTrabajo).count()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_horas_extras_data()
