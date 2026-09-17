from pydantic import BaseModel
from typing import Optional, Dict, Any

class ReporteCreate(BaseModel):
    estudiante_id: int
    curso_id: int
    clase_id: int
    rubrica_id: Optional[int] = None
    texto_original: str
    calificaciones_dimensiones: Dict[str, float] = {}
    metadata_adicional: Optional[Dict[str, Any]] = {}
