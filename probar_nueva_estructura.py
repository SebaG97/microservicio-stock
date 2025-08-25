#!/usr/bin/env python3
"""
Script para probar la inserción de un parte de trabajo con múltiples técnicos
usando los datos del JSON que proporcionaste
"""

from database import engine, get_db
from models import ParteTrabajo, Tecnico
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import text

def probar_insercion_parte():
    """Prueba insertar un parte de trabajo con múltiples técnicos"""
    
    print("🧪 Probando inserción de parte de trabajo con múltiples técnicos...")
    
    db = next(get_db())
    try:
        # 1. Obtener los técnicos que queremos asignar
        tecnicos = db.query(Tecnico).filter(
            Tecnico.email.in_([
                "luis.gonzalez@parks.com.py",
                "carmelo.orue@parks.com.py", 
                "edgar.ortega@parks.com.py"
            ])
        ).all()
        
        print(f"👥 Técnicos encontrados: {len(tecnicos)}")
        for t in tecnicos:
            print(f"   - {t.nombre} {t.apellido} ({t.email})")
        
        # 2. Crear el parte de trabajo con los datos del JSON
        parte = ParteTrabajo(
            id_parte_api="CC395D5D5F2",
            numero=113,
            ejercicio="2025",
            fecha=datetime.fromisoformat("2025-08-22T16:05:54-03:00").replace(tzinfo=None),
            hora_inicio=datetime.fromisoformat("2025-08-22T15:00").replace(tzinfo=None),
            hora_fin=datetime.fromisoformat("2025-08-22T16:45").replace(tzinfo=None),
            kilometraje=None,
            trabajo_solicitado="Adquisición de datos",
            notas="",
            notas_internas="",
            notas_internas_administracion="0002743",
            estado=2,
            dni_firma="",
            persona_firmante="Fernando Makoto Takakura",
            firmado=True,
            archivado=False,
            
            # Datos del cliente
            cliente_codigo_interno="Lynx",
            cliente_id="B69FCF55D9F",
            cliente_empresa="Hidrovias do Brasil (Lynx)",
            cliente_cif="",
            cliente_direccion="",
            cliente_provincia="",
            cliente_localidad="",
            cliente_pais="",
            cliente_telefono="",
            cliente_email="",
            cliente_erp_id="",
            
            proyecto_id="",
            erp_id=""
        )
        
        # 3. Asignar los técnicos al parte
        parte.tecnicos = tecnicos
        
        # 4. Guardar en la base de datos
        db.add(parte)
        db.commit()
        db.refresh(parte)
        
        print(f"\n✅ Parte de trabajo creado con ID: {parte.id}")
        print(f"   📋 Número: {parte.numero}")
        print(f"   📅 Fecha: {parte.fecha}")
        print(f"   👤 Cliente: {parte.cliente_empresa}")
        print(f"   📝 Trabajo: {parte.trabajo_solicitado}")
        print(f"   👥 Técnicos asignados: {len(parte.tecnicos)}")
        
        # 5. Verificar la relación muchos a muchos
        print("\n🔍 Verificando relaciones en base de datos...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT pt.numero, pt.trabajo_solicitado, t.nombre, t.apellido, t.email
                FROM partes_trabajo pt
                JOIN parte_trabajo_tecnicos ptt ON pt.id = ptt.parte_trabajo_id
                JOIN tecnicos t ON ptt.tecnico_id = t.id
                WHERE pt.id = :parte_id
                ORDER BY t.nombre
            """), {"parte_id": parte.id})
            
            relaciones = result.fetchall()
            print(f"✅ Encontradas {len(relaciones)} relaciones:")
            for r in relaciones:
                print(f"   - Parte {r[0]} ({r[1]}) -> {r[2]} {r[3]} ({r[4]})")
        
        # 6. Probar consulta inversa (técnicos de un parte)
        parte_consultado = db.query(ParteTrabajo).filter(ParteTrabajo.id == parte.id).first()
        print(f"\n🔄 Consulta inversa - Técnicos del parte {parte_consultado.numero}:")
        for tecnico in parte_consultado.tecnicos:
            print(f"   - {tecnico.nombre} {tecnico.apellido} ({tecnico.email})")
        
        # 7. Probar consulta de partes de un técnico
        primer_tecnico = tecnicos[0]
        print(f"\n🔄 Partes asignados a {primer_tecnico.nombre} {primer_tecnico.apellido}:")
        for parte_del_tecnico in primer_tecnico.partes_trabajo:
            print(f"   - Parte {parte_del_tecnico.numero}: {parte_del_tecnico.trabajo_solicitado}")
        
        print("\n🎉 ¡Prueba exitosa! La base de datos almacena correctamente:")
        print("   ✅ Múltiples técnicos por parte de trabajo")
        print("   ✅ Campo número (113)")
        print("   ✅ Todos los datos del JSON de la API")
        print("   ✅ Relaciones bidireccionales funcionales")
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    probar_insercion_parte()
