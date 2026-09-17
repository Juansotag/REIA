"""
Servicio de Privacidad y Anonimización Zero-PII para REIA.
GovLab: Universidad de la Sabana.
Asegura que ningún nombre, documento de identidad ni dato identificable viaje a proveedores externos de IA.
"""

import re
from typing import List, Dict, Any

class PrivacyService:

    @staticmethod
    def detectar_menciones(texto: str, estudiantes_curso: List[Any]) -> List[Dict[str, Any]]:
        """
        Analiza el texto transcrito para detectar posibles menciones de compañeros del mismo curso.
        Retorna una lista de coincidencias con su posición para renderizar chiclets interactivos.
        """
        if not texto:
            return []

        menciones_detectadas = []
        texto_lower = texto.lower()

        for est in estudiantes_curso:
            nombre_partes = est.nombres.split()
            primer_nombre = nombre_partes[0].lower()
            nombre_completo = est.nombre_completo.lower()

            # Buscar nombre completo primero, luego primer nombre
            patron = rf"\b{re.escape(primer_nombre)}\b"
            coincidencias = list(re.finditer(patron, texto_lower))

            if coincidencias:
                for match in coincidencias:
                    menciones_detectadas.append({
                        "estudiante_id": est.id,
                        "nombre_detectado": match.group(0),
                        "nombre_sugerido": est.nombre_completo,
                        "start": match.start(),
                        "end": match.end()
                    })

        return menciones_detectadas

    @staticmethod
    def anonimizar_texto(
        texto: str,
        estudiante_principal: Any,
        companeros_confirmados: List[Dict[str, Any]] = None
    ) -> str:
        """
        Sanitiza el comentario docente antes de enviarlo a cualquier servicio de LLM.
        Sustituye el nombre del estudiante evaluado por [ESTUDIANTE].
        Sustituye nombres de otros compañeros por [COMPANERO_1], [COMPANERO_2], etc.
        """
        if not texto:
            return ""

        texto_anon = texto

        # 1. Anonimizar al estudiante principal
        if estudiante_principal:
            # Reemplazar nombre completo
            texto_anon = re.sub(
                rf"\b{re.escape(estudiante_principal.nombre_completo)}\b",
                "[ESTUDIANTE]",
                texto_anon,
                flags=re.IGNORECASE
            )
            # Reemplazar primer nombre y segundo nombre
            for parte in estudiante_principal.nombres.split():
                if len(parte) > 2:
                    texto_anon = re.sub(
                        rf"\b{re.escape(parte)}\b",
                        "[ESTUDIANTE]",
                        texto_anon,
                        flags=re.IGNORECASE
                    )
            # Reemplazar apellidos
            for parte in estudiante_principal.apellidos.split():
                if len(parte) > 2:
                    texto_anon = re.sub(
                        rf"\b{re.escape(parte)}\b",
                        "[ESTUDIANTE]",
                        texto_anon,
                        flags=re.IGNORECASE
                    )

        # 2. Anonimizar compañeros confirmados
        if companeros_confirmados:
            for idx, comp in enumerate(companeros_confirmados, 1):
                nombre_comp = comp.get("nombre", "")
                if nombre_comp:
                    for parte in nombre_comp.split():
                        if len(parte) > 2:
                            texto_anon = re.sub(
                                rf"\b{re.escape(parte)}\b",
                                f"[COMPANERO_{idx}]",
                                texto_anon,
                                flags=re.IGNORECASE
                            )

        return texto_anon

    @staticmethod
    def reemplazar_tokens_locales(texto_ia: str, estudiante: Any) -> str:
        """
        Motor de Reemplazo Local (Local Token Swapper).
        Toma el texto generado por la IA y sustituye en memoria las variables genéricas
        por los datos reales del estudiante justo antes de renderizar o exportar a Word/PDF.
        """
        if not texto_ia or not estudiante:
            return texto_ia

        resultado = texto_ia
        nombre_completo = estudiante.nombre_completo
        pronombre = estudiante.pronombre or ("él" if getattr(estudiante, "genero", "Masculino") == "Masculino" else "ella")

        # Reemplazo de todas las posibles variantes de placeholders para el nombre
        patrones_nombre = [
            r"\[NOMBRE[_\s]+ESTUDIANTE\]",
            r"\[NOMBRE[_\s]+DEL[_\s]+ESTUDIANTE\]",
            r"\[NOMBRE[_\s]+DE[_\s]+LA[_\s]+ESTUDIANTE\]",
            r"\[NOMBRE[_\s]+DEL[_\s]+ALUMNO\]",
            r"\[NOMBRE[_\s]+DE[_\s]+LA[_\s]+ALUMNA\]",
            r"\[NOMBRE[_\s]+ALUMNO\]",
            r"\[NOMBRE\]",
            r"\[ESTUDIANTE\]",
            r"\[ALUMNO\]",
            r"\[ALUMNA\]",
            r"\[ESTUDIANTE[_\s]+EVALUADO\]",
            r"<NOMBRE(?:[_\s]+ESTUDIANTE)?>",
            r"\{NOMBRE(?:[_\s]+ESTUDIANTE)?\}",
        ]
        for pat in patrones_nombre:
            resultado = re.sub(pat, nombre_completo, resultado, flags=re.IGNORECASE)

        # Reemplazo de pronombres
        patrones_pronombre = [
            r"\[PRONOMBRE\]",
            r"\[él/ella\]",
            r"\[él\/ella\]",
            r"\[el/la\]",
            r"\[el\/la\]"
        ]
        for pat in patrones_pronombre:
            resultado = re.sub(pat, pronombre, resultado, flags=re.IGNORECASE)

        # Documento, edad, grado
        resultado = re.sub(r"\[(?:NUMERO_)?DOCUMENTO\]|\[ID_ESTUDIANTE\]", str(getattr(estudiante, "numero_documento", "")), resultado, flags=re.IGNORECASE)
        resultado = re.sub(r"\[EDAD\]", str(getattr(estudiante, "edad", "")), resultado, flags=re.IGNORECASE)
        resultado = re.sub(r"\[GRADO\]", f"{getattr(estudiante, 'grado_actual', '')}º Grado", resultado, flags=re.IGNORECASE)

        # Respaldo inteligente: si el modelo redactó en prosa genérica sin corchetes y el nombre no figura:
        if nombre_completo not in resultado:
            resultado = re.sub(
                r"\b(el\s+estudiante|la\s+estudiante|el\s+alumno|la\s+alumna)\b",
                f"\\1 {nombre_completo}",
                resultado,
                count=1,
                flags=re.IGNORECASE
            )

        return resultado
