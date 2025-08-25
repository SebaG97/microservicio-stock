# 📋 API Endpoints para Órdenes de Trabajo (Partes)

## Base URL
```
http://localhost:8000/api
```

## 🔗 Endpoints Disponibles

### 1. **Listar todas las órdenes de trabajo**
```
GET /api/partes-trabajo/
```

**Parámetros de consulta opcionales:**
- `skip`: Número de registros a omitir (paginación) - Default: 0
- `limit`: Máximo de registros a retornar (1-1000) - Default: 100
- `estado`: Filtrar por estado (`pendiente`, `en_proceso`, `finalizado`)
- `tecnico_id`: Filtrar por ID del técnico
- `cliente_empresa`: Filtrar por nombre de empresa cliente (búsqueda parcial)
- `fecha_desde`: Fecha inicio del rango (formato: YYYY-MM-DD)
- `fecha_hasta`: Fecha fin del rango (formato: YYYY-MM-DD)

**Ejemplo:**
```
GET /api/partes-trabajo/?estado=finalizado&limit=50&skip=0
GET /api/partes-trabajo/?tecnico_id=5&fecha_desde=2025-01-01&fecha_hasta=2025-01-31
```

### 2. **Obtener una orden específica**
```
GET /api/partes-trabajo/{id}
```

**Ejemplo:**
```
GET /api/partes-trabajo/123
```

### 3. **Crear nueva orden de trabajo**
```
POST /api/partes-trabajo/
Content-Type: application/json

{
  "id_parte_api": "PART12345",
  "tecnico_id": 1,
  "cliente_id": "CLI001",
  "cliente_empresa": "Empresa ABC",
  "fecha_inicio": "2025-08-22T08:00:00",
  "fecha_fin": "2025-08-22T17:00:00",
  "descripcion": "Instalación de equipo",
  "estado": "pendiente"
}
```

### 4. **Actualizar orden de trabajo**
```
PUT /api/partes-trabajo/{id}
Content-Type: application/json

{
  "id_parte_api": "PART12345",
  "tecnico_id": 1,
  "cliente_id": "CLI001",
  "cliente_empresa": "Empresa ABC",
  "fecha_inicio": "2025-08-22T08:00:00",
  "fecha_fin": "2025-08-22T17:00:00",
  "descripcion": "Instalación de equipo actualizada",
  "estado": "finalizado"
}
```

### 5. **Eliminar orden de trabajo**
```
DELETE /api/partes-trabajo/{id}
```

### 6. **Estadísticas y resumen**
```
GET /api/partes-trabajo/stats/resumen
```

**Respuesta:**
```json
{
  "totales": {
    "total": 96,
    "pendientes": 5,
    "en_proceso": 10,
    "finalizados": 81
  },
  "por_tecnico": [
    {
      "tecnico": "Juan Pérez",
      "total_partes": 15
    }
  ]
}
```

### 7. **Búsqueda avanzada**
```
GET /api/partes-trabajo/buscar/?q=termino_busqueda
```

Busca en: ID parte, empresa cliente, ID cliente, descripción, nombre del técnico.

### 8. **Cambiar estado de una orden**
```
PATCH /api/partes-trabajo/{id}/estado?nuevo_estado=finalizado
```

Estados válidos: `pendiente`, `en_proceso`, `finalizado`

---

## 🧑‍💻 Endpoints de Técnicos (ya existentes)

### Listar técnicos
```
GET /api/horas-extras/tecnicos/
```

---

## 📊 Estructura de Datos

### Objeto ParteTrabajo
```json
{
  "id": 1,
  "id_parte_api": "PART12345",
  "tecnico_id": 1,
  "cliente_id": "CLI001",
  "cliente_empresa": "Empresa ABC S.A.",
  "fecha_inicio": "2025-08-22T08:00:00",
  "fecha_fin": "2025-08-22T17:00:00",
  "descripcion": "Instalación y configuración de equipo",
  "estado": "finalizado",
  "tecnico": {
    "id": 1,
    "nombre": "Juan",
    "apellido": "Pérez",
    "legajo": "T001",
    "activo": true
  }
}
```

### Estados disponibles
- `pendiente`: Orden creada pero no iniciada
- `en_proceso`: Orden en ejecución
- `finalizado`: Orden completada

---

## 🚀 Para usar en tu Frontend

### JavaScript/TypeScript ejemplo:

```javascript
// Obtener todas las órdenes
const response = await fetch('http://localhost:8000/api/partes-trabajo/');
const ordenes = await response.json();

// Obtener órdenes filtradas
const responseFiltered = await fetch(
  'http://localhost:8000/api/partes-trabajo/?estado=finalizado&limit=50'
);
const ordenesFinalizadas = await responseFiltered.json();

// Obtener estadísticas
const statsResponse = await fetch('http://localhost:8000/api/partes-trabajo/stats/resumen');
const estadisticas = await statsResponse.json();

// Crear nueva orden
const nuevaOrden = {
  id_parte_api: "PART" + Date.now(),
  tecnico_id: 1,
  cliente_empresa: "Nueva Empresa",
  fecha_inicio: new Date().toISOString(),
  descripcion: "Nueva orden de trabajo",
  estado: "pendiente"
};

const createResponse = await fetch('http://localhost:8000/api/partes-trabajo/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(nuevaOrden)
});
```

---

## 📝 Notas Importantes

1. **CORS habilitado**: El backend acepta peticiones desde cualquier origen
2. **Paginación**: Usa `skip` y `limit` para manejar grandes cantidades de datos
3. **Filtros**: Combina múltiples filtros para búsquedas específicas
4. **Validación**: Los campos obligatorios son validados automáticamente
5. **Relaciones**: Las respuestas incluyen información del técnico asignado
6. **Fechas**: Usa formato ISO 8601 (YYYY-MM-DDTHH:mm:ss)

## 🔍 Documentación Interactiva

Accede a la documentación completa con ejemplos en:
```
http://localhost:8000/docs
```
