from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

class Rubrica(Base):
    __tablename__ = "rubricas"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    clase_id = Column(Integer, ForeignKey("clases.id", ondelete="SET NULL"), nullable=True)
    escala_min = Column(Numeric(3, 1), default=0.0, nullable=False)
    escala_max = Column(Numeric(3, 1), default=5.0, nullable=False)
    tipo_escala = Column(String(20), default="CONTINUA", nullable=False) # 'CONTINUA' o 'DISCRETA'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    clase = relationship("Clase", back_populates="rubricas")
    dimensiones = relationship("DimensionRubrica", back_populates="rubrica", cascade="all, delete-orphan")
    reportes = relationship("Reporte", back_populates="rubrica")

class DimensionRubrica(Base):
    __tablename__ = "dimensiones_rubrica"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rubrica_id = Column(Integer, ForeignKey("rubricas.id", ondelete="CASCADE"), nullable=False)
    clave = Column(String(50), nullable=False)   # ej. 'dim_1_logica'
    nombre = Column(String(150), nullable=False) # ej. 'Pensamiento Lógico y Estructurado'
    descripcion = Column(Text, nullable=True)
    peso_porcentual = Column(Numeric(5, 2), default=0.0)
    descriptor_bajo = Column(Text, nullable=True)      # 0.0 - 2.9
    descriptor_basico = Column(Text, nullable=True)    # 3.0 - 3.9
    descriptor_alto = Column(Text, nullable=True)      # 4.0 - 4.5
    descriptor_superior = Column(Text, nullable=True)  # 4.6 - 5.0

    # Relaciones
    rubrica = relationship("Rubrica", back_populates="dimensiones")
