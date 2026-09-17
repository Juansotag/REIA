from pydantic import BaseModel
from typing import Optional, List

class EstudianteBase(BaseModel):
    nombres: str
    apellidos: str
    tipo_documento: str = "TI"
    numero_documento: str
    genero: str = "Masculino"
    pronombre: str = "él"
    edad: int
    grado_actual: int
    acudiente_nombre: Optional[str] = None
    acudiente_contacto: Optional[str] = None

class EstudianteCreate(EstudianteBase):
    curso_id: Optional[int] = None
    clases_ids: Optional[List[int]] = []

class EstudianteOut(EstudianteBase):
    id: int
    uuid_anonimo: str

    class Config:
        from_attributes = True
