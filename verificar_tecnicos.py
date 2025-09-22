from database import get_db
from models import Tecnico, HorasExtras, ParteTrabajo
from sqlalchemy.orm import sessionmaker
from database import engine
from sqlalchemy import func

Session = sessionmaker(bind=engine)
db = Session()

print('👷 VERIFICANDO DATOS DE TÉCNICOS...')

# Obtener todos los técnicos con sus estadísticas
tecnicos = db.query(Tecnico).all()

for tecnico in tecnicos:
    print(f'\n👤 {tecnico.nombre} (ID: {tecnico.id})')
    
    # Calcular totales de horas extras
    totales = db.query(
        func.sum(HorasExtras.horas_normales).label('total_normales'),
        func.sum(HorasExtras.horas_extras_normales).label('total_extras_normales'), 
        func.sum(HorasExtras.horas_extras_especiales).label('total_extras_especiales'),
        func.count(HorasExtras.id).label('total_ordenes')
    ).filter(HorasExtras.tecnico_id == tecnico.id).first()
    
    print(f'   📊 Horas totales:')
    print(f'      Normales: {totales.total_normales or 0}h')
    print(f'      Extras normales: {totales.total_extras_normales or 0}h') 
    print(f'      Extras especiales: {totales.total_extras_especiales or 0}h')
    print(f'      Órdenes trabajadas: {totales.total_ordenes or 0}')
    
    # Verificar si tiene campos adicionales que podrían no actualizarse
    print(f'   📋 Datos del técnico:')
    for column in tecnico.__table__.columns:
        if column.name != 'id':
            valor = getattr(tecnico, column.name)
            print(f'      {column.name}: {valor}')

print('\n🔍 VERIFICANDO POSIBLES CAMPOS NO ACTUALIZADOS...')

# Buscar campos que podrían estar desactualizados
print('Revisando si hay campos calculados en la tabla tecnicos que necesiten actualización...')

db.close()
