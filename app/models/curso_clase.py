from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

# Tablas intermedias Many-to-Many
matriculas_curso = Table(
    "matriculas_curso",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("estudiante_id", Integer, ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False),
    Column("curso_id", Integer, ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False),
    Column("anio_lectivo", Integer, default=2026)
)

matriculas_clase = Table(
    "matriculas_clase",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("estudiante_id", Integer, ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False),
    Column("clase_id", Integer, ForeignKey("clases.id", ondelete="CASCADE"), nullable=False),
    Column("anio_lectivo", Integer, default=2026)
)

clases_curso = Table(
    "clases_curso",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("curso_id", Integer, ForeignKey("cursos.id", ondelete="CASCADE"), nullable=False),
    Column("clase_id", Integer, ForeignKey("clases.id", ondelete="CASCADE"), nullable=False),
    Column("docente_encargado", String(150), nullable=True)
)

class Curso(Base):
    __tablename__ = "cursos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(50), nullable=False) # ej. "Noveno B"
    grado = Column(Integer, nullable=False)     # 5 a 11
    seccion = Column(String(5), nullable=False) # 'A', 'B'
    anio_lectivo = Column(Integer, default=2026, nullable=False)
    director_curso = Column(String(150), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    estudiantes = relationship("Estudiante", secondary=matriculas_curso, back_populates="cursos")
    clases = relationship("Clase", secondary=clases_curso, back_populates="cursos")
    reportes = relationship("Reporte", back_populates="curso", cascade="all, delete-orphan")

class Clase(Base):
    __tablename__ = "clases"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False) # ej. "Matemáticas"
    area = Column(String(100), nullable=False)   # ej. "Ciencias Exactas"
    descripcion = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    estudiantes = relationship("Estudiante", secondary=matriculas_clase, back_populates="clases")
    cursos = relationship("Curso", secondary=clases_curso, back_populates="clases")
    reportes = relationship("Reporte", back_populates="clase", cascade="all, delete-orphan")
    rubricas = relationship("Rubrica", back_populates="clase")
