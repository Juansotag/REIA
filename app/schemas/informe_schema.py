from pydantic import BaseModel
from typing import Optional, List

class InformeRequest(BaseModel):
    tipo_informe: str # 'INDIVIDUAL' o 'AGREGADO'
    estudiante_id: Optional[int] = None
    curso_id: Optional[int] = None
    clase_id: Optional[int] = None
    rubrica_id: Optional[int] = None
    fecha_inicio: str
    fecha_fin: str
    prompt_personalizado: Optional[str] = ""
