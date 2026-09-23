"""
Servicio Factory de Inteligencia Artificial para REIA.
GovLab: Universidad de la Sabana.
Soporte dual e intercambiable en caliente para OpenAI (GPT-4o / GPT-4o-mini)
y Anthropic (Claude 3.5 Sonnet / Claude 3.5 Haiku), con modo de simulación inteligente offline.
"""

import os
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseLLMService(ABC):

    @abstractmethod
    def inferir_rubrica(self, comentario_anonimo: str, rubrica_data: Dict[str, Any]) -> Dict[str, float]:
        """Infiere puntuaciones sugeridas de 0.0 a 5.0 para cada dimensión a partir del comentario."""
        pass

    @abstractmethod
    def redactar_informe(
        self,
        observaciones_anonimas: List[Dict[str, Any]],
        prompt_docente: str,
        es_individual: bool,
        metadatos: Dict[str, Any] = None
    ) -> str:
        """Redacta el informe pedagógico formativo usando placeholders [NOMBRE_ESTUDIANTE] y [PRONOMBRE]."""
        pass

class OpenAIService(BaseLLMService):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def inferir_rubrica(self, comentario_anonimo: str, rubrica_data: Dict[str, Any]) -> Dict[str, float]:
        if not self.api_key:
            return SimuladoLLMService().inferir_rubrica(comentario_anonimo, rubrica_data)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            dimensiones_info = "\n".join([
                f"- Clave: {d['clave']}, Nombre: {d['nombre']}. Descripción: {d.get('descripcion', '')}. "
                f"Tramos: Bajo (0-2.9): {d.get('descriptor_bajo', '')}, Básico (3-3.9): {d.get('descriptor_basico', '')}, "
                f"Alto (4-4.5): {d.get('descriptor_alto', '')}, Superior (4.6-5): {d.get('descriptor_superior', '')}"
                for d in rubrica_data.get("dimensiones", [])
            ])

            prompt = f"""Eres un evaluador pedagógico experto del GovLab - Universidad de la Sabana.
Analiza la siguiente observación docente sobre un estudiante y sugiere una calificación numérica entre 0.0 y 5.0 para cada una de las dimensiones de la rúbrica '{rubrica_data.get('nombre')}'.

Observación del docente (datos anonimizados):
"{comentario_anonimo}"

Dimensiones evaluadas:
{dimensiones_info}

Responde ÚNICAMENTE en formato JSON con las claves de las dimensiones y sus valores numéricos (números flotantes con un decimal entre 0.0 y 5.0).
Ejemplo: {{"dim_1_logica": 4.2, "dim_2_resolucion": 3.8}}"""

            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"[OpenAIService] Error en inferencia: {e}. Usando respaldo simulado.")
            return SimuladoLLMService().inferir_rubrica(comentario_anonimo, rubrica_data)

    def redactar_informe(
        self,
        observaciones_anonimas: List[Dict[str, Any]],
        prompt_docente: str,
        es_individual: bool,
        metadatos: Dict[str, Any] = None
    ) -> str:
        if not self.api_key:
            return SimuladoLLMService().redactar_informe(observaciones_anonimas, prompt_docente, es_individual, metadatos)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            obs_texto = "\n".join([
                f"- Fecha: {o.get('fecha')}, Materia: {o.get('clase')}, Observación: {o.get('texto')}, Calificaciones: {o.get('calificaciones')}"
                for o in observaciones_anonimas
            ])

            if es_individual:
                system_prompt = """Eres el asistente de evaluación formativa Estudiante360 del GovLab de la Universidad de la Sabana.
Tu misión es redactar informes cualitativos individuales, integrales, constructivos y de alto valor pedagógico basados en bitácoras de observación docente.

REGLAS ESTRICTAS DE PRIVACIDAD Y PERSONALIZACIÓN INDIVIDUAL:
1. En ningún caso conoces el nombre real del estudiante.
2. Cada vez que te refieras al estudiante, utiliza SIEMPRE el marcador [NOMBRE_ESTUDIANTE] (por ejemplo: "Durante el período evaluado, [NOMBRE_ESTUDIANTE] ha evidenciado..."). No uses nombres ficticios ni te limites a decir "el alumno" sin el marcador [NOMBRE_ESTUDIANTE].
3. Debes usar el marcador [PRONOMBRE] para referirte a él o ella según convenga gramaticalmente.
4. Si se mencionan compañeros, refiérete a ellos como 'un compañero' o mantén [COMPANERO_1].

ESTRUCTURA DEL INFORME:
1. Resumen Diagnóstico de la Trayectoria Formativa.
2. Fortalezas y Competencias Destacadas.
3. Áreas de Oportunidad y Retos Pedagógicos Observados.
4. Recomendaciones y Plan de Acción Concreto."""

                user_prompt = f"""Instrucción particular del docente:
{prompt_docente}

Observaciones registradas en el período:
{obs_texto}

Redacta el informe individual con tono empático, riguroso y formal."""
            else:
                system_prompt = """Eres el asistente de evaluación formativa Estudiante360 del GovLab de la Universidad de la Sabana.
Tu misión es redactar un informe colectivo de aula / curso institucional, analizando las tendencias grupales, la convivencia, los logros de aprendizaje colectivos y las dinámicas del grupo basadas en la bitácora de observaciones de la cohorte.

REGLAS ESTRICTAS PARA INFORMES COLECTIVOS DE AULA / CURSO:
1. Este es un informe GRUPAL / COLECTIVO DE AULA para todo el curso o cohorte, NO para un estudiante individual.
2. NUNCA utilices [NOMBRE_ESTUDIANTE] ni hables en términos de un solo estudiante. Refiérete siempre al "grupo", "la clase", "el curso", "los estudiantes" o "la cohorte".
3. Sintetiza los patrones comunes observados en el aula, las dinámicas de participación grupal, el clima de convivencia y los logros y retos compartidos.
4. Formula recomendaciones pedagógicas orientadas a la gestión docente, trabajo en equipo, metodologías de aula y articulación con el director de curso.

ESTRUCTURA DEL INFORME COLECTIVO DE AULA:
1. Diagnóstico General y Clima de Aula del Grupo.
2. Fortalezas Colectivas y Competencias Grupales Destacadas.
3. Retos Pedagógicos y Convivenciales del Curso.
4. Estrategias y Recomendaciones Pedagógicas para el Equipo Docente."""

                user_prompt = f"""Instrucción particular del docente / directivo:
{prompt_docente}

Bitácora de observaciones del curso en el período:
{obs_texto}

Redacta el informe colectivo de aula con tono profesional, constructivo, riguroso y pedagógico."""

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[OpenAIService] Error en redacción: {e}. Usando respaldo simulado.")
            return SimuladoLLMService().redactar_informe(observaciones_anonimas, prompt_docente, es_individual, metadatos)

class AnthropicService(BaseLLMService):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")

    def inferir_rubrica(self, comentario_anonimo: str, rubrica_data: Dict[str, Any]) -> Dict[str, float]:
        if not self.api_key:
            return SimuladoLLMService().inferir_rubrica(comentario_anonimo, rubrica_data)

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)

            dimensiones_info = "\n".join([
                f"- Clave: {d['clave']}, Nombre: {d['nombre']}. Tramos: Bajo (0-2.9), Básico (3-3.9), Alto (4-4.5), Superior (4.6-5)"
                for d in rubrica_data.get("dimensiones", [])
            ])

            prompt = f"""Eres un evaluador pedagógico experto del GovLab - Universidad de la Sabana.
Analiza la siguiente observación docente y sugiere una nota entre 0.0 y 5.0 para cada dimensión.
Observación: "{comentario_anonimo}"
Dimensiones:
{dimensiones_info}

Responde ÚNICAMENTE un objeto JSON válido con las claves y valores numéricos. No incluyas texto previo ni posterior."""

            response = client.messages.create(
                model=self.model,
                max_tokens=300,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.content[0].text
            # Limpiar posibles bloques markdown ```json ... ```
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content.strip())
        except Exception as e:
            print(f"[AnthropicService] Error en inferencia: {e}. Usando respaldo simulado.")
            return SimuladoLLMService().inferir_rubrica(comentario_anonimo, rubrica_data)

    def redactar_informe(
        self,
        observaciones_anonimas: List[Dict[str, Any]],
        prompt_docente: str,
        es_individual: bool,
        metadatos: Dict[str, Any] = None
    ) -> str:
        if not self.api_key:
            return SimuladoLLMService().redactar_informe(observaciones_anonimas, prompt_docente, es_individual, metadatos)

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)

            obs_texto = "\n".join([
                f"- Fecha: {o.get('fecha')}, Materia: {o.get('clase')}, Observación: {o.get('texto')}"
                for o in observaciones_anonimas
            ])

            if es_individual:
                system_prompt = """Eres el asistente de evaluación formativa Estudiante360 del GovLab de la Universidad de la Sabana.
Tu misión es redactar informes cualitativos individuales, integrales y constructivos basados en bitácoras de observación docente.

REGLAS DE PRIVACIDAD Y PERSONALIZACIÓN INDIVIDUAL:
1. En ningún caso conoces el nombre real del estudiante.
2. Cada vez que te refieras al estudiante evaluado, utiliza SIEMPRE el marcador [NOMBRE_ESTUDIANTE] (por ejemplo: "Durante este período, [NOMBRE_ESTUDIANTE] demostró...").
3. Usa el marcador [PRONOMBRE] para referirte a él o ella según convenga gramaticalmente.
4. Si se mencionan compañeros, usa 'un compañero' o [COMPANERO_1].

ESTRUCTURA DEL INFORME:
1. Resumen Diagnóstico de la Trayectoria Formativa.
2. Fortalezas y Competencias Destacadas.
3. Áreas de Oportunidad y Retos Pedagógicos Observados.
4. Recomendaciones y Plan de Acción Concreto."""

                user_prompt = f"""Instrucciones del docente: {prompt_docente}

Observaciones del período:
{obs_texto}

Redacta un informe formativo individual completo con: Diagnóstico general, Fortalezas, Aspectos por Mejorar y Recomendaciones Pedagógicas."""
            else:
                system_prompt = """Eres el asistente de evaluación formativa Estudiante360 del GovLab de la Universidad de la Sabana.
Tu misión es redactar un informe pedagógico colectivo de aula / curso institucional, analizando las tendencias grupales, la convivencia, los logros de aprendizaje colectivos y las dinámicas del grupo basadas en la bitácora de observaciones de la cohorte.

REGLAS ESTRICTAS PARA INFORMES COLECTIVOS DE AULA / CURSO:
1. Este es un informe GRUPAL / COLECTIVO DE AULA para todo el curso o cohorte, NO para un estudiante individual.
2. NUNCA utilices [NOMBRE_ESTUDIANTE] ni hables en términos de un solo estudiante. Refiérete siempre al "grupo", "la clase", "el curso", "los estudiantes" o "la cohorte".
3. Sintetiza los patrones comunes observados en el aula, las dinámicas de participación grupal, el clima de convivencia y los logros y retos compartidos.
4. Formula recomendaciones pedagógicas orientadas a la gestión docente, trabajo en equipo, metodologías de aula y articulación con el director de curso.

ESTRUCTURA DEL INFORME COLECTIVO DE AULA:
1. Diagnóstico General y Clima de Aula del Grupo.
2. Fortalezas Colectivas y Competencias Grupales Destacadas.
3. Retos Pedagógicos y Convivenciales del Curso.
4. Estrategias y Recomendaciones Pedagógicas para el Equipo Docente."""

                user_prompt = f"""Instrucciones del docente / directivo: {prompt_docente}

Bitácora de observaciones del curso en el período:
{obs_texto}

Redacta un informe colectivo de aula completo con: Diagnóstico general del clima de aula, Fortalezas colectivas, Retos del curso y Recomendaciones pedagógicas grupales."""

            response = client.messages.create(
                model=self.model,
                max_tokens=1200,
                temperature=0.4,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"[AnthropicService] Error en redacción: {e}. Usando respaldo simulado.")
            return SimuladoLLMService().redactar_informe(observaciones_anonimas, prompt_docente, es_individual, metadatos)

class SimuladoLLMService(BaseLLMService):
    """Servicio simulado para pruebas offline, demostraciones o ambientes sin API Key activa."""

    def inferir_rubrica(self, comentario_anonimo: str, rubrica_data: Dict[str, Any]) -> Dict[str, float]:
        import random
        comentario_lower = comentario_anonimo.lower()
        es_positivo = any(p in comentario_lower for p in ["excelente", "sobresaliente", "dominio", "agilidad", "liderazgo", "muy bien", "gran"])
        es_negativo = any(p in comentario_lower for p in ["dificultad", "cuesta", "frustración", "pelea", "altercado", "distraído", "inseguridad", "fallas"])

        resultado = {}
        for d in rubrica_data.get("dimensiones", []):
            if es_positivo:
                val = round(random.uniform(4.3, 4.9), 1)
            elif es_negativo:
                val = round(random.uniform(2.2, 3.2), 1)
            else:
                val = round(random.uniform(3.5, 4.2), 1)
            resultado[d["clave"]] = val

        return resultado

    def redactar_informe(
        self,
        observaciones_anonimas: List[Dict[str, Any]],
        prompt_docente: str,
        es_individual: bool,
        metadatos: Dict[str, Any] = None
    ) -> str:
        if es_individual:
            return (
                "### 1. Diagnóstico General y Evolución Formativa\n"
                "A lo largo del período académico evaluado, [NOMBRE_ESTUDIANTE] ha evidenciado una trayectoria dinámica con avances sustanciales en su proceso de aprendizaje. "
                "Las observaciones docentes señalan que [PRONOMBRE] participa con compromiso en las sesiones curriculares y responde favorablemente a las estrategias pedagógicas orientadas al desarrollo de competencias.\n\n"
                "### 2. Fortalezas y Competencias Destacadas\n"
                "- **Capacidad de Comprensión y Aplicación**: Demuestra consistencia conceptual al abordar temáticas complejas y estructurar soluciones efectivas.\n"
                "- **Disposición para la Indagación**: Muestra curiosidad académica y aporta preguntas relevantes en clase.\n"
                "- **Convivencia y Trabajo en Equipo**: Promueve interacciones constructivas con sus pares cuando se propician espacios colaborativos.\n\n"
                "### 3. Aspectos Pedagógicos y Convivenciales por Fortalecer\n"
                "- **Consolidación en Tareas Complejas**: En momentos de alta exigencia o ante conceptos abstractos, [PRONOMBRE] puede manifestar dudas que requieren acompañamiento puntual para mantener la seguridad.\n"
                "- **Autorregulación de la Atención**: Conviene afianzar hábitos de concentración sostenida durante explicaciones grupales extensas.\n\n"
                "### 4. Recomendaciones y Plan de Acción Sugerido\n"
                "Se sugiere continuar fortaleciendo la confianza académica de [NOMBRE_ESTUDIANTE] mediante ejercicios prácticos contextualizados y mantener una comunicación constante entre la institución y la familia para consolidar hábitos de estudio ordenados en el hogar."
            )
        else:
            return (
                "### 1. Diagnóstico General y Clima de Aula del Grupo\n"
                "A lo largo del período evaluado, el grupo de estudiantes ha demostrado un proceso dinámico y participativo en las diferentes actividades curriculares. Se observa un clima de aula propicio para el aprendizaje colaborativo, con una notable disposición hacia el diálogo pedagógico y la construcción colectiva del conocimiento.\n\n"
                "### 2. Fortalezas Colectivas y Competencias Grupales Destacadas\n"
                "- **Trabajo Colaborativo y Cohesión**: Los estudiantes demuestran gran capacidad para integrarse en equipos de trabajo, asumiendo roles con responsabilidad y apoyándose mutuamente en el logro de metas comunes.\n"
                "- **Participación Activa y Pensamiento Crítico**: Se evidencia iniciativa para plantear inquietudes fundamentadas y enriquecer las discusiones en clase con argumentos sólidos.\n"
                "- **Apropiación Conceptual**: En la mayoría de las áreas evaluadas, el curso exhibe un dominio consistente de los conceptos clave y habilidad para aplicarlos en contextos prácticos.\n\n"
                "### 3. Retos Pedagógicos y Convivenciales del Curso\n"
                "- **Autorregulación y Concentración Colectiva**: En momentos de transición entre actividades o sesiones extensas, se requiere afianzar la gestión del tiempo y la atención sostenida de todo el grupo.\n"
                "- **Manejo de Diferencias y Comunicación Asertiva**: Aunque la convivencia es en general positiva, se recomienda continuar fortaleciendo las habilidades socioemocionales para la mediación pacífica ante discrepancias de opinión.\n\n"
                "### 4. Estrategias y Recomendaciones Pedagógicas para el Equipo Docente\n"
                "- Implementar metodologías activas y proyectos interdisciplinarios que canalicen el liderazgo y la energía del curso de manera constructiva.\n"
                "- Establecer acuerdos pedagógicos explícitos al inicio de cada bloque temático para optimizar la autorregulación grupal.\n"
                "- Mantener canales fluidos de retroalimentación formativa y articulación continua con la dirección de grupo y las familias."
            )

def get_llm_service(provider: str = None) -> BaseLLMService:
    prov = provider or os.getenv("LLM_PROVIDER_DEFAULT", "openai").lower()
    if prov == "anthropic":
        return AnthropicService()
    elif prov == "openai":
        return OpenAIService()
    return SimuladoLLMService()
