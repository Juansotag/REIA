from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, func, JSON
from app.database import Base

class ModeloInforme(Base):
    __tablename__ = "modelos_informe"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo_informe = Column(String(20), nullable=False) # 'INDIVIDUAL' o 'AGREGADO'
    prompt_base = Column(Text, nullable=False)
    filtros_predeterminados = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class InformeGenerado(Base):
    __tablename__ = "informes_generados"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    modelo_informe_id = Column(Integer, ForeignKey("modelos_informe.id", ondelete="SET NULL"), nullable=True)
    tipo_informe = Column(String(20), nullable=False) # 'INDIVIDUAL' o 'AGREGADO'
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=True)
    curso_id = Column(Integer, ForeignKey("cursos.id", ondelete="CASCADE"), nullable=True)
    clase_id = Column(Integer, ForeignKey("clases.id", ondelete="CASCADE"), nullable=True)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    prompt_utilizado = Column(Text, nullable=True)
    contenido_narrativo = Column(Text, nullable=False)
    datos_grafica = Column(JSON, default=dict)
    archivo_docx_path = Column(String(255), nullable=True)
    archivo_pdf_path = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
