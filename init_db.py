#!/usr/bin/env python3
from database import SessionLocal, engine
from models import Base, Deposito, Rubro, Marca, TipoProducto, Proveedor, ProductoLinea, Procedencia, Estado

def init_db():
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Verificando datos...")
        
        # Crear depósitos básicos
        if not db.query(Deposito).first():
            print("Creando depósitos...")
            depositos = [
                Deposito(nombre='Depósito Principal'),
                Deposito(nombre='Depósito Secundario'),
                Deposito(nombre='Almacén')
            ]
            for dep in depositos:
                db.add(dep)
        
        # Crear rubros básicos
        if not db.query(Rubro).first():
            print("Creando rubros...")
            rubros = [
                Rubro(nombre='Electrónicos'),
                Rubro(nombre='Herramientas'),
                Rubro(nombre='Repuestos')
            ]
            for rub in rubros:
                db.add(rub)
        
        # Crear marcas básicas
        if not db.query(Marca).first():
            print("Creando marcas...")
            marcas = [
                Marca(nombre='Samsung'),
                Marca(nombre='HP'),
                Marca(nombre='Genérica')
            ]
            for marca in marcas:
                db.add(marca)
        
        # Crear tipos de producto básicos
        if not db.query(TipoProducto).first():
            print("Creando tipos de producto...")
            tipos = [
                TipoProducto(nombre='Hardware'),
                TipoProducto(nombre='Software'),
                TipoProducto(nombre='Accesorio')
            ]
            for tipo in tipos:
                db.add(tipo)
        
        # Crear proveedores básicos
        if not db.query(Proveedor).first():
            print("Creando proveedores...")
            proveedores = [
                Proveedor(nombre='Proveedor A'),
                Proveedor(nombre='Proveedor B')
            ]
            for prov in proveedores:
                db.add(prov)
        
        # Crear líneas de producto básicas
        if not db.query(ProductoLinea).first():
            print("Creando líneas de producto...")
            lineas = [
                ProductoLinea(nombre='Línea Premium'),
                ProductoLinea(nombre='Línea Estándar')
            ]
            for linea in lineas:
                db.add(linea)
        
        # Crear procedencias básicas
        if not db.query(Procedencia).first():
            print("Creando procedencias...")
            procedencias = [
                Procedencia(nombre='Nacional'),
                Procedencia(nombre='Importado')
            ]
            for proc in procedencias:
                db.add(proc)
        
        # Crear estados básicos
        if not db.query(Estado).first():
            print("Creando estados...")
            estados = [
                Estado(nombre='Activo'),
                Estado(nombre='Inactivo'),
                Estado(nombre='Descontinuado')
            ]
            for est in estados:
                db.add(est)
        
        db.commit()
        print('✅ Datos básicos creados exitosamente')
        
        # Verificar conteos
        print(f"Depósitos: {db.query(Deposito).count()}")
        print(f"Rubros: {db.query(Rubro).count()}")
        print(f"Marcas: {db.query(Marca).count()}")
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
