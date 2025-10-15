# 📋 Módulo de Caja Chica - Documentación API

## Descripción General

El módulo de Caja Chica permite gestionar los gastos de una caja chica empresarial, incluyendo:
- ✅ Control de saldo y monto inicial
- ✅ Registro de gastos con facturación
- ✅ Gestión de proveedores con RUC
- ✅ Compras que se integran automáticamente al stock
- ✅ Movimientos de inventario automáticos
- ✅ Listados profesionales con filtros

## Modelos de Base de Datos

### 1. CajaChica
```sql
CREATE TABLE caja_chica (
    id SERIAL PRIMARY KEY,
    monto_inicial FLOAT NOT NULL,
    saldo_actual FLOAT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    activo BOOLEAN DEFAULT TRUE
);
```

### 2. GastoCajaChica  
```sql
CREATE TABLE gastos_caja_chica (
    id SERIAL PRIMARY KEY,
    caja_chica_id INTEGER REFERENCES caja_chica(id),
    proveedor_id INTEGER REFERENCES proveedores(id),
    proveedor_nombre VARCHAR, -- Para proveedores no registrados
    numero_factura VARCHAR NOT NULL, -- Formato: xxx-xxx-xxxxxxx
    fecha_factura DATE NOT NULL,
    monto_total FLOAT NOT NULL,
    descripcion TEXT,
    fecha_registro TIMESTAMP DEFAULT NOW()
);
```

### 3. GastoProducto
```sql
CREATE TABLE gastos_productos (
    id SERIAL PRIMARY KEY,
    gasto_id INTEGER REFERENCES gastos_caja_chica(id),
    producto_id INTEGER REFERENCES productos(id),
    deposito_id INTEGER REFERENCES depositos(id),
    cantidad FLOAT NOT NULL,
    precio_unitario FLOAT NOT NULL,
    subtotal FLOAT NOT NULL
);
```

### 4. Proveedor (Actualizado)
```sql
-- Campo agregado a tabla existente
ALTER TABLE proveedores ADD COLUMN ruc VARCHAR UNIQUE;
```

## Endpoints API

### 🏛️ Gestión de Caja Chica

#### POST `/api/caja-chica/`
**Crear nueva caja chica**
```json
{
    "monto_inicial": 50000.0
}
```
**Response:**
```json
{
    "id": 1,
    "monto_inicial": 50000.0,
    "saldo_actual": 50000.0,
    "fecha_creacion": "2024-01-15T10:30:00",
    "activo": true
}
```

#### GET `/api/caja-chica/actual`
**Obtener caja chica activa**

#### PUT `/api/caja-chica/{id}`
**Actualizar monto inicial**
```json
{
    "monto_inicial": 75000.0
}
```

#### GET `/api/caja-chica/resumen`
**Obtener resumen completo con estadísticas**
```json
{
    "caja_chica": {
        "id": 1,
        "monto_inicial": 50000.0,
        "saldo_actual": 42350.0,
        "fecha_creacion": "2024-01-15T10:30:00",
        "activo": true
    },
    "gastos_totales": 7650.0,
    "gastos_del_mes": 2300.0,
    "ultimo_gasto": {
        "id": 5,
        "numero_factura": "001-001-0000123",
        "monto_total": 850.0,
        "fecha_registro": "2024-01-20T14:15:00"
    }
}
```

### 💸 Gestión de Gastos

#### POST `/api/gastos/`
**Registrar nuevo gasto**

**Caso 1: Gasto con productos (ingresa al stock)**
```json
{
    "proveedor_id": 5,
    "numero_factura": "001-001-0000001",
    "fecha_factura": "2024-01-20",
    "descripcion": "Compra de materiales",
    "productos": [
        {
            "producto_id": 10,
            "deposito_id": 1,
            "cantidad": 5.0,
            "precio_unitario": 150.0
        },
        {
            "producto_id": 12,
            "deposito_id": 1,
            "cantidad": 2.0,
            "precio_unitario": 200.0
        }
    ]
}
```

**Caso 2: Gasto sin productos (servicios, combustible, etc.)**
```json
{
    "proveedor_nombre": "Combustibles El Rápido",
    "numero_factura": "002-001-0000001",
    "fecha_factura": "2024-01-20",
    "descripcion": "Combustible para vehículos",
    "productos": []
}
```

**Response:**
```json
{
    "id": 1,
    "caja_chica_id": 1,
    "proveedor_id": 5,
    "proveedor_nombre": null,
    "numero_factura": "001-001-0000001",
    "fecha_factura": "2024-01-20",
    "monto_total": 1150.0,
    "descripcion": "Compra de materiales",
    "fecha_registro": "2024-01-20T15:30:00",
    "proveedor": {
        "id": 5,
        "nombre": "Ferretería San José",
        "ruc": "80123456-7"
    },
    "productos": [
        {
            "id": 1,
            "producto_id": 10,
            "deposito_id": 1,
            "cantidad": 5.0,
            "precio_unitario": 150.0,
            "subtotal": 750.0
        }
    ]
}
```

#### GET `/api/gastos/`
**Listar gastos con filtros opcionales**

**Parámetros:**
- `skip`: Offset para paginación (default: 0)
- `limit`: Límite de resultados (default: 100)
- `mes`: Filtrar por mes (1-12)
- `año`: Filtrar por año (ej: 2024)

**Ejemplos:**
- `/api/gastos/` - Todos los gastos
- `/api/gastos/?mes=1&año=2024` - Gastos de enero 2024
- `/api/gastos/?skip=0&limit=10` - Primeros 10 gastos

#### GET `/api/gastos/{id}`
**Obtener gasto específico con detalles completos**

#### PUT `/api/gastos/{id}`
**Actualizar datos básicos del gasto**
```json
{
    "descripcion": "Descripción actualizada",
    "proveedor_nombre": "Nuevo nombre de proveedor"
}
```

#### DELETE `/api/gastos/{id}`
**Eliminar gasto y revertir movimientos de stock**
- ⚠️ **Importante**: Esta acción revierte automáticamente los ingresos de stock
- Se crean movimientos de corrección en el historial

### 🏢 Gestión de Proveedores

#### POST `/api/proveedores/`
**Crear proveedor rápido con RUC**
```json
{
    "nombre": "Ferretería San José",
    "ruc": "80123456-7"
}
```

**Response:**
```json
{
    "id": 1,
    "nombre": "Ferretería San José",
    "ruc": "80123456-7"
}
```

#### PUT `/api/proveedores/{id}`
**Actualizar proveedor existente**
```json
{
    "nombre": "Ferretería San José S.A.",
    "ruc": "80123456-7"
}
```

### 📦 Consultas Auxiliares

#### GET `/api/gastos/productos/{gasto_id}`
**Obtener productos de un gasto específico**

## Integración con Sistema de Stock

### ✅ Funcionamiento Automático

Cuando se registra un gasto con productos:

1. **Se actualiza el stock automáticamente:**
   - Si existe stock para producto + depósito → se suma la cantidad
   - Si no existe → se crea nuevo registro de stock

2. **Se genera movimiento de inventario:**
   ```json
   {
       "tipo": "ingreso",
       "motivo": "Compra por caja chica - Factura: 001-001-0000001",
       "cantidad": 5.0,
       "cliente_empresa": "Ferretería San José"
   }
   ```

3. **Se actualiza el saldo de caja chica:**
   - Saldo actual = Monto inicial - Total de gastos

### ⚠️ Consideraciones Importantes

- **Eliminación de gastos**: Revierte automáticamente el stock
- **Validaciones**: Verifica que productos y depósitos existan
- **Concurrencia**: Las operaciones son transaccionales
- **Historial**: Todos los movimientos quedan registrados

## Casos de Uso

### 1. 🛒 Compra de Inventario
```bash
# Registrar compra que ingresa al stock
POST /api/gastos/
{
    "proveedor_id": 5,
    "numero_factura": "001-001-0000123",
    "fecha_factura": "2024-01-20", 
    "productos": [
        {
            "producto_id": 15,
            "deposito_id": 1,
            "cantidad": 10,
            "precio_unitario": 250.0
        }
    ]
}

# Resultado: Stock actualizado + Movimiento registrado + Saldo reducido
```

### 2. 💵 Gasto de Servicios
```bash
# Registrar gasto que no afecta stock
POST /api/gastos/
{
    "proveedor_nombre": "Servicios de Limpieza ABC",
    "numero_factura": "003-002-0000456",
    "fecha_factura": "2024-01-20",
    "descripcion": "Servicio de limpieza mensual",
    "productos": []
}

# Resultado: Solo saldo reducido, sin afectar stock
```

### 3. 📊 Consulta de Estado
```bash
# Obtener resumen completo
GET /api/caja-chica/resumen

# Ver gastos del mes actual
GET /api/gastos/?mes=1&año=2024

# Historial completo
GET /api/gastos/
```

## Estados de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| 404 | Caja chica no encontrada | Crear caja chica primero |
| 404 | Producto/Depósito no existe | Verificar IDs válidos |
| 400 | RUC duplicado | Usar RUC único |
| 400 | Número de factura duplicado | Verificar numeración |

## Próximas Mejoras Sugeridas

- [ ] **Reportes PDF**: Generar reportes mensuales en PDF
- [ ] **Categorías de gastos**: Clasificar gastos por tipo
- [ ] **Aprobaciones**: Workflow de aprobación para gastos grandes
- [ ] **Fotos de facturas**: Adjuntar imágenes de comprobantes
- [ ] **Múltiples cajas chicas**: Manejar diferentes cajas por departamento
- [ ] **Notificaciones**: Alertas cuando el saldo sea bajo
- [ ] **Integración contable**: Export a sistemas contables