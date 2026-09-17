from app.models.curso_clase import Curso, Clase, matriculas_curso, matriculas_clase, clases_curso
from app.models.estudiante import Estudiante
from app.models.rubrica import Rubrica, DimensionRubrica
from app.models.reporte import Reporte
from app.models.modelo_informe import ModeloInforme, InformeGenerado

__all__ = [
    "Curso",
    "Clase",
    "matriculas_curso",
    "matriculas_clase",
    "clases_curso",
    "Estudiante",
    "Rubrica",
    "DimensionRubrica",
    "Reporte",
    "ModeloInforme",
    "InformeGenerado"
]
