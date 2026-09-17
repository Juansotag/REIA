"""
Servicio de Importación y Exportación de Estudiantes en Excel / CSV.
GovLab: Universidad de la Sabana.
"""

import io
import pandas as pd
from typing import List, Dict, Any

class ExcelService:

    @staticmethod
    def exportar_estudiantes_excel(estudiantes: List[Any]) -> bytes:
        data = []
        for e in estudiantes:
            cursos_str = ", ".join([c.nombre for c in e.cursos]) if e.cursos else "Sin curso"
            data.append({
                "ID": e.id,
                "UUID_Anonimo": e.uuid_anonimo,
                "Tipo_Doc": e.tipo_documento,
                "Numero_Documento": e.numero_documento,
                "Nombres": e.nombres,
                "Apellidos": e.apellidos,
                "Genero": e.genero,
                "Pronombre": e.pronombre,
                "Edad": e.edad,
                "Grado": e.grado_actual,
                "Curso": cursos_str,
                "Acudiente": e.acudiente_nombre or "",
                "Contacto_Acudiente": e.acudiente_contacto or ""
            })

        df = pd.DataFrame(data)
        out = io.BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Estudiantes")
        return out.getvalue()

    @staticmethod
    def importar_estudiantes(archivo_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
        """Lee archivo Excel o CSV y retorna lista de registros normalizados."""
        bio = io.BytesIO(archivo_bytes)
        if filename.endswith(".csv"):
            df = pd.read_csv(bio)
        else:
            df = pd.read_excel(bio)

        # Estandarizar nombres de columnas a minúsculas sin espacios
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

        estudiantes = []
        for _, row in df.iterrows():
            nombres = str(row.get("nombres", row.get("nombre", ""))).strip()
            apellidos = str(row.get("apellidos", row.get("apellido", ""))).strip()
            if not nombres or not apellidos:
                continue

            doc = str(row.get("numero_documento", row.get("documento", row.get("identificacion", "")))).strip()
            grado = int(row.get("grado", row.get("grado_actual", 9)))
            genero = str(row.get("genero", "Masculino")).strip().capitalize()
            pronombre = "él" if genero == "Masculino" else "ella"

            estudiantes.append({
                "nombres": nombres,
                "apellidos": apellidos,
                "tipo_documento": str(row.get("tipo_doc", "TI")).strip(),
                "numero_documento": doc,
                "genero": genero,
                "pronombre": pronombre,
                "edad": int(row.get("edad", grado + 5)),
                "grado_actual": grado,
                "acudiente_nombre": str(row.get("acudiente", "")).strip(),
                "acudiente_contacto": str(row.get("contacto_acudiente", "")).strip()
            })

        return estudiantes
