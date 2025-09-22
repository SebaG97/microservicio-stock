from database import get_db
from models import ParteTrabajo, HorasExtras
from sqlalchemy.orm import sessionmaker
from database import engine
from datetime import datetime

Session = sessionmaker(bind=engine)
db = Session()

# Buscar la orden específica
orden = db.query(ParteTrabajo).filter(ParteTrabajo.id_parte_api == '820949cfe11').first()

if orden:
    print(f'📋 Orden: {orden.id_parte_api}')
    print(f'📅 Fecha: {orden.fecha}')
    print(f'⏰ Hora inicio: {orden.hora_inicio}')
    print(f'⏰ Hora fin: {orden.hora_fin}')
    print(f'📊 Estado: {orden.estado}')
    print(f'👷 Técnicos: {len(orden.tecnicos) if orden.tecnicos else 0}')
    if orden.tecnicos:
        for tec in orden.tecnicos:
            print(f'   - {tec.nombre} (ID: {tec.id_tecnico})')
    
    print('\n🕒 HORAS EXTRAS CALCULADAS:')
    horas_extras = db.query(HorasExtras).filter(HorasExtras.id_parte_api == orden.id_parte_api).all()
    for he in horas_extras:
        print(f'👷 Técnico: {he.tecnico.nombre if he.tecnico else "N/A"}')
        print(f'   Normales: {he.horas_normales}h')
        print(f'   Extras normales: {he.horas_extras_normales}h')
        print(f'   Extras especiales: {he.horas_extras_especiales}h')
        print(f'   Total: {he.total_horas}h')
        print('---')
else:
    print('❌ Orden no encontrada')

db.close()
