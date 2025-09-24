#!/usr/bin/env python3
"""
Script para corregir las transferencias erróneas que se realizaron como ajustes
"""

import sqlite3
from datetime import datetime

def corregir_transferencias():
    conn = sqlite3.connect('stock.db')
    cursor = conn.cursor()
    
    print("🔍 Buscando movimientos de transferencia incorrectos...")
    
    # Buscar movimientos de ajuste con motivo transferencia_deposito
    cursor.execute("""
        SELECT sm.id, sm.fecha, sm.producto_id, sm.deposito_id, sm.cantidad, 
               p.nombre as producto_nombre, d.nombre as deposito_nombre
        FROM stock_movimientos sm
        JOIN productos p ON sm.producto_id = p.id
        JOIN depositos d ON sm.deposito_id = d.id
        WHERE sm.tipo = 'ajuste' AND sm.motivo = 'transferencia_deposito'
        ORDER BY sm.fecha DESC
    """)
    
    movimientos_incorrectos = cursor.fetchall()
    
    if not movimientos_incorrectos:
        print("✅ No se encontraron movimientos incorrectos de transferencia")
        conn.close()
        return
    
    print(f"❌ Se encontraron {len(movimientos_incorrectos)} movimientos incorrectos:")
    for mov in movimientos_incorrectos:
        print(f"  - ID {mov[0]}: {mov[5]} en {mov[6]} - Cantidad: {mov[4]} - Fecha: {mov[1]}")
    
    respuesta = input("\n¿Deseas corregir estos movimientos? (s/n): ")
    if respuesta.lower() != 's':
        print("❌ Operación cancelada")
        conn.close()
        return
    
    # Para cada movimiento incorrecto, corregir el stock
    for mov in movimientos_incorrectos:
        mov_id, fecha, producto_id, deposito_id, cantidad, producto_nombre, deposito_nombre = mov
        
        print(f"\n🔧 Corrigiendo movimiento ID {mov_id} - {producto_nombre} en {deposito_nombre}")
        
        # Restar la cantidad que se sumó incorrectamente
        cursor.execute("""
            UPDATE stock 
            SET existencia = existencia - ?
            WHERE producto_id = ? AND deposito_id = ?
        """, (cantidad, producto_id, deposito_id))
        
        # Cambiar el tipo de movimiento de 'ajuste' a 'egreso' para reflejar la corrección
        cursor.execute("""
            UPDATE stock_movimientos 
            SET tipo = 'egreso', motivo = 'correccion_transferencia_erronea'
            WHERE id = ?
        """, (mov_id,))
        
        print(f"  ✅ Stock corregido: restadas {cantidad} unidades")
    
    # Ver el estado actual después de la corrección
    print("\n📊 Estado del stock después de la corrección:")
    cursor.execute("""
        SELECT p.nombre as producto, d.nombre as deposito, s.existencia
        FROM stock s
        JOIN productos p ON s.producto_id = p.id
        JOIN depositos d ON s.deposito_id = d.id
        WHERE p.nombre = 'PC PANEL TOUCH'
        ORDER BY d.nombre
    """)
    
    stocks = cursor.fetchall()
    for stock in stocks:
        print(f"  - {stock[0]} en {stock[1]}: {stock[2]} unidades")
    
    conn.commit()
    conn.close()
    print("\n✅ Corrección completada exitosamente")

if __name__ == "__main__":
    corregir_transferencias()