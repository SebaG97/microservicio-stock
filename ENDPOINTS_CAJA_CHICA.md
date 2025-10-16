# ENDPOINTS CORRECTOS PARA CAJA CHICA

## Resumen de Caja Chica
**GET** `/api/caja-chica/resumen`
- Retorna: información de la caja chica, gastos totales, gastos del mes, último gasto

## Gastos de Caja Chica  
**GET** `/api/caja-chica/gastos`
- Parámetros opcionales: `?limit=10&offset=0`
- Retorna: lista de gastos paginada

## Crear Gasto
**POST** `/api/caja-chica/gastos`
- Body: JSON con datos del gasto
```json
{
  "descripcion": "Compra de materiales",
  "proveedor_id": 1,
  "productos": [
    {
      "producto_id": 1,
      "cantidad": 2,
      "precio_unitario": 100.50
    }
  ]
}
```

## Ajustar Saldo
**POST** `/api/caja-chica/ajustar-saldo`
- Body: JSON con nuevo saldo
```json
{
  "nuevo_saldo": 5000.00,
  "descripcion": "Recarga de caja chica"
}
```

## Proveedores
**GET** `/api/proveedores`
- Retorna: lista de todos los proveedores

**POST** `/api/proveedores`
- Body: JSON con datos del proveedor
```json
{
  "nombre": "Proveedor Test",
  "ruc": "12345678901"
}
```

## Productos  
**GET** `/api/productos`
- Retorna: lista de todos los productos

---

## ERRORES ACTUALES EN TU FRONTEND:

❌ **INCORRECTO:** `GET /api/gastos/?limit=5`
✅ **CORRECTO:** `GET /api/caja-chica/gastos?limit=5`

❌ **INCORRECTO:** Acceder a `promedio_mensual` directamente
✅ **CORRECTO:** El endpoint `/api/caja-chica/resumen` retorna:
```json
{
  "gastos_del_mes": 0.0,  // <- Usa esta propiedad
  "gastos_totales": 0.0,
  "ultimo_gasto": null,
  "caja_chica": {...}
}
```