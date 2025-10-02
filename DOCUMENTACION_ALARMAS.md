# 📊 API de Alarmas de Vessels - Documentación

## 🎯 Descripción General

Este sistema monitorea el estado de recepción de datos de los vessels (embarcaciones) conectados a la base de datos MySQL `parks_data`. Genera alarmas basadas en el tiempo transcurrido desde la última recepción de datos de cada vessel.

## ⚡ Estados de Alarma

| Estado | Color | Condición | Descripción |
|--------|-------|-----------|-------------|
| **Verde** | 🟢 | < 2 horas | Datos recientes - Operación normal |
| **Amarillo** | 🟡 | 2-8 horas | Sin datos nuevos - Advertencia |
| **Naranja** | 🟠 | 8-12 horas | Sin datos nuevos - Atención requerida |
| **Rojo** | 🔴 | > 12 horas | Sin datos nuevos - Estado CRÍTICO |

## 🌐 Endpoints Disponibles

### 1. **GET /api/alarmas**
Obtiene el estado completo de alarmas para todos los vessels.

**Respuesta:**
```json
{
  "total_vessels": 77,
  "alarmas": [
    {
      "vessel_name": "TIO KIKE",
      "ultimo_dato": "2024-10-02T00:00:18",
      "horas_sin_datos": 1.5,
      "estado_alarma": "verde",
      "mensaje": "Vessel TIO KIKE operando normalmente"
    }
  ],
  "resumen": {
    "verde": 60,
    "amarillo": 0,
    "naranja": 0,
    "rojo": 17
  }
}
```

### 2. **GET /api/alarmas/resumen**
Obtiene un resumen estadístico del estado de las alarmas.

**Respuesta:**
```json
{
  "total_vessels": 77,
  "conteo_por_estado": {
    "verde": 60,
    "amarillo": 0,
    "naranja": 0,
    "rojo": 17
  },
  "porcentajes": {
    "verde": 77.9,
    "amarillo": 0.0,
    "naranja": 0.0,
    "rojo": 22.1
  },
  "vessels_operativos": 60,
  "vessels_con_problemas": 17
}
```

### 3. **GET /api/alarmas/criticos**
Obtiene solo los vessels en estado crítico.

**Parámetros de consulta:**
- `horas` (opcional): Umbral de horas para considerar crítico (default: 12.0)

**Ejemplo:** `/api/alarmas/criticos?horas=24`

**Respuesta:**
```json
[
  {
    "vessel_name": "TEST_ADM",
    "ultimo_dato": "2025-03-25T20:57:00",
    "horas_sin_datos": 4573.16,
    "estado_alarma": "rojo",
    "mensaje": "Vessel TEST_ADM: 4573.2h sin datos - CRÍTICO"
  }
]
```

### 4. **GET /api/alarmas/vessel/{vessel_name}**
Obtiene el estado de alarma para un vessel específico.

**Parámetros de ruta:**
- `vessel_name`: Nombre del vessel (case-insensitive)

**Ejemplo:** `/api/alarmas/vessel/TIO KIKE`

**Respuesta:**
```json
{
  "vessel_name": "TIO KIKE",
  "ultimo_dato": "2024-10-02T00:00:18",
  "horas_sin_datos": 1.5,
  "estado_alarma": "verde",
  "mensaje": "Vessel TIO KIKE operando normalmente"
}
```

## 🗄️ Configuración de Base de Datos

### MySQL Connection
- **Host:** `db.parks.com.py:3306`
- **Database:** `parks_data`
- **Usuario:** `root`
- **Tabla principal:** `measurements`

### Estructura de la tabla `measurements`
```sql
CREATE TABLE measurements (
  id int(11) NOT NULL PRIMARY KEY,
  timestamp datetime NOT NULL,
  vessel_name varchar(100) NOT NULL,
  variable_name varchar(100) NOT NULL,
  value varchar(100) NOT NULL,
  additional_data varchar(10000) NULL,
  received_at datetime NULL,
  original_timestamp datetime NULL,
  KEY idx_timestamp (timestamp),
  KEY idx_vessel_name (vessel_name),
  KEY idx_variable_name (variable_name)
);
```

## 🚀 Uso desde Frontend

### Ejemplo con JavaScript/Fetch
```javascript
// Obtener resumen de alarmas
fetch('/api/alarmas/resumen')
  .then(response => response.json())
  .then(data => {
    console.log(`Vessels operativos: ${data.vessels_operativos}`);
    console.log(`Vessels con problemas: ${data.vessels_con_problemas}`);
  });

// Obtener vessels críticos
fetch('/api/alarmas/criticos?horas=12')
  .then(response => response.json())
  .then(vessels => {
    vessels.forEach(vessel => {
      console.log(`🚨 ${vessel.vessel_name}: ${vessel.horas_sin_datos}h sin datos`);
    });
  });
```

### Ejemplo con Angular/HTTP Client
```typescript
// En tu servicio Angular
getResumenAlarmas(): Observable<any> {
  return this.http.get('/api/alarmas/resumen');
}

getVesselsCriticos(horas: number = 12): Observable<any[]> {
  return this.http.get<any[]>(`/api/alarmas/criticos?horas=${horas}`);
}

// En tu componente
this.alarmasService.getResumenAlarmas().subscribe(resumen => {
  this.totalVessels = resumen.total_vessels;
  this.vesselsOperativos = resumen.vessels_operativos;
  this.vesselsConProblemas = resumen.vessels_con_problemas;
});
```

## 🔧 Archivos Implementados

```
📁 microservicio-stock/
├── database.py                 # Configuración conexión MySQL añadida
├── models_mysql.py            # Modelo SQLAlchemy para tabla measurements  
├── schemas.py                 # Esquemas Pydantic para responses (añadido al final)
├── routers/alarmas.py         # Endpoints REST de alarmas
├── servicios/alarmas_service.py # Lógica de negocio para cálculo de alarmas
├── main.py                    # Registro del router en FastAPI (modificado)
└── requirements.txt           # Dependencias MySQL añadidas (pymysql, cryptography)
```

## ✅ Estados del Sistema

**Actualmente funcionando:**
- ✅ Conexión MySQL a `parks_data` 
- ✅ Lectura de datos de tabla `measurements` existente
- ✅ Cálculo de alarmas por tiempo sin datos
- ✅ 4 endpoints REST completamente funcionales
- ✅ Sistema integrado con microservicio de stock existente
- ✅ 77 vessels monitoreados actualmente
- ✅ Datos de prueba: 137M+ registros en measurements

**Para el frontend:**
- Los endpoints están listos para consumir desde Angular u otro framework
- Respuestas en formato JSON estándar
- CORS habilitado para desarrollo
- Sistema de estados claro con colores (verde/amarillo/naranja/rojo)
- Incluye mensajes descriptivos para mostrar al usuario