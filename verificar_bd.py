from database import SessionLocal
from models import Tecnico, ParteTrabajo, HorasExtras

db = SessionLocal()

tecnicos = db.query(Tecnico).count()
partes = db.query(ParteTrabajo).count()
horas = db.query(HorasExtras).count()

print(f'Tecnicos en BD: {tecnicos}')
print(f'Partes en BD: {partes}')
print(f'Registros de horas: {horas}')

print(f'\nLista de tecnicos:')
for tecnico in db.query(Tecnico).all():
    print(f'  - {tecnico.nombre} {tecnico.apellido} (ID: {tecnico.id})')

db.close()
