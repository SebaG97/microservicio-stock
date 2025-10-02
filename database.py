from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL - Base de datos existente para stock
DB_HOST = '192.168.100.204'
DB_PORT = '6543'
DB_NAME = 'stock_db'  # Usar la base de datos existente
DB_USER = 'postgres'
DB_PASS = '12345'

print(f"DEBUG: Conectando a postgresql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MySQL - Nueva base de datos para measurements/alarmas
MYSQL_HOST = 'db.parks.com.py'
MYSQL_PORT = '3306'
MYSQL_DB = 'parks_data'
MYSQL_USER = 'root'
MYSQL_PASS = 'ps1sw9751'

print(f"DEBUG: Configurando conexión MySQL a {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}")

MYSQL_DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

mysql_engine = create_engine(MYSQL_DATABASE_URL)
MySQLSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mysql_engine)
MySQLBase = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_mysql_db():
    db = MySQLSessionLocal()
    try:
        yield db
    finally:
        db.close()
