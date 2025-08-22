from database import SessionLocal
from models import Tecnico
from servicios.sincronizador_automatico import SincronizadorAutomatico

# Crear técnicos faltantes manualmente
tecnicos_faltantes = [
    {"user": "carmelo.orue@parks.com.py", "nombre": "Carmelo Orue"},
    {"user": "federico.lopez@parks.com.py", "nombre": "Federico Lopez"}, 
    {"user": "javier.britez@parks.com.py", "nombre": "Javier Britez"},
    {"user": "sebastian.giret@parks.com.py", "nombre": "Sebastian Giret"},
    {"user": "vicente.demoura@parks.com.py", "nombre": "Vicente De Moura"}
]

db = SessionLocal()

print("Creando técnicos faltantes...")

for tecnico_info in tecnicos_faltantes:
    # Verificar si ya existe
    email = tecnico_info["user"]
    existing = db.query(Tecnico).filter(Tecnico.legajo == email).first()
    
    if not existing:
        nombre_completo = tecnico_info["nombre"]
        partes_nombre = nombre_completo.split(" ")
        nombre = partes_nombre[0] if partes_nombre else "Técnico"
        apellido = " ".join(partes_nombre[1:]) if len(partes_nombre) > 1 else "Usuario"
        
        nuevo_tecnico = Tecnico(
            nombre=nombre,
            apellido=apellido,
            legajo=email,
            activo=True
        )
        
        db.add(nuevo_tecnico)
        print(f"✅ Creado: {nombre} {apellido}")
    else:
        print(f"⏭️ Ya existe: {tecnico_info['nombre']}")

db.commit()

# Verificar el resultado
print(f"\nTécnicos en BD después de la actualización:")
tecnicos = db.query(Tecnico).all()
for tecnico in tecnicos:
    print(f"  - {tecnico.nombre} {tecnico.apellido} (Legajo: {tecnico.legajo})")

print(f"\nTotal técnicos: {len(tecnicos)}")

db.close()
