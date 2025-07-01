from pydantic import BaseModel
from typing import Optional

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
        orm_mode = True


# --- Marca Schemas ---
class MarcaBase(BaseModel):
    nombre: str

class MarcaCreate(MarcaBase):
    pass

class MarcaOut(MarcaBase):
    id: int
    class Config:
        orm_mode = True


# --- TipoProducto Schemas ---
class TipoProductoBase(BaseModel):
    nombre: str

class TipoProductoCreate(TipoProductoBase):
    pass

class TipoProductoOut(TipoProductoBase):
    id: int
    class Config:
        orm_mode = True


# --- Proveedor Schemas ---
class ProveedorBase(BaseModel):
    nombre: str

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorOut(ProveedorBase):
    id: int
    class Config:
        orm_mode = True


# --- ProductoLinea Schemas ---
class ProductoLineaBase(BaseModel):
    nombre: str

class ProductoLineaCreate(ProductoLineaBase):
    pass

class ProductoLineaOut(ProductoLineaBase):
    id: int
    class Config:
        orm_mode = True


# --- Procedencia Schemas ---
class ProcedenciaBase(BaseModel):
    nombre: str

class ProcedenciaCreate(ProcedenciaBase):
    pass

class ProcedenciaOut(ProcedenciaBase):
    id: int
    class Config:
        orm_mode = True

# --- Estado Schemas ---
class EstadoBase(BaseModel):
    nombre: str

class EstadoCreate(EstadoBase):
    pass

class EstadoOut(EstadoBase):
    id: int
    class Config:
        orm_mode = True

# --- Deposito Schemas ---
class DepositoBase(BaseModel):
    nombre: str

class DepositoCreate(DepositoBase):
    pass

class DepositoOut(DepositoBase):
    id: int
    class Config:
        orm_mode = True


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
        orm_mode = True
