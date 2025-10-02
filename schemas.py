from pydantic import BaseModel
from typing import Optional, List

class StockBase(BaseModel):
    producto_id: int
    deposito_id: int
    existencia: float
    stock_minimo: float

class StockCreate(StockBase):
    pass

class StockUpdate(BaseModel):
    existencia: Optional[float] = None
    stock_minimo: Optional[float] = None

class StockOut(StockBase):
    id: int
    class Config:
        from_attributes = True


# --- Marca Schemas ---
class MarcaBase(BaseModel):
    nombre: str

class MarcaCreate(MarcaBase):
    pass

class MarcaOut(MarcaBase):
    id: int
    class Config:
        from_attributes = True


# --- TipoProducto Schemas ---
class TipoProductoBase(BaseModel):
    nombre: str

class TipoProductoCreate(TipoProductoBase):
    pass

class TipoProductoOut(TipoProductoBase):
    id: int
    class Config:
        from_attributes = True


# --- Proveedor Schemas ---
class ProveedorBase(BaseModel):
    nombre: str

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorOut(ProveedorBase):
    id: int
    class Config:
        from_attributes = True


# --- ProductoLinea Schemas ---
class ProductoLineaBase(BaseModel):
    nombre: str

class ProductoLineaCreate(ProductoLineaBase):
    pass

class ProductoLineaOut(ProductoLineaBase):
    id: int
    class Config:
        from_attributes = True


# --- Procedencia Schemas ---
class ProcedenciaBase(BaseModel):
    nombre: str

class ProcedenciaCreate(ProcedenciaBase):
    pass

class ProcedenciaOut(ProcedenciaBase):
    id: int
    class Config:
        from_attributes = True

# --- Estado Schemas ---
class EstadoBase(BaseModel):
    nombre: str

class EstadoCreate(EstadoBase):
    pass

class EstadoOut(EstadoBase):
    id: int
    class Config:
        from_attributes = True

# --- Deposito Schemas ---
class DepositoBase(BaseModel):
    nombre: str

class DepositoCreate(DepositoBase):
    pass

class DepositoOut(DepositoBase):
    id: int
    class Config:
        from_attributes = True


# --- Producto Schemas ---
from typing import Optional

# --- Rubro Schemas ---
class RubroBase(BaseModel):
    nombre: str

class RubroCreate(RubroBase):
    pass

class RubroUpdate(BaseModel):
    nombre: Optional[str] = None

class RubroRead(RubroBase):
    id: int
    class Config:
        from_attributes = True

class ProductoBase(BaseModel):
    id_producto: Optional[str] = None
    descripcion: str
    codigo: Optional[str] = None
    rubro_id: Optional[int] = None
    marca_id: Optional[int] = None
    tipo_producto_id: Optional[int] = None
    proveedor_id: Optional[int] = None
    linea_id: Optional[int] = None
    procedencia_id: Optional[int] = None
    ingreso: Optional[str] = None
    foto: Optional[str] = None
    estado_id: Optional[int] = None

class ProductoCreate(ProductoBase):
    pass

class ProductoOut(ProductoBase):
    id: int
    class Config:
        from_attributes = True

class ProductoParteTrabajoOut(BaseModel):
    """Schema para productos utilizados en una orden de trabajo"""
    producto: ProductoOut
    cantidad_total: float
    movimientos: List[dict]
    
    class Config:
        from_attributes = True


# --- StockMovimiento Schemas ---
from enum import Enum
from datetime import datetime

class MovimientoTipo(str, Enum):
    ingreso = "ingreso"
    egreso = "egreso"
    ajuste = "ajuste"

class StockMovimientoBase(BaseModel):
    producto_id: int
    deposito_id: int
    cantidad: float
    tipo: MovimientoTipo
    motivo: str
    fecha: Optional[datetime] = None
    cliente_id: Optional[str] = None
    cliente_empresa: Optional[str] = None
    parte_trabajo_id: Optional[int] = None

class StockMovimientoCreate(StockMovimientoBase):
    pass

class StockMovimientoOut(StockMovimientoBase):
    id: int
    cliente_id: Optional[str] = None
    cliente_empresa: Optional[str] = None
    class Config:
        from_attributes = True

# --- Transferencia Schemas ---
class TransferenciaStock(BaseModel):
    producto_id: int
    deposito_origen_id: int
    deposito_destino_id: int
    cantidad: float
    motivo: Optional[str] = "transferencia_deposito"

class TransferenciaResponse(BaseModel):
    mensaje: str
    producto_id: int
    deposito_origen_id: int
    deposito_destino_id: int
    cantidad: float
    stock_origen_actual: float
    stock_destino_actual: float

# --- Tecnico Schemas ---
class TecnicoBase(BaseModel):
    nombre: str
    apellido: str
    legajo: str
    email: Optional[str] = None
    tipocuenta: Optional[int] = None
    activo: Optional[bool] = True

class TecnicoCreate(TecnicoBase):
    pass

class TecnicoOut(TecnicoBase):
    id: int
    class Config:
        from_attributes = True

class TecnicoSimple(BaseModel):
    """Schema simplificado para técnicos en respuestas de partes de trabajo"""
    user: Optional[str] = None  # email del técnico
    nombre: str
    tipocuenta: Optional[int] = None
    
    class Config:
        from_attributes = True

# --- Feriado Schemas ---
from datetime import date, time

class FeriadoBase(BaseModel):
    fecha: date
    nombre: str

class FeriadoCreate(FeriadoBase):
    pass

class FeriadoOut(FeriadoBase):
    id: int
    class Config:
        from_attributes = True

# --- ParteTrabajo Schemas ---
class ParteTrabajoBase(BaseModel):
    id_parte_api: str
    numero: Optional[int] = None
    ejercicio: Optional[str] = None
    fecha: datetime
    hora_inicio: Optional[datetime] = None  # horaIni
    hora_fin: Optional[datetime] = None     # horaFin
    kilometraje: Optional[float] = None
    trabajo_solicitado: Optional[str] = None
    notas: Optional[str] = None
    notas_internas: Optional[str] = None
    notas_internas_administracion: Optional[str] = None
    estado: Optional[int] = None
    dni_firma: Optional[str] = None
    persona_firmante: Optional[str] = None
    firmado: Optional[bool] = False
    archivado: Optional[bool] = False
    
    # Datos del cliente
    cliente_codigo_interno: Optional[str] = None
    cliente_id: Optional[str] = None
    cliente_empresa: Optional[str] = None
    cliente_cif: Optional[str] = None
    cliente_direccion: Optional[str] = None
    cliente_provincia: Optional[str] = None
    cliente_localidad: Optional[str] = None
    cliente_pais: Optional[str] = None
    cliente_telefono: Optional[str] = None
    cliente_email: Optional[str] = None
    cliente_erp_id: Optional[str] = None
    
    proyecto_id: Optional[str] = None
    erp_id: Optional[str] = None

class ParteTrabajoCreate(ParteTrabajoBase):
    tecnico_ids: Optional[List[int]] = []  # Lista de IDs de técnicos

class ParteTrabajoOut(ParteTrabajoBase):
    id: int
    tecnicos: List[TecnicoSimple] = []  # Lista de técnicos asignados
    class Config:
        from_attributes = True

class ParteTrabajoConProductosOut(ParteTrabajoOut):
    """Schema para listado de órdenes de trabajo con información de productos"""
    productos_utilizados: int = 0  # Número de productos diferentes utilizados
    productos_resumen: str = ""    # Resumen texto de los productos principales
    
    class Config:
        from_attributes = True

# --- HorasExtras Schemas ---
class HorasExtrasBase(BaseModel):
    parte_trabajo_id: int
    tecnico_id: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    horas_normales: Optional[float] = 0
    horas_extras_normales: Optional[float] = 0
    horas_extras_especiales: Optional[float] = 0
    tipo_dia: str
    calculado_automaticamente: Optional[bool] = True

class HorasExtrasCreate(HorasExtrasBase):
    pass

class HorasExtrasOut(HorasExtrasBase):
    id: int
    parte_trabajo: Optional[ParteTrabajoOut] = None
    tecnico: Optional[TecnicoOut] = None
    class Config:
        from_attributes = True

# --- Schemas para reportes ---
class HorasExtrasResumen(BaseModel):
    tecnico_id: int
    tecnico_nombre: str
    tecnico_apellido: str
    fecha_inicio: date
    fecha_fin: date
    total_horas_extras_normales: float
    total_horas_extras_especiales: float
    total_horas_trabajadas: float
    partes_trabajados: int

class HorasExtrasReporte(BaseModel):
    resumen: List[HorasExtrasResumen]
    periodo_inicio: date
    periodo_fin: date
    total_tecnicos: int

# --- Movimientos Múltiples Schemas ---
class ItemMovimiento(BaseModel):
    producto_id: int
    cantidad: float
    precio_unitario: Optional[float] = None
    observaciones: Optional[str] = None

class MovimientoMultiple(BaseModel):
    deposito_id: int
    tipo: MovimientoTipo  
    items: List[ItemMovimiento]
    motivo: str
    cliente_id: Optional[str] = None
    cliente_empresa: Optional[str] = None
    tecnico_id: Optional[int] = None
    parte_trabajo_id: Optional[str] = None

class ResultadoItemMovimiento(BaseModel):
    producto_id: int
    descripcion: str
    cantidad: float
    stock_anterior: float
    stock_actual: float
    exitoso: bool
    error: Optional[str] = None
    precio_unitario: Optional[float] = None

class MovimientoMultipleResponse(BaseModel):
    mensaje: str
    deposito_id: int
    tipo: str
    items_procesados: int
    items_exitosos: int
    items_fallidos: int
    total_valor: Optional[float] = None
    resultados: List[ResultadoItemMovimiento]

# --- Transferencia Múltiple Schemas ---
class ItemTransferencia(BaseModel):
    producto_id: int
    cantidad: float

class TransferenciaMultiple(BaseModel):
    deposito_origen_id: int
    deposito_destino_id: int
    items: List[ItemTransferencia]
    motivo: Optional[str] = "transferencia_multiple"

class ResultadoItemTransferencia(BaseModel):
    producto_id: int
    descripcion: str
    cantidad: float
    stock_origen_anterior: float
    stock_origen_actual: float
    stock_destino_anterior: float
    stock_destino_actual: float
    exitoso: bool
    error: Optional[str] = None

class TransferenciaMultipleResponse(BaseModel):
    mensaje: str
    deposito_origen_id: int
    deposito_destino_id: int
    items_procesados: int
    items_exitosos: int
    items_fallidos: int
    resultados: List[ResultadoItemTransferencia]


# --- Esquemas para Alarmas de Vessels ---
from datetime import datetime
from enum import Enum

class EstadoAlarma(str, Enum):
    """Enumeración para los estados de alarma según las horas sin datos"""
    VERDE = "verde"      # Datos recientes (menos de 2 horas)
    AMARILLO = "amarillo"  # 2-8 horas sin datos
    NARANJA = "naranja"   # 8-12 horas sin datos  
    ROJO = "rojo"        # Más de 12 horas sin datos

class AlarmaVessel(BaseModel):
    """Esquema para la respuesta de alarma de un vessel individual"""
    vessel_name: str
    ultimo_dato: datetime
    horas_sin_datos: float
    estado_alarma: EstadoAlarma
    mensaje: str

    class Config:
        from_attributes = True

class ListaAlarmas(BaseModel):
    """Esquema para la respuesta completa del listado de alarmas"""
    total_vessels: int
    alarmas: List[AlarmaVessel]
    resumen: dict  # Conteo por estado: {"verde": 5, "amarillo": 2, "naranja": 1, "rojo": 3}
