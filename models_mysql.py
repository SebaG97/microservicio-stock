from sqlalchemy import Column, Integer, String, DateTime, Text
from database import MySQLBase

class Measurement(MySQLBase):
    """
    Modelo para la tabla measurements existente en la base de datos MySQL parks_data.
    Estructura real de la tabla:
    - id: int(11) NOT NULL PRIMARY KEY
    - timestamp: datetime NOT NULL  
    - vessel_name: varchar(100) NOT NULL
    - variable_name: varchar(100) NOT NULL
    - value: varchar(100) NOT NULL
    - additional_data: varchar(10000) NULL
    - received_at: datetime NULL
    - original_timestamp: datetime NULL
    """
    __tablename__ = "measurements"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    vessel_name = Column(String(100), nullable=False, index=True)
    variable_name = Column(String(100), nullable=False, index=True)
    value = Column(String(100), nullable=False)
    additional_data = Column(String(10000), nullable=True)
    received_at = Column(DateTime, nullable=True)
    original_timestamp = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Measurement(vessel_name={self.vessel_name}, timestamp={self.timestamp}, variable={self.variable_name})>"