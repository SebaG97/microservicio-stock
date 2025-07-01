import requests
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.partedetrabajo.com/v1/productos/"
API_TOKEN = os.getenv("API_TOKEN")
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_DATABASE')
DB_USER = os.getenv('DB_USERNAME')
DB_PASS = os.getenv('DB_PASSWORD')

HEADERS = {"X-Auth-Partedetrabajo-Token": "daab3e2d8444beedf1c3b28a8b6d4af165809f91"}

def get_api_productos():
    response = requests.get(API_URL, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_existing_productos():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    with conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id_producto, codigo, descripcion FROM productos')
            return {row[0]: {"codigo": row[1], "descripcion": row[2]} for row in cur.fetchall()}

def insert_producto(prod):
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO productos (id_producto, codigo, descripcion) VALUES (%s, %s, %s)',
                (prod["id"], prod["codigo"], prod["descripcion"])
            )
        conn.commit()

def update_producto(prod):
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE productos SET codigo = %s, descripcion = %s WHERE id_producto = %s',
                (prod["codigo"], prod["descripcion"], prod["id"])
            )
        conn.commit()

def sync_productos():
    print("Sincronizando productos...")
    api_response = get_api_productos()
    api_productos = api_response.get("docs", [])
    existentes = get_existing_productos()
    nuevos = 0
    editados = 0
    for prod in api_productos:
        prod_id = prod["id"]
        if prod_id not in existentes:
            insert_producto(prod)
            print(f"Producto nuevo guardado: {prod_id}")
            nuevos += 1
        else:
            if (prod["codigo"] != existentes[prod_id]["codigo"]) or (prod["descripcion"] != existentes[prod_id]["descripcion"]):
                update_producto(prod)
                print(f"Producto actualizado: {prod_id}")
                editados += 1
    print(f"Sincronización completa. Nuevos: {nuevos}, Editados: {editados}")

if __name__ == "__main__":
    sync_productos()
