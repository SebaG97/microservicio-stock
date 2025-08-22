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

class StockMovimientoCreate(StockMovimientoBase):
    pass

class StockMovimientoOut(StockMovimientoBase):
    id: int
    cliente_id: Optional[str] = None
    cliente_empresa: Optional[str] = None
    class Config:
        from_attributes = True

# --- Tecnico Schemas ---
class TecnicoBase(BaseModel):
    nombre: str
    apellido: str
    legajo: str
    activo: Optional[bool] = True

class TecnicoCreate(TecnicoBase):
    pass

class TecnicoOut(TecnicoBase):
    id: int
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
    tecnico_id: int
    cliente_id: Optional[str] = None
    cliente_empresa: Optional[str] = None
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    descripcion: Optional[str] = None
    estado: Optional[str] = "pendiente"

class ParteTrabajoCreate(ParteTrabajoBase):
    pass

class ParteTrabajoOut(ParteTrabajoBase):
    id: int
    tecnico: Optional[TecnicoOut] = None
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
