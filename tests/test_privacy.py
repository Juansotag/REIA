import pytest
from app.services.privacy_service import PrivacyService

class DummyEstudiante:
    def __init__(self, id, nombres, apellidos, genero="Masculino", pronombre="él", doc="1025847392"):
        self.id = id
        self.nombres = nombres
        self.apellidos = apellidos
        self.genero = genero
        self.pronombre = pronombre
        self.numero_documento = doc
        self.edad = 14
        self.grado_actual = 9

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

def test_deteccion_menciones_companeros():
    estudiantes = [
        DummyEstudiante(1, "Andrés Felipe", "Castro"),
        DummyEstudiante(2, "Mateo", "Gómez"),
        DummyEstudiante(3, "Sofía", "Ramírez")
    ]
    texto = "Durante el descanso se presentó una discusión acalorada con Andrés sobre el trabajo en equipo."
    menciones = PrivacyService.detectar_menciones(texto, estudiantes)
    
    assert len(menciones) >= 1
    assert menciones[0]["estudiante_id"] == 1
    assert menciones[0]["nombre_sugerido"] == "Andrés Felipe Castro"

def test_anonimizacion_zero_pii():
    estudiante = DummyEstudiante(1, "Sofía Valentina", "Ramírez Gutiérrez", genero="Femenino", pronombre="ella")
    texto = "Hoy Sofía Valentina demostró gran agilidad resolviendo problemas."
    
    texto_anon = PrivacyService.anonimizar_texto(texto, estudiante)
    assert "[ESTUDIANTE]" in texto_anon
    assert "Sofía" not in texto_anon
    assert "Ramírez" not in texto_anon

def test_reemplazo_local_tokens():
    estudiante = DummyEstudiante(1, "Juan David", "Morales Castro", genero="Masculino", pronombre="él")
    texto_ia = "Se recomienda que [NOMBRE_ESTUDIANTE] mantenga su dedicación ya que [PRONOMBRE] tiene gran potencial."
    
    texto_final = PrivacyService.reemplazar_tokens_locales(texto_ia, estudiante)
    assert "Juan David Morales Castro" in texto_final
    assert "[NOMBRE_ESTUDIANTE]" not in texto_final
    assert "él" in texto_final
    assert "[PRONOMBRE]" not in texto_final
