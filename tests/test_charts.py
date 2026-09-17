import base64
from app.services.chart_service import ChartService
from app.services.docx_service import DocxService
from app.services.pdf_service import PdfService

def test_generacion_grafica_individual():
    fechas = ["10/02", "24/02", "10/03", "24/03"]
    series = {
        "Pensamiento Lógico": [3.5, 3.8, 4.2, 4.5],
        "Resolución de Problemas": [3.0, 3.2, 3.8, 4.0]
    }
    img_b64 = ChartService.generar_grafica_individual_base64(fechas, series, "Rúbrica Matemáticas")
    assert isinstance(img_b64, str)
    assert len(img_b64) > 1000
    # Verificar que es decodificable como PNG
    decoded = base64.b64decode(img_b64)
    assert decoded.startswith(b"\x89PNG")

def test_generacion_grafica_boxplots():
    periodos = ["Feb 2026", "Mar 2026", "Abr 2026"]
    distribuciones = [
        [2.5, 3.0, 3.5, 3.8, 4.0, 4.5],
        [3.0, 3.5, 3.8, 4.0, 4.2, 4.8],
        [3.2, 3.8, 4.0, 4.2, 4.5, 4.9]
    ]
    img_b64 = ChartService.generar_grafica_agregada_curso_base64(periodos, distribuciones, "Distribución Noveno B")
    assert isinstance(img_b64, str)
    decoded = base64.b64decode(img_b64)
    assert decoded.startswith(b"\x89PNG")

def test_generacion_docx():
    docx_bytes = DocxService.generar_informe_docx(
        titulo_informe="Informe de Prueba REIA",
        datos_cabecera={"Estudiante": "Sofía Ramírez", "Curso": "Noveno B"},
        contenido_ia="### 1. Diagnóstico\nEl estudiante presenta un desempeño óptimo.",
        grafica_base64=None,
        tabla_rubrica=[{"dimension": "Lógica", "promedio": 4.5, "nivel": "Alto"}]
    )
    assert isinstance(docx_bytes, bytes)
    assert len(docx_bytes) > 2000
    # Formato zip/docx inicia con PK
    assert docx_bytes.startswith(b"PK")

def test_generacion_pdf():
    pdf_bytes = PdfService.generar_informe_pdf(
        titulo_informe="Informe de Prueba PDF",
        datos_cabecera={"Estudiante": "Juan Morales", "Curso": "Décimo A"},
        contenido_ia="### 1. Diagnóstico\nDesempeño sobresaliente en ciencias.",
        grafica_base64=None,
        tabla_rubrica=[{"dimension": "Indagación", "promedio": 4.6, "nivel": "Superior"}]
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")
