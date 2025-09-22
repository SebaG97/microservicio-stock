from database import get_db
from models import ParteTrabajo, HorasExtras
from sqlalchemy.orm import sessionmaker
from database import engine

Session = sessionmaker(bind=engine)
db = Session()

print('🔍 BUSCANDO ÓRDENES CON HORAS EXTRAS ESPECIALES ALTAS...')

# Buscar horas extras con más de 8 horas especiales
horas_extras_altas = db.query(HorasExtras).filter(HorasExtras.horas_extras_especiales > 8).all()

print(f'Encontradas {len(horas_extras_altas)} registros con más de 8h extras especiales:')

for he in horas_extras_altas:
    orden = he.parte_trabajo  # Usar la relación
    print(f'\n📋 Orden: {orden.id_parte_api if orden else "N/A"}')
    print(f'👷 Técnico: {he.tecnico.nombre if he.tecnico else "N/A"} (ID: {he.tecnico_id})')
    print(f'   Normales: {he.horas_normales}h')
    print(f'   Extras normales: {he.horas_extras_normales}h')
    print(f'   🚨 Extras especiales: {he.horas_extras_especiales}h')
    print(f'   Total: {he.horas_normales + he.horas_extras_normales + he.horas_extras_especiales}h')
    
    if orden:
        print(f'   📅 Fecha: {orden.fecha}')
        print(f'   ⏰ Inicio: {orden.hora_inicio}')
        print(f'   ⏰ Fin: {orden.hora_fin}')

print('\n🔍 VERIFICANDO SI EXISTE LA ORDEN 820949cfe11...')
todas_ordenes = db.query(ParteTrabajo).filter(ParteTrabajo.id_parte_api.contains('820949')).all()
print(f'Órdenes que contienen "820949": {len(todas_ordenes)}')
for orden in todas_ordenes:
    print(f'- {orden.id_parte_api}')

db.close()
