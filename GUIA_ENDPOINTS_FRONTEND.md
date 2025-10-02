# 📋 GUÍA COMPLETA DE ENDPOINTS - SISTEMA DE HORAS EXTRAS

## 🌐 Servidor
- **URL Base:** `http://localhost:8000` o `http://192.168.100.204:8000`
- **Estado:** ✅ OPERATIVO
- **Documentación:** http://localhost:8000/docs

## 👥 Técnicos Disponibles
Los IDs válidos de técnicos son del **11 al 20**:

| ID | Nombre            | Legajo                     | Partes | Horas Extras |
|----|-------------------|----------------------------|--------|--------------|
| 11 | Edgar Ortega      | edgar.ortega              | 13     | 27           |
| 12 | Carmelo Orué      | carmelo.orue              | 0      | 25           |
| 13 | Luis González     | luis.gonzalez             | 36     | 51           |
| 14 | Alejandro Rojas   | alejandro.rojas           | 15     | 40           |
| 15 | Raul González     | raul.gonzalez             | 18     | 34           |
| 16 | Javier Brítez     | javier.britez             | 0      | 12           |
| 17 | Parks Admin       | operaciones               | 14     | 14           |
| 18 | Federico López    | federico.lopez            | 0      | 1            |
| 19 | Sebastian Giret   | sebastian.giret           | 0      | 1            |
| 20 | Vicente De Moura  | vicente.demoura           | 0      | 1            |

## 🔗 Endpoints Disponibles

### 1. **Obtener todos los técnicos**
```
GET /api/horas-extras/tecnicos/
```
**Ejemplo:** http://localhost:8000/api/horas-extras/tecnicos/

### 2. **Obtener reporte de horas extras**
```
GET /api/horas-extras/reporte/?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD
```
**Ejemplo:** http://localhost:8000/api/horas-extras/reporte/?fecha_inicio=2025-07-21&fecha_fin=2025-08-20

### 3. **Obtener partes con horas extras de un técnico** (El que estaba fallando)
```
GET /api/horas-extras/partes/{tecnico_id}/?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD
```
**Ejemplo:** http://localhost:8000/api/horas-extras/partes/11/?fecha_inicio=2025-07-21&fecha_fin=2025-08-20

### 4. **Obtener detalle de horas extras de un técnico**
```
GET /api/horas-extras/detalle/{tecnico_id}?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD
```
**Ejemplo:** http://localhost:8000/api/horas-extras/detalle/11?fecha_inicio=2025-07-21&fecha_fin=2025-08-20

### 5. **Sincronización manual**
```
POST /api/horas-extras/sincronizar-partes-mejorado/
```

## ⚠️ Solución al Error 404

### **El Problema:**
El frontend estaba recibiendo 404 para:
```
GET http://192.168.100.204:5173/api/horas-extras/partes/11/?fecha_inicio=2025-07-21&fecha_fin=2025-08-20
```

### **La Causa:**
- URL incorrecta: `http://192.168.100.204:5173` (puerto del frontend)
- Debería ser: `http://192.168.100.204:8000` (puerto del backend)

### **La Solución:**
✅ **Cambiar la configuración del frontend para apuntar al puerto 8000**

```typescript
// ❌ INCORRECTO:
const API_URL = 'http://192.168.100.204:5173/api';

// ✅ CORRECTO:
const API_URL = 'http://192.168.100.204:8000/api';
```

## 📊 Respuestas de Ejemplo

### Endpoint /partes/11/:
```json
[
  {
    "id": 123,
    "id_parte_api": "15F08C4ABA26",
    "fecha": "2025-08-20",
    "hora_inicio": "14:30",
    "hora_fin": "17:30", 
    "descripcion": "Trabajo de mantenimiento",
    "cliente_empresa": "Empresa XYZ",
    "horas_normales": 2.5,
    "horas_extras_normales": 0.5,
    "horas_extras_especiales": 0,
    "tipo_dia": "laboral",
    "calculado_automaticamente": true
  }
]
```

## 🚀 Estado del Sistema
- ✅ **96 partes finalizados** procesados
- ✅ **10 técnicos** activos  
- ✅ **206 registros de horas extras** calculados
- ✅ **Sincronización automática** cada 5 minutos
- ✅ **Todos los endpoints** funcionando

## 🔧 Pruebas Rápidas
Para verificar que todo funciona:

1. **Técnicos:** http://localhost:8000/api/horas-extras/tecnicos/
2. **Reporte:** http://localhost:8000/api/horas-extras/reporte/?fecha_inicio=2025-07-01&fecha_fin=2025-08-31
3. **Partes de Edgar:** http://localhost:8000/api/horas-extras/partes/11/?fecha_inicio=2025-07-21&fecha_fin=2025-08-20
4. **Documentación:** http://localhost:8000/docs
