from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, Text, Time, Table
from sqlalchemy.orm import relationship
from database import Base
import enum
from sqlalchemy import DateTime, Enum
from datetime import datetime

class Rubro(Base):
    __tablename__ = "rubros"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)

class Marca(Base):
    __tablename__ = "marcas"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)

class TipoProducto(Base):
    __tablename__ = "tipos_producto"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)

class Proveedor(Base):
    __tablename__ = "proveedores"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)

class ProductoLinea(Base):
    __tablename__ = "producto_lineas"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)

class Procedencia(Base):
    __tablename__ = "procedencias"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)

class Estado(Base):
    __tablename__ = "estados"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)

class Deposito(Base):
    __tablename__ = "depositos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True)
    id_producto = Column(String, unique=True)
    descripcion = Column(String, nullable=False)
    codigo = Column(String, unique=True)  # Renombrado de codigo_barra a codigo
    rubro_id = Column(Integer, ForeignKey("rubros.id"))
    marca_id = Column(Integer, ForeignKey("marcas.id"))
    tipo_producto_id = Column(Integer, ForeignKey("tipos_producto.id"))
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"))
    linea_id = Column(Integer, ForeignKey("producto_lineas.id"))
    procedencia_id = Column(Integer, ForeignKey("procedencias.id"))
    ingreso = Column(Date)
    foto = Column(String)
    estado_id = Column(Integer, ForeignKey("estados.id"))
    # Relaciones
    rubro = relationship("Rubro")
    marca = relationship("Marca")
    tipo_producto = relationship("TipoProducto")
    proveedor = relationship("Proveedor")
    linea = relationship("ProductoLinea")
    procedencia = relationship("Procedencia")
    estado = relationship("Estado")

class Stock(Base):
    __tablename__ = "stock"
    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id"))
    deposito_id = Column(Integer, ForeignKey("depositos.id"))
    existencia = Column(Float, default=0)
    stock_minimo = Column(Float, default=0)
    producto = relationship("Producto")
    deposito = relationship("Deposito")

class MovimientoTipo(enum.Enum):
    ingreso = "ingreso"
    egreso = "egreso"
    ajuste = "ajuste"

class StockMovimiento(Base):
    __tablename__ = "stock_movimientos"
    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey("productos.id"))
    deposito_id = Column(Integer, ForeignKey("depositos.id"))
    cantidad = Column(Float, nullable=False)
    tipo = Column(Enum(MovimientoTipo), nullable=False)
    motivo = Column(String)
    fecha = Column(DateTime, default=datetime.utcnow)
    cliente_id = Column(String, nullable=True)
    cliente_empresa = Column(String, nullable=True)

    producto = relationship("Producto")
    deposito = relationship("Deposito")

# Nuevos modelos para sistema de horas extras
class Tecnico(Base):
    __tablename__ = "tecnicos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    legajo = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)  # Para el user del JSON
    tipocuenta = Column(Integer, nullable=True)  # Para el tipocuenta del JSON
    activo = Column(Boolean, default=True)

class Feriado(Base):
    __tablename__ = "feriados"
    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False)
    nombre = Column(String, nullable=False)

# Tabla de asociación para la relación muchos a muchos entre ParteTrabajo y Tecnico
parte_trabajo_tecnicos = Table(
    'parte_trabajo_tecnicos',
    Base.metadata,
    Column('parte_trabajo_id', Integer, ForeignKey('partes_trabajo.id'), primary_key=True),
    Column('tecnico_id', Integer, ForeignKey('tecnicos.id'), primary_key=True)
)

class ParteTrabajo(Base):
    __tablename__ = "partes_trabajo"
    id = Column(Integer, primary_key=True)
    id_parte_api = Column(String, unique=True, nullable=False)  # ID de la API externa (ej: "CC395D5D5F2")
    numero = Column(Integer, nullable=True)  # Número del parte de trabajo (ej: 113)
    ejercicio = Column(String, nullable=True)  # Año del ejercicio (ej: "2025")
    fecha = Column(DateTime, nullable=False)  # Fecha del parte
    hora_inicio = Column(DateTime, nullable=True)  # horaIni del JSON
    hora_fin = Column(DateTime, nullable=True)  # horaFin del JSON
    kilometraje = Column(Float, nullable=True)
    trabajo_solicitado = Column(Text, nullable=True)  # trabajoSolicitado del JSON
    notas = Column(Text, nullable=True)
    notas_internas = Column(Text, nullable=True)  # notasInternas del JSON
    notas_internas_administracion = Column(Text, nullable=True)  # notasInternasAdministracion del JSON
    estado = Column(Integer, nullable=True)  # Estado numérico del JSON
    dni_firma = Column(String, nullable=True)  # dniFirma del JSON
    persona_firmante = Column(String, nullable=True)  # personaFirmante del JSON
    firmado = Column(Boolean, default=False)  # firmado del JSON
    archivado = Column(Boolean, default=False)  # archivado del JSON
    
    # Datos del cliente
    cliente_codigo_interno = Column(String, nullable=True)  # cliente_codigoInterno del JSON
    cliente_id = Column(String, nullable=True)  # cliente_id del JSON
    cliente_empresa = Column(String, nullable=True)  # cliente_empresa del JSON
    cliente_cif = Column(String, nullable=True)
    cliente_direccion = Column(String, nullable=True)
    cliente_provincia = Column(String, nullable=True)
    cliente_localidad = Column(String, nullable=True)
    cliente_pais = Column(String, nullable=True)
    cliente_telefono = Column(String, nullable=True)
    cliente_email = Column(String, nullable=True)
    cliente_erp_id = Column(String, nullable=True)
    
    proyecto_id = Column(String, nullable=True)  # proyecto_id del JSON
    erp_id = Column(String, nullable=True)  # erp_id del JSON
    
    # Relación muchos a muchos con tecnicos
    tecnicos = relationship("Tecnico", secondary=parte_trabajo_tecnicos, back_populates="partes_trabajo")

# Agregar la relación inversa en Tecnico
Tecnico.partes_trabajo = relationship("ParteTrabajo", secondary=parte_trabajo_tecnicos, back_populates="tecnicos")

class HorasExtrasTipo(enum.Enum):
    normal = "normal"
    especial = "especial"  # dobles

class HorasExtras(Base):
    __tablename__ = "horas_extras"
    id = Column(Integer, primary_key=True)
    parte_trabajo_id = Column(Integer, ForeignKey("partes_trabajo.id"))
    tecnico_id = Column(Integer, ForeignKey("tecnicos.id"))
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    horas_normales = Column(Float, default=0)
    horas_extras_normales = Column(Float, default=0)
    horas_extras_especiales = Column(Float, default=0)
    tipo_dia = Column(String, nullable=False)  # laboral, sabado, domingo, feriado
    calculado_automaticamente = Column(Boolean, default=True)
    
    parte_trabajo = relationship("ParteTrabajo")
    tecnico = relationship("Tecnico")
