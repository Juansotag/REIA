import json
from datetime import date
from fastapi import APIRouter, Depends, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Estudiante, Curso, Clase, Rubrica, Reporte, ModeloInforme, InformeGenerado
from app.services.privacy_service import PrivacyService
from app.services.llm_service import get_llm_service
from app.services.chart_service import ChartService
from app.services.docx_service import DocxService
from app.services.pdf_service import PdfService

router = APIRouter(prefix="/informes", tags=["Informes"])
templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
def index_informes(request: Request, db: Session = Depends(get_db)):
    estudiantes = db.query(Estudiante).filter_by(activo=True).order_by(Estudiante.apellidos).all()
    cursos = db.query(Curso).order_by(Curso.grado).all()
    rubricas = db.query(Rubrica).order_by(Rubrica.id).all()
    modelos = db.query(ModeloInforme).order_by(ModeloInforme.id).all()
    informes_guardados = db.query(InformeGenerado).order_by(InformeGenerado.created_at.desc()).limit(20).all()

    return templates.TemplateResponse(request, "informes/index.html", {
        "active_tab": "informes",
        "estudiantes": estudiantes,
        "cursos": cursos,
        "rubricas": rubricas,
        "modelos": modelos,
        "informes_guardados": informes_guardados
    })

@router.get("/ver-guardado/{informe_id}", response_class=HTMLResponse)
def ver_informe_guardado(informe_id: int, request: Request, db: Session = Depends(get_db)):
    inf = db.query(InformeGenerado).filter_by(id=informe_id).first()
    if not inf:
        return HTMLResponse("<div class='card'>Informe no encontrado.</div>")

    datos_cabecera = {}
    if inf.tipo_informe == "INDIVIDUAL" and inf.estudiante_id:
        est = db.query(Estudiante).filter_by(id=inf.estudiante_id).first()
        if est:
            datos_cabecera = {
                "Estudiante": est.nombre_completo,
                "Identificacion": f"{est.tipo_documento} {est.numero_documento}",
                "Grado": f"{est.grado_actual} grado",
                "Periodo de Evaluacion": f"{inf.fecha_inicio} al {inf.fecha_fin}"
            }
    elif inf.curso_id:
        cur = db.query(Curso).filter_by(id=inf.curso_id).first()
        if cur:
            datos_cabecera = {
                "Curso": cur.nombre,
                "Grado": f"{cur.grado} grado",
                "Director": cur.director_curso or "N/A",
                "Periodo de Analisis": f"{inf.fecha_inicio} al {inf.fecha_fin}"
            }

    titulo_informe = f"Informe Oficial: {datos_cabecera.get('Estudiante', datos_cabecera.get('Curso', 'Institucional'))}"

    payload_exportacion = json.dumps({
        "titulo_informe": titulo_informe,
        "datos_cabecera": datos_cabecera,
        "contenido_narrativo": inf.contenido_narrativo,
        "grafica_base64": inf.datos_grafica.get("grafica_base64") if inf.datos_grafica else None,
        "tabla_rubrica": inf.datos_grafica.get("tabla_rubrica", []) if inf.datos_grafica else []
    })

    return templates.TemplateResponse(request, "informes/preview_panel.html", {
        "titulo_informe": titulo_informe,
        "fecha_inicio": inf.fecha_inicio.isoformat(),
        "fecha_fin": inf.fecha_fin.isoformat(),
        "rubrica": None,
        "datos_cabecera": datos_cabecera,
        "grafica_base64": inf.datos_grafica.get("grafica_base64") if inf.datos_grafica else None,
        "contenido_narrativo": inf.contenido_narrativo,
        "tabla_rubrica": inf.datos_grafica.get("tabla_rubrica", []) if inf.datos_grafica else [],
        "payload_exportacion": payload_exportacion
    })

@router.post("/generar", response_class=HTMLResponse)
def generar_informe(
    request: Request,
    tipo_informe: str = Form("INDIVIDUAL"),
    estudiante_id: str = Form(""),
    curso_id: str = Form(""),
    rubrica_id: str = Form(""),
    fecha_inicio: str = Form("2026-02-01"),
    fecha_fin: str = Form("2026-11-30"),
    prompt_personalizado: str = Form(""),
    db: Session = Depends(get_db)
):
    f_ini = date.fromisoformat(fecha_inicio)
    f_fin = date.fromisoformat(fecha_fin)
    rub_id = int(rubrica_id) if rubrica_id and rubrica_id.isdigit() else None
    rubrica = db.query(Rubrica).filter_by(id=rub_id).first() if rub_id else None

    grafica_base64 = None
    tabla_rubrica = []
    observaciones_para_ia = []
    datos_cabecera = {}

    est_obj_id = None
    cur_obj_id = None

    if tipo_informe == "INDIVIDUAL":
        est_id = int(estudiante_id) if estudiante_id and estudiante_id.isdigit() else None
        estudiante = db.query(Estudiante).filter_by(id=est_id).first()
        if not estudiante:
            return HTMLResponse("<div class='card'>Estudiante no encontrado.</div>")

        est_obj_id = estudiante.id
        titulo_informe = f"Informe de Evaluacion Formativa: {estudiante.nombre_completo}"
        curso_nombre = estudiante.cursos[0].nombre if estudiante.cursos else "Sin Curso"
        datos_cabecera = {
            "Estudiante": estudiante.nombre_completo,
            "Identificacion": f"{estudiante.tipo_documento} {estudiante.numero_documento}",
            "Grado y Curso": f"{estudiante.grado_actual} grado ({curso_nombre})",
            "Edad": f"{estudiante.edad} anos",
            "Periodo de Evaluacion": f"{fecha_inicio} al {fecha_fin}"
        }

        query_rep = db.query(Reporte).filter(
            Reporte.estudiante_id == estudiante.id,
            Reporte.fecha >= f_ini,
            Reporte.fecha <= f_fin
        )
        if rub_id:
            query_rep = query_rep.filter(Reporte.rubrica_id == rub_id)

        reportes = query_rep.order_by(Reporte.fecha).all()

        fechas_str = []
        series_dims = {}
        for r in reportes:
            f_label = r.fecha.strftime("%d/%m")
            fechas_str.append(f_label)
            observaciones_para_ia.append({
                "fecha": r.fecha.isoformat(),
                "clase": r.clase.nombre if r.clase else "General",
                "texto": r.texto_anonimizado,
                "calificaciones": r.calificaciones_dimensiones
            })
            for dim_clave, val in r.calificaciones_dimensiones.items():
                if dim_clave not in series_dims:
                    series_dims[dim_clave] = []
                series_dims[dim_clave].append(float(val))

        series_nombradas = {}
        if rubrica:
            for dim in rubrica.dimensiones:
                if dim.clave in series_dims:
                    series_nombradas[dim.nombre] = series_dims[dim.clave]
                    prom = sum(series_dims[dim.clave]) / len(series_dims[dim.clave]) if series_dims[dim.clave] else 0.0
                    nivel = "Superior" if prom >= 4.6 else ("Alto" if prom >= 4.0 else ("Basico" if prom >= 3.0 else "Bajo"))
                    tabla_rubrica.append({"dimension": dim.nombre, "promedio": prom, "nivel": nivel})
        else:
            series_nombradas = series_dims

        if fechas_str and series_nombradas:
            grafica_base64 = ChartService.generar_grafica_individual_base64(
                fechas=fechas_str,
                series_dimensiones=series_nombradas,
                nombre_rubrica=rubrica.nombre if rubrica else "Evolucion Formativa"
            )

        llm = get_llm_service()
        texto_ia_bruto = llm.redactar_informe(
            observaciones_anonimas=observaciones_para_ia,
            prompt_docente=prompt_personalizado,
            es_individual=True
        )
        contenido_narrativo = PrivacyService.reemplazar_tokens_locales(texto_ia_bruto, estudiante)

    else:
        # AGREGADO POR CURSO
        c_id = int(curso_id) if curso_id and curso_id.isdigit() else None
        curso = db.query(Curso).filter_by(id=c_id).first()
        if not curso:
            return HTMLResponse("<div class='card'>Curso no encontrado.</div>")

        cur_obj_id = curso.id
        titulo_informe = f"Informe Colectivo de Aula: {curso.nombre}"
        datos_cabecera = {
            "Curso / Cohorte": curso.nombre,
            "Grado": f"{curso.grado} de Educacion Basica/Media",
            "Director de Curso": curso.director_curso or "N/A",
            "Periodo de Analisis": f"{fecha_inicio} al {fecha_fin}"
        }

        query_rep = db.query(Reporte).filter(
            Reporte.curso_id == curso.id,
            Reporte.fecha >= f_ini,
            Reporte.fecha <= f_fin
        )
        if rub_id:
            query_rep = query_rep.filter(Reporte.rubrica_id == rub_id)

        reportes = query_rep.order_by(Reporte.fecha).all()

        meses_data = {}
        for r in reportes:
            mes_label = r.fecha.strftime("%b %Y").capitalize()
            if mes_label not in meses_data:
                meses_data[mes_label] = []
            for val in r.calificaciones_dimensiones.values():
                try:
                    meses_data[mes_label].append(float(val))
                except ValueError:
                    pass

            observaciones_para_ia.append({
                "fecha": r.fecha.isoformat(),
                "clase": r.clase.nombre if r.clase else "",
                "texto": r.texto_anonimizado
            })

        periodos = list(meses_data.keys())
        distribuciones = [meses_data[p] for p in periodos if len(meses_data[p]) > 0]
        periodos_validos = [p for p in periodos if len(meses_data[p]) > 0]

        if periodos_validos and distribuciones:
            grafica_base64 = ChartService.generar_grafica_agregada_curso_base64(
                periodos=periodos_validos,
                distribuciones=distribuciones,
                nombre_rubrica=rubrica.nombre if rubrica else f"Distribucion Grupal {curso.nombre}"
            )

        llm = get_llm_service()
        contenido_narrativo = llm.redactar_informe(
            observaciones_anonimas=observaciones_para_ia,
            prompt_docente=prompt_personalizado,
            es_individual=False
        )

    # Guardar informe generado en la base de datos
    nuevo_informe = InformeGenerado(
        tipo_informe=tipo_informe,
        estudiante_id=est_obj_id,
        curso_id=cur_obj_id,
        fecha_inicio=f_ini,
        fecha_fin=f_fin,
        prompt_utilizado=prompt_personalizado,
        contenido_narrativo=contenido_narrativo,
        datos_grafica={"grafica_base64": grafica_base64, "tabla_rubrica": tabla_rubrica}
    )
    db.add(nuevo_informe)
    db.commit()

    payload_exportacion = json.dumps({
        "titulo_informe": titulo_informe,
        "datos_cabecera": datos_cabecera,
        "contenido_narrativo": contenido_narrativo,
        "grafica_base64": grafica_base64,
        "tabla_rubrica": tabla_rubrica
    })

    return templates.TemplateResponse(request, "informes/preview_panel.html", {
        "titulo_informe": titulo_informe,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "rubrica": rubrica,
        "datos_cabecera": datos_cabecera,
        "grafica_base64": grafica_base64,
        "contenido_narrativo": contenido_narrativo,
        "tabla_rubrica": tabla_rubrica,
        "payload_exportacion": payload_exportacion
    })

@router.post("/descargar-docx")
def descargar_docx(payload_json: str = Form(...)):
    data = json.loads(payload_json)
    docx_bytes = DocxService.generar_informe_docx(
        titulo_informe=data["titulo_informe"],
        datos_cabecera=data["datos_cabecera"],
        contenido_ia=data["contenido_narrativo"],
        grafica_base64=data.get("grafica_base64"),
        tabla_rubrica=data.get("tabla_rubrica")
    )

    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=Informe_REIA_Oficial.docx"}
    )

@router.post("/descargar-pdf")
def descargar_pdf(payload_json: str = Form(...)):
    data = json.loads(payload_json)
    pdf_bytes = PdfService.generar_informe_pdf(
        titulo_informe=data["titulo_informe"],
        datos_cabecera=data["datos_cabecera"],
        contenido_ia=data["contenido_narrativo"],
        grafica_base64=data.get("grafica_base64"),
        tabla_rubrica=data.get("tabla_rubrica")
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Informe_REIA_Oficial.pdf"}
    )
