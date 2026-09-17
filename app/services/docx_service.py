"""
Servicio de Generación Documental Word (.docx) para REIA.
GovLab: Universidad de la Sabana.
Genera informes oficiales editables con membrete, ficha técnica, gráficas incrustadas y firmas.
"""

import io
import base64
import os
from typing import Dict, Any
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

class DocxService:

    @staticmethod
    def generar_informe_docx(
        titulo_informe: str,
        datos_cabecera: Dict[str, str],
        contenido_ia: str,
        grafica_base64: str = None,
        tabla_rubrica: list = None
    ) -> bytes:
        doc = Document()

        # Configuración de márgenes
        for section in doc.sections:
            section.top_margin = Inches(0.8)
            section.bottom_margin = Inches(0.8)
            section.left_margin = Inches(0.9)
            section.right_margin = Inches(0.9)

        # 1. Encabezado Institucional
        header_table = doc.add_table(rows=1, cols=2)
        header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        header_table.autofit = False

        # Logo si existe
        cell_logo = header_table.cell(0, 0)
        logo_path = "static/img/GovLab_blanco.png"
        if os.path.exists(logo_path):
            try:
                # El logo blanco queda excelente si se inserta o si se añade con fondo,
                # o insertamos texto institucional estilizado
                p_logo = cell_logo.paragraphs[0]
                p_logo.add_run("GovLab\n").bold = True
                p_logo.runs[0].font.size = Pt(16)
                p_logo.runs[0].font.color.rgb = RGBColor(0, 19, 91)
                p_sub = p_logo.add_run("Universidad de la Sabana")
                p_sub.font.size = Pt(10)
                p_sub.font.color.rgb = RGBColor(147, 170, 201)
            except Exception:
                pass

        cell_title = header_table.cell(0, 1)
        p_title = cell_title.paragraphs[0]
        p_title.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_tool = p_title.add_run("REIA: Evaluación Formativa\n")
        r_tool.font.size = Pt(11)
        r_tool.bold = True
        r_tool.font.color.rgb = RGBColor(0, 19, 91)
        r_date = p_title.add_run("Informe Oficial de Seguimiento Académico")
        r_date.font.size = Pt(9)
        r_date.font.color.rgb = RGBColor(100, 116, 139)

        doc.add_paragraph().paragraph_format.space_after = Pt(8)

        # Título Principal
        h1 = doc.add_heading(level=1)
        h1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r_h1 = h1.add_run(titulo_informe)
        r_h1.font.size = Pt(18)
        r_h1.font.color.rgb = RGBColor(0, 19, 91)
        h1.paragraph_format.space_after = Pt(12)

        # 2. Ficha Técnica
        info_table = doc.add_table(rows=len(datos_cabecera), cols=2)
        info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for idx, (label, val) in enumerate(datos_cabecera.items()):
            row = info_table.rows[idx]
            cell_lbl = row.cells[0]
            cell_val = row.cells[1]
            
            p_lbl = cell_lbl.paragraphs[0]
            r_lbl = p_lbl.add_run(label)
            r_lbl.bold = True
            r_lbl.font.size = Pt(9.5)
            r_lbl.font.color.rgb = RGBColor(0, 19, 91)

            p_val = cell_val.paragraphs[0]
            r_val = p_val.add_run(val)
            r_val.font.size = Pt(9.5)
            r_val.font.color.rgb = RGBColor(55, 65, 81)

        doc.add_paragraph().paragraph_format.space_after = Pt(10)

        # 3. Gráfica Incrustada si está presente
        if grafica_base64:
            h_grafica = doc.add_heading(level=2)
            r_hg = h_grafica.add_run("Trayectoria y Desempeño Longitudinal")
            r_hg.font.size = Pt(13)
            r_hg.font.color.rgb = RGBColor(0, 56, 125)

            try:
                img_bytes = base64.b64decode(grafica_base64)
                img_stream = io.BytesIO(img_bytes)
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.add_run().add_picture(img_stream, width=Inches(6.0))
                p_img.paragraph_format.space_after = Pt(12)
            except Exception as e:
                print(f"[DocxService] Error al incrustar gráfica: {e}")

        # 4. Contenido Cualitativo Redactado por IA
        h_ia = doc.add_heading(level=2)
        r_hia = h_ia.add_run("Análisis Cualitativo y Recomendaciones Pedagógicas")
        r_hia.font.size = Pt(13)
        r_hia.font.color.rgb = RGBColor(0, 56, 125)

        import re
        for line in contenido_ia.split("\n"):
            line_str = line.strip()
            if not line_str:
                continue
            if line_str.startswith("####"):
                h_sub = doc.add_heading(level=4)
                r_sub = h_sub.add_run(line_str.lstrip("#").strip())
                r_sub.font.size = Pt(10)
                r_sub.font.color.rgb = RGBColor(0, 19, 91)
            elif line_str.startswith("###") or line_str.startswith("##") or line_str.startswith("#"):
                h_sub = doc.add_heading(level=3)
                r_sub = h_sub.add_run(line_str.lstrip("#").strip())
                r_sub.font.size = Pt(11)
                r_sub.font.color.rgb = RGBColor(0, 19, 91)
            elif line_str.startswith("-") or line_str.startswith("*"):
                p_b = doc.add_paragraph(style="List Bullet")
                raw_item = line_str.lstrip("-*").strip()
                parts = re.split(r'(\*\*.*?\*\*)', raw_item)
                for part in parts:
                    if part.startswith('**') and part.endswith('**'):
                        r = p_b.add_run(part[2:-2])
                        r.bold = True
                    else:
                        r = p_b.add_run(part)
                    r.font.size = Pt(10)
                    r.font.color.rgb = RGBColor(55, 65, 81)
            else:
                p = doc.add_paragraph()
                parts = re.split(r'(\*\*.*?\*\*)', line_str)
                for part in parts:
                    if part.startswith('**') and part.endswith('**'):
                        r = p.add_run(part[2:-2])
                        r.bold = True
                    else:
                        r = p.add_run(part)
                    r.font.size = Pt(10)
                    r.font.color.rgb = RGBColor(55, 65, 81)
                p.paragraph_format.space_after = Pt(6)

        # 5. Tabla de Dimensiones de Rúbrica si está presente
        if tabla_rubrica:
            doc.add_paragraph().paragraph_format.space_after = Pt(8)
            h_tab = doc.add_heading(level=2)
            r_htab = h_tab.add_run("Resumen Cuantitativo por Dimensión")
            r_htab.font.size = Pt(13)
            r_htab.font.color.rgb = RGBColor(0, 56, 125)

            rtable = doc.add_table(rows=len(tabla_rubrica) + 1, cols=3)
            rtable.alignment = WD_TABLE_ALIGNMENT.CENTER
            hdr = rtable.rows[0]
            hdr.cells[0].paragraphs[0].add_run("Dimensión").bold = True
            hdr.cells[1].paragraphs[0].add_run("Nota Promedio").bold = True
            hdr.cells[2].paragraphs[0].add_run("Nivel de Desempeño").bold = True

            for idx, item in enumerate(tabla_rubrica, 1):
                row = rtable.rows[idx]
                row.cells[0].paragraphs[0].add_run(str(item.get("dimension", "")))
                row.cells[1].paragraphs[0].add_run(f"{float(item.get('promedio', 0.0)):.1f}")
                row.cells[2].paragraphs[0].add_run(str(item.get("nivel", "")))

        # 6. Espacio de Firmas
        doc.add_paragraph().paragraph_format.space_after = Pt(36)
        sig_table = doc.add_table(rows=1, cols=3)
        sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER

        firmas = ["Docente Titular", "Coordinador Académico", "Orientador Escolar"]
        for idx, cargo in enumerate(firmas):
            cell = sig_table.cell(0, idx)
            p_sig = cell.paragraphs[0]
            p_sig.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_sig.add_run("_________________________\n").font.size = Pt(10)
            r_c = p_sig.add_run(cargo)
            r_c.bold = True
            r_c.font.size = Pt(9)
            r_c.font.color.rgb = RGBColor(0, 19, 91)

        out_stream = io.BytesIO()
        doc.save(out_stream)
        return out_stream.getvalue()
