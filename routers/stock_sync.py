from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Producto, Stock, StockMovimiento, MovimientoTipo
import requests, os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/stock", tags=["stock"])

@router.post("/sync-ordenes/")
def sync_ordenes(db: Session = Depends(get_db)):
    API_URL = "https://api.partedetrabajo.com/v1/partes/"
    HEADERS = {"X-Auth-Partedetrabajo-Token": os.getenv("API_TOKEN")}
    print("Iniciando sincronización de órdenes externas...")
    response = requests.get(API_URL, headers=HEADERS)
    response.raise_for_status()
    partes = response.json().get("docs", [])
    print(f"Órdenes recibidas: {len(partes)}")
    movimientos = 0
    for parte in partes:
        parte_id = parte["id"]
        cliente_id = parte.get("cliente_id")
        cliente_empresa = parte.get("cliente_empresa")
        print(f"Procesando parte: {parte_id} (cliente: {cliente_id}, empresa: {cliente_empresa})")
        for linea in parte.get("lineasProducto", []):
            id_producto_api = linea["producto_id"]
            unidades = linea["unidades"]
            print(f"  Producto API: {id_producto_api}, Unidades: {unidades}")
            producto = db.query(Producto).filter(Producto.id_producto == id_producto_api).first()
            if not producto:
                print(f"    Producto {id_producto_api} no encontrado en base local, se omite.")
                continue
            existe = db.query(StockMovimiento).filter(
                StockMovimiento.producto_id == producto.id,
                StockMovimiento.motivo == parte_id,
                StockMovimiento.tipo == MovimientoTipo.egreso
            ).first()
            if existe:
                print(f"    Ya existe movimiento de egreso para parte {parte_id} y producto {producto.id}, se omite.")
                continue
            stock = db.query(Stock).filter(Stock.producto_id == producto.id, Stock.deposito_id == 1).first()
            if not stock:
                print(f"    No hay stock para producto {producto.id} en depósito 1, se omite.")
                continue
            if stock.existencia < unidades:
                print(f"    Stock insuficiente para producto {producto.id}: {stock.existencia} < {unidades}, se omite.")
                continue
            stock.existencia -= unidades
            movimiento = StockMovimiento(
                producto_id=producto.id,
                deposito_id=stock.deposito_id,
                cantidad=unidades,
                tipo=MovimientoTipo.egreso,
                motivo=parte_id,
                cliente_id=cliente_id,
                cliente_empresa=cliente_empresa
            )
            db.add(movimiento)
            movimientos += 1
            print(f"    Movimiento de egreso registrado para producto {producto.id}, parte {parte_id}, cliente {cliente_id}, empresa {cliente_empresa}, unidades {unidades}")
    db.commit()
    print(f"Sincronización completa. Movimientos registrados: {movimientos}")
    return {"msg": f"Sincronización completa. Movimientos registrados: {movimientos}"}
