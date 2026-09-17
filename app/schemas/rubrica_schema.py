from pydantic import BaseModel
from typing import Optional, List

class DimensionCreate(BaseModel):
    clave: str
    nombre: str
    descripcion: Optional[str] = None
    peso_porcentual: float = 0.0
    descriptor_bajo: Optional[str] = None
    descriptor_basico: Optional[str] = None
    descriptor_alto: Optional[str] = None
    descriptor_superior: Optional[str] = None

class RubricaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    clase_id: Optional[int] = None
    escala_min: float = 0.0
    escala_max: float = 5.0
    tipo_escala: str = "CONTINUA"
    dimensiones: List[DimensionCreate] = []
