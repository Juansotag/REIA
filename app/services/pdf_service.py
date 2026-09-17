"""
Servicio de Generación Documental PDF para REIA.
GovLab: Universidad de la Sabana.
Genera informes oficiales con estilos institucionales, gráficas incrustadas y firmas.
"""

import io
import base64
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle

class PdfService:

    @staticmethod
    def generar_informe_pdf(
        titulo_informe: str,
        datos_cabecera: Dict[str, str],
        contenido_ia: str,
        grafica_base64: str = None,
        tabla_rubrica: list = None
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=45,
            leftMargin=45,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        # Estilos Institucionales UniSabana
        c_blue_dark = colors.HexColor("#00135B")
        c_blue_light = colors.HexColor("#00387D")
        c_text = colors.HexColor("#374151")
        c_tint = colors.HexColor("#D9E1EF")

        style_title = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            textColor=c_blue_dark,
            spaceAfter=10
        )

        style_heading = ParagraphStyle(
            "HeadingStyle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=c_blue_light,
            spaceBefore=12,
            spaceAfter=6
        )

        style_body = ParagraphStyle(
            "BodyStyle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            textColor=c_text,
            leading=13,
            spaceAfter=6
        )

        style_bullet = ParagraphStyle(
            "BulletStyle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=c_text,
            leading=12,
            leftIndent=15,
            spaceAfter=4
        )

        story = []

        # 1. Cabecera
        header_data = [
            [
                Paragraph("<b>GovLab: Universidad de la Sabana</b>", style_body),
                Paragraph("<b>REIA</b> | Reporte Oficial", ParagraphStyle("RightHdr", parent=style_body, alignment=2))
            ]
        ]
        t_header = Table(header_data, colWidths=[300, 220])
        t_header.setStyle(TableStyle([
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LINEBELOW", (0, 0), (-1, -1), 1.5, c_blue_dark)
        ]))
        story.append(t_header)
        story.append(Spacer(1, 14))

        # Título
        story.append(Paragraph(titulo_informe, style_title))

        # 2. Ficha Técnica
        tabla_datos = []
        for k, v in datos_cabecera.items():
            tabla_datos.append([
                Paragraph(f"<b>{k}:</b>", style_body),
                Paragraph(str(v), style_body)
            ])
        t_ficha = Table(tabla_datos, colWidths=[160, 360])
        t_ficha.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, c_tint),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, c_tint),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t_ficha)
        story.append(Spacer(1, 14))

        # 3. Gráfica si existe
        if grafica_base64:
            story.append(Paragraph("Trayectoria y Desempeño Longitudinal", style_heading))
            try:
                img_bytes = base64.b64decode(grafica_base64)
                img_io = io.BytesIO(img_bytes)
                rl_img = RLImage(img_io, width=480, height=240)
                story.append(rl_img)
                story.append(Spacer(1, 10))
            except Exception as e:
                print(f"[PdfService] Error al incrustar gráfica: {e}")

        # 4. Narrativa de la IA
        story.append(Paragraph("Análisis Cualitativo y Recomendaciones Pedagógicas", style_heading))
        for line in contenido_ia.split("\n"):
            line_str = line.strip()
            if not line_str:
                continue
            if line_str.startswith("###") or line_str.startswith("##"):
                story.append(Paragraph(line_str.lstrip("#").strip(), style_heading))
            elif line_str.startswith("-") or line_str.startswith("*"):
                story.append(Paragraph(f"• {line_str.lstrip('-*').strip()}", style_bullet))
            else:
                story.append(Paragraph(line_str, style_body))

        # 5. Firmas
        story.append(Spacer(1, 30))
        firmas_data = [
            ["_________________________", "_________________________", "_________________________"],
            ["Docente Titular", "Coordinador Académico", "Orientador Escolar"]
        ]
        t_firmas = Table(firmas_data, colWidths=[170, 170, 170])
        t_firmas.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 1), (-1, 1), 8.5),
            ("TEXTCOLOR", (0, 1), (-1, 1), c_blue_dark),
        ]))
        story.append(t_firmas)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
