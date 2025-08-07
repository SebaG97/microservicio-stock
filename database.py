from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# DEBUG: Usar la base de datos existente stock_db
DB_HOST = '192.168.100.218'
DB_PORT = '6543'
DB_NAME = 'stock_db'  # Usar la base de datos existente
DB_USER = 'postgres'
DB_PASS = '12345'

print(f"DEBUG: Conectando a postgresql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
