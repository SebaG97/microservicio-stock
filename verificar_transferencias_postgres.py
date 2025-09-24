#!/usr/bin/env python3
"""
Script para verificar y corregir los movimientos de transferencia en PostgreSQL
"""

from sqlalchemy.orm import Session
from database import get_db, engine
from models import StockMovimiento, Stock, Producto, Deposito
from schemas import MovimientoTipo
from datetime import datetime

def verificar_transferencias():
    """Verificar movimientos de transferencia incorrectos"""
    db = next(get_db())
    
    print("🔍 Verificando movimientos de transferencia en PostgreSQL...")
    
    # Buscar movimientos de ajuste con motivo transferencia_deposito
    movimientos_incorrectos = db.query(StockMovimiento).filter(
        StockMovimiento.tipo == MovimientoTipo.ajuste,
        StockMovimiento.motivo == "transferencia_deposito"
    ).order_by(StockMovimiento.fecha.desc()).all()
    
    if not movimientos_incorrectos:
        print("✅ No se encontraron movimientos incorrectos con tipo 'ajuste' y motivo 'transferencia_deposito'")
        
        # Buscar cualquier movimiento con motivo transferencia_deposito
        todos_transferencias = db.query(StockMovimiento).filter(
            StockMovimiento.motivo == "transferencia_deposito"
        ).order_by(StockMovimiento.fecha.desc()).all()
        
        if todos_transferencias:
            print(f"📋 Se encontraron {len(todos_transferencias)} movimientos con motivo 'transferencia_deposito':")
            for mov in todos_transferencias:
                producto = db.query(Producto).filter(Producto.id == mov.producto_id).first()
                deposito = db.query(Deposito).filter(Deposito.id == mov.deposito_id).first()
                print(f"  - ID {mov.id}: {producto.descripcion if producto else 'Producto ' + str(mov.producto_id)} en {deposito.nombre if deposito else 'Depósito ' + str(mov.deposito_id)} - Cantidad: {mov.cantidad} - Tipo: {mov.tipo} - Fecha: {mov.fecha}")
    else:
        print(f"❌ Se encontraron {len(movimientos_incorrectos)} movimientos incorrectos:")
        for mov in movimientos_incorrectos:
            producto = db.query(Producto).filter(Producto.id == mov.producto_id).first()
            deposito = db.query(Deposito).filter(Deposito.id == mov.deposito_id).first()
            print(f"  - ID {mov.id}: {producto.descripcion if producto else 'Producto ' + str(mov.producto_id)} en {deposito.nombre if deposito else 'Depósito ' + str(mov.deposito_id)} - Cantidad: {mov.cantidad} - Fecha: {mov.fecha}")
    
    # Mostrar stock actual
    print("\n📊 Stock actual por producto y depósito:")
    stocks = db.query(Stock).filter(Stock.existencia > 0).order_by(Stock.producto_id, Stock.deposito_id).all()
    
    for stock in stocks:
        producto = db.query(Producto).filter(Producto.id == stock.producto_id).first()
        deposito = db.query(Deposito).filter(Deposito.id == stock.deposito_id).first()
        print(f"  - {producto.nombre if producto else 'Producto ' + str(stock.producto_id)} en {deposito.nombre if deposito else 'Depósito ' + str(stock.deposito_id)}: {stock.existencia} unidades")
    
    db.close()
    return movimientos_incorrectos

def corregir_movimientos_incorrectos(movimientos):
    """Corregir los movimientos que fueron mal registrados"""
    if not movimientos:
        print("✅ No hay movimientos que corregir")
        return
    
    db = next(get_db())
    
    print(f"\n🔧 Corrigiendo {len(movimientos)} movimientos incorrectos...")
    
    for mov in movimientos:
        # Restar la cantidad que se sumó incorrectamente
        stock = db.query(Stock).filter(
            Stock.producto_id == mov.producto_id,
            Stock.deposito_id == mov.deposito_id
        ).first()
        
        if stock:
            stock.existencia -= mov.cantidad
            print(f"  ✅ Corregido stock de producto {mov.producto_id} en depósito {mov.deposito_id}: restadas {mov.cantidad} unidades")
        
        # Cambiar el tipo de movimiento para reflejar la corrección
        mov.tipo = MovimientoTipo.egreso
        mov.motivo = "correccion_transferencia_erronea"
    
    db.commit()
    db.close()
    print("✅ Corrección completada")

if __name__ == "__main__":
    movimientos_incorrectos = verificar_transferencias()
    
    if movimientos_incorrectos:
        respuesta = input("\n¿Deseas corregir estos movimientos? (s/n): ")
        if respuesta.lower() == 's':
            corregir_movimientos_incorrectos(movimientos_incorrectos)
        else:
            print("❌ Corrección cancelada")