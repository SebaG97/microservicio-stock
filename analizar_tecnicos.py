from database import SessionLocal
from models import Tecnico, ParteTrabajo, HorasExtras

# Verificar los técnicos únicos que deberían existir según la API
tecnicos_esperados = [
    "alejandro.rojas@parks.com.py",
    "carmelo.orue@parks.com.py", 
    "edgar.ortega@parks.com.py",
    "federico.lopez@parks.com.py",
    "javier.britez@parks.com.py",
    "luis.gonzalez@parks.com.py",
    "operaciones@parks.com.py",
    "raul.gonzalez@parks.com.py",
    "sebastian.giret@parks.com.py",
    "vicente.demoura@parks.com.py"
]

db = SessionLocal()

print("Técnicos que deberían existir:")
for i, email in enumerate(tecnicos_esperados, 1):
    print(f"  {i}. {email}")

print(f"\nTécnicos actualmente en BD:")
tecnicos_bd = db.query(Tecnico).all()
for tecnico in tecnicos_bd:
    print(f"  - {tecnico.nombre} {tecnico.apellido} (ID: {tecnico.id})")

# Contar partes por técnico para verificar
print(f"\nDistribución de partes por técnico:")
for tecnico in tecnicos_bd:
    count = db.query(ParteTrabajo).filter(ParteTrabajo.tecnico_id == tecnico.id).count()
    print(f"  - {tecnico.nombre}: {count} partes")

db.close()
