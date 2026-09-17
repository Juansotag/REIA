from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.curso_clase import matriculas_curso, matriculas_clase

class Estudiante(Base):
    __tablename__ = "estudiantes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid_anonimo = Column(String(64), unique=True, index=True, nullable=False)
    tipo_documento = Column(String(10), default="TI", nullable=False)
    numero_documento = Column(String(30), unique=True, index=True, nullable=False)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    genero = Column(String(20), nullable=False)   # 'Masculino', 'Femenino', 'Otro'
    pronombre = Column(String(10), nullable=False) # 'él', 'ella', 'elle'
    fecha_nacimiento = Column(Date, nullable=True)
    edad = Column(Integer, nullable=False)
    grado_actual = Column(Integer, index=True, nullable=False) # 5 a 11
    acudiente_nombre = Column(String(150), nullable=True)
    acudiente_contacto = Column(String(100), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relaciones
    cursos = relationship("Curso", secondary=matriculas_curso, back_populates="estudiantes")
    clases = relationship("Clase", secondary=matriculas_clase, back_populates="estudiantes")
    reportes = relationship("Reporte", back_populates="estudiante", cascade="all, delete-orphan")

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}"
