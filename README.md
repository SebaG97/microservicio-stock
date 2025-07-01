# Microservicio de Stock

Este proyecto es un microservicio REST para control de stock, desarrollado con FastAPI y PostgreSQL.

## Características
- Endpoints para consultar y actualizar stock
- Estructura profesional lista para futuras integraciones (facturación, reportes, etc)
- Conexión a base de datos PostgreSQL

## Requisitos
- Python 3.9+
- PostgreSQL

## Instalación
1. Crea un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Copia el archivo `.env.example` a `.env` y configura tus variables de entorno.

## Uso
```bash
uvicorn main:app --reload
```

## Estructura del proyecto
- `main.py`: punto de entrada FastAPI
- `models.py`: modelos Pydantic y SQLAlchemy
- `database.py`: conexión y utilidades de base de datos
- `routers/`: endpoints REST
- `.env.example`: ejemplo de configuración

## Futuras integraciones
- Facturación
- Reportes
- Integración con otros sistemas
