from fastapi import FastAPI
from routers import stock, marcas, tipo_producto, proveedores, producto_lineas, procedencias, estados, depositos, productos, rubros
from database import engine
from models import Base
from fastapi.middleware.cors import CORSMiddleware
from database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from models import Producto

app = FastAPI(title="Microservicio de Stock")

# Crear todas las tablas automáticamente al iniciar
Base.metadata.create_all(bind=engine)

app.include_router(stock.router, prefix="/api")
app.include_router(marcas.router, prefix="/api")
app.include_router(tipo_producto.router, prefix="/api")
app.include_router(proveedores.router, prefix="/api")
app.include_router(producto_lineas.router, prefix="/api")
app.include_router(procedencias.router, prefix="/api")
app.include_router(estados.router, prefix="/api")
app.include_router(depositos.router, prefix="/api")
app.include_router(productos.router, prefix="/api")
app.include_router(rubros.router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir cualquier origen para desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/productos")
def get_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()
    print(productos)
    return [
        {
            "id_producto": getattr(p, "id_producto", None),
            "codigo": getattr(p, "codigo", None),
            "descripcion": getattr(p, "descripcion", None)
        } for p in productos
    ]
