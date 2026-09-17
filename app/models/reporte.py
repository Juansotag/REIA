from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Reporte(Base):
    __tablename__ = "reportes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid_anonimo = Column(String(64), index=True, nullable=False)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False)
    curso_id = Column(Integer, ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False)
    clase_id = Column(Integer, ForeignKey("clases.id", ondelete="CASCADE"), nullable=False)
    rubrica_id = Column(Integer, ForeignKey("rubricas.id", ondelete="SET NULL"), nullable=True)
    fecha = Column(Date, default=func.current_date(), nullable=False)
    texto_original = Column(Text, nullable=False)
    texto_anonimizado = Column(Text, nullable=False)
    calificaciones_dimensiones = Column(JSON, default=dict, nullable=False) # {'dim_1': 4.5, ...}
    metadata_adicional = Column(JSON, default=dict, nullable=True)         # {'metodo': 'STT', ...}
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    estudiante = relationship("Estudiante", back_populates="reportes")
    curso = relationship("Curso", back_populates="reportes")
    clase = relationship("Clase", back_populates="reportes")
    rubrica = relationship("Rubrica", back_populates="reportes")
