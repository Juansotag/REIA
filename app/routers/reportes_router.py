from datetime import date
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Estudiante, Curso, Clase, Rubrica, Reporte
from app.services.privacy_service import PrivacyService
from app.services.llm_service import get_llm_service

router = APIRouter(prefix="/reportes", tags=["Reportes"])
templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
def index_reportes(request: Request, db: Session = Depends(get_db)):
    cursos = db.query(Curso).order_by(Curso.grado).all()
    clases = db.query(Clase).order_by(Clase.nombre).all()
    rubricas = db.query(Rubrica).order_by(Rubrica.id).all()
    reportes = db.query(Reporte).order_by(Reporte.fecha.desc()).limit(30).all()

    return templates.TemplateResponse(request, "reportes/index.html", {
        "active_tab": "reportes",
        "cursos": cursos,
        "clases": clases,
        "rubricas": rubricas,
        "reportes": reportes,
        "curso_sel": cursos[0] if cursos else None,
        "clase_sel": clases[0] if clases else None,
        "rubrica_sel": rubricas[0] if rubricas else None,
        "estudiante_actual": None,
        "fecha_hoy": date.today().isoformat(),
        "vista_activa": "historial"
    })

@router.get("/historial-tabla", response_class=HTMLResponse)
def historial_tabla(
    request: Request,
    curso_id: str = "",
    clase_id: str = "",
    q: str = "",
    db: Session = Depends(get_db)
):
    query = db.query(Reporte)

    if curso_id and curso_id.isdigit():
        query = query.filter(Reporte.curso_id == int(curso_id))

    if clase_id and clase_id.isdigit():
        query = query.filter(Reporte.clase_id == int(clase_id))

    if q:
        q_clean = f"%{q.strip()}%"
        query = query.join(Reporte.estudiante).filter(
            (Reporte.texto_original.ilike(q_clean)) |
            (Estudiante.nombres.ilike(q_clean)) |
            (Estudiante.apellidos.ilike(q_clean))
        )

    reportes = query.order_by(Reporte.fecha.desc()).limit(40).all()

    return templates.TemplateResponse(request, "reportes/historial_tabla.html", {
        "reportes": reportes
    })

@router.get("/modal-detalle/{reporte_id}", response_class=HTMLResponse)
def modal_detalle_reporte(reporte_id: int, request: Request, db: Session = Depends(get_db)):
    rep = db.query(Reporte).filter_by(id=reporte_id).first()
    dimensiones_info = []
    if rep:
        dim_map = {}
        if rep.rubrica and rep.rubrica.dimensiones:
            dim_map = {d.clave: d.nombre for d in rep.rubrica.dimensiones}
        for k, v in rep.calificaciones_dimensiones.items():
            dimensiones_info.append({
                "clave": k,
                "nombre": dim_map.get(k, k.replace("_", " ").title()),
                "nota": float(v)
            })

    return templates.TemplateResponse(request, "reportes/modal_detalle.html", {
        "reporte": rep,
        "dimensiones_info": dimensiones_info
    })

@router.get("/modal-editar/{reporte_id}", response_class=HTMLResponse)
def modal_editar_reporte(reporte_id: int, request: Request, db: Session = Depends(get_db)):
    rep = db.query(Reporte).filter_by(id=reporte_id).first()
    dimensiones_info = []
    if rep:
        dim_map = {}
        if rep.rubrica and rep.rubrica.dimensiones:
            dim_map = {d.clave: d.nombre for d in rep.rubrica.dimensiones}
            for d in rep.rubrica.dimensiones:
                current_val = float(rep.calificaciones_dimensiones.get(d.clave, 3.5))
                dimensiones_info.append({
                    "clave": d.clave,
                    "nombre": d.nombre,
                    "nota": current_val
                })
        else:
            for k, v in rep.calificaciones_dimensiones.items():
                dimensiones_info.append({
                    "clave": k,
                    "nombre": k.replace("_", " ").title(),
                    "nota": float(v)
                })

    return templates.TemplateResponse(request, "reportes/modal_editar.html", {
        "reporte": rep,
        "dimensiones_info": dimensiones_info
    })

@router.post("/{reporte_id}/editar", response_class=HTMLResponse)
async def guardar_edicion_reporte(reporte_id: int, request: Request, db: Session = Depends(get_db)):
    rep = db.query(Reporte).filter_by(id=reporte_id).first()
    if not rep:
        return HTMLResponse("Reporte no encontrado", status_code=404)

    form_data = await request.form()
    texto_original = form_data.get("texto_original", "").strip()
    fecha_str = form_data.get("fecha", date.today().isoformat())

    rep.texto_original = texto_original
    rep.texto_anonimizado = PrivacyService.anonimizar_texto(texto_original, rep.estudiante)
    try:
        rep.fecha = date.fromisoformat(fecha_str)
    except Exception:
        pass

    nuevas_calificaciones = dict(rep.calificaciones_dimensiones)
    for key, value in form_data.items():
        if key.startswith("dim_"):
            clave_dim = key.replace("dim_", "")
            try:
                nuevas_calificaciones[clave_dim] = float(value)
            except ValueError:
                pass

    rep.calificaciones_dimensiones = nuevas_calificaciones
    db.commit()

    reportes = db.query(Reporte).order_by(Reporte.fecha.desc()).limit(40).all()
    return templates.TemplateResponse(request, "reportes/historial_tabla.html", {
        "reportes": reportes
    })

@router.delete("/{reporte_id}", response_class=HTMLResponse)
def eliminar_reporte(reporte_id: int, request: Request, db: Session = Depends(get_db)):
    rep = db.query(Reporte).filter_by(id=reporte_id).first()
    if rep:
        db.delete(rep)
        db.commit()

    reportes = db.query(Reporte).order_by(Reporte.fecha.desc()).limit(40).all()
    return templates.TemplateResponse(request, "reportes/historial_tabla.html", {
        "reportes": reportes
    })

@router.get("/modo-rafaga", response_class=HTMLResponse)
def modo_rafaga(
    request: Request,
    curso_id: str = "",
    clase_id: str = "",
    rubrica_id: str = "",
    fecha: str = "",
    index: int = 0,
    db: Session = Depends(get_db)
):
    if not curso_id or not curso_id.isdigit():
        return HTMLResponse("<div class='card'>Seleccione un curso valido para iniciar.</div>")

    c_id = int(curso_id)
    curso = db.query(Curso).filter_by(id=c_id).first()
    clase = db.query(Clase).filter_by(id=int(clase_id)).first() if clase_id and clase_id.isdigit() else db.query(Clase).first()
    rubrica = db.query(Rubrica).filter_by(id=int(rubrica_id)).first() if rubrica_id and rubrica_id.isdigit() else None

    estudiantes = db.query(Estudiante).join(Estudiante.cursos).filter(
        Curso.id == c_id,
        Estudiante.activo == True
    ).order_by(Estudiante.apellidos).all()

    total = len(estudiantes)
    if total == 0:
        return HTMLResponse("<div class='card'>No hay estudiantes en este curso.</div>")

    if index >= total:
        return HTMLResponse(f"""
        <div class='card' style='text-align: center; padding: 3rem;'>
          <span class='resultado-badge acuerdo' style='font-size: 1rem;'>Sesion de Reportes Completada</span>
          <h2 style='color: var(--c-blue-dark); margin-top: 1rem;'>Se han evaluado todos los estudiantes de {curso.nombre}</h2>
          <p style='color: var(--text-muted);'>Puede reiniciar la secuencia o dirigirse a la pestana de Informes para ver la evolucion.</p>
          <button class='primary' onclick='location.reload()'>Reiniciar Sesion</button>
        </div>
        """)

    index_actual = max(0, index)
    estudiante = estudiantes[index_actual]

    return templates.TemplateResponse(request, "reportes/tarjeta_rafaga.html", {
        "curso": curso,
        "clase": clase,
        "rubrica": rubrica,
        "estudiante": estudiante,
        "index_actual": index_actual,
        "total_estudiantes": total,
        "fecha": fecha or date.today().isoformat()
    })

@router.get("/detectar-chiclets", response_class=HTMLResponse)
def detectar_chiclets(request: Request, curso_id: int, texto: str = "", db: Session = Depends(get_db)):
    if not texto or len(texto) < 4:
        return HTMLResponse("")

    estudiantes_curso = db.query(Estudiante).join(Estudiante.cursos).filter(
        Curso.id == curso_id,
        Estudiante.activo == True
    ).all()

    menciones = PrivacyService.detectar_menciones(texto, estudiantes_curso)

    return templates.TemplateResponse(request, "components/chiclet_badge.html", {
        "menciones": menciones
    })

@router.post("/interpretar-audio", response_class=HTMLResponse)
async def interpretar_audio(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    texto_original = form_data.get("texto_original", "")
    rubrica_id = form_data.get("rubrica_id", "")
    estudiante_id = form_data.get("estudiante_id", "")

    if not rubrica_id or not rubrica_id.isdigit():
        return HTMLResponse("")

    rubrica = db.query(Rubrica).filter_by(id=int(rubrica_id)).first()
    if not rubrica:
        return HTMLResponse("")

    estudiante = db.query(Estudiante).filter_by(id=int(estudiante_id)).first() if estudiante_id else None
    texto_anon = PrivacyService.anonimizar_texto(texto_original, estudiante)

    rubrica_data = {
        "nombre": rubrica.nombre,
        "dimensiones": [
            {
                "clave": d.clave,
                "nombre": d.nombre,
                "descripcion": d.descripcion,
                "descriptor_bajo": d.descriptor_bajo,
                "descriptor_basico": d.descriptor_basico,
                "descriptor_alto": d.descriptor_alto,
                "descriptor_superior": d.descriptor_superior
            }
            for d in rubrica.dimensiones
        ]
    }

    llm = get_llm_service()
    sugerencias = llm.inferir_rubrica(texto_anon, rubrica_data)

    return templates.TemplateResponse(request, "reportes/sliders_sugeridos.html", {
        "rubrica": rubrica,
        "sugerencias": sugerencias
    })

@router.post("/guardar-avanzar", response_class=HTMLResponse)
async def guardar_y_avanzar(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()

    estudiante_id = int(form_data.get("estudiante_id"))
    curso_id = int(form_data.get("curso_id"))
    clase_id = int(form_data.get("clase_id"))
    rubrica_id_str = form_data.get("rubrica_id", "")
    rubrica_id = int(rubrica_id_str) if rubrica_id_str and rubrica_id_str.isdigit() else None
    fecha_str = form_data.get("fecha", date.today().isoformat())
    index_actual = int(form_data.get("index_actual", 0))
    texto_original = form_data.get("texto_original", "").strip()

    estudiante = db.query(Estudiante).filter_by(id=estudiante_id).first()

    calificaciones = {}
    for key, value in form_data.items():
        if key.startswith("dim_"):
            clave_dim = key.replace("dim_", "")
            try:
                calificaciones[clave_dim] = float(value)
            except ValueError:
                pass

    texto_anon = PrivacyService.anonimizar_texto(texto_original, estudiante)

    rep = Reporte(
        uuid_anonimo=estudiante.uuid_anonimo,
        estudiante_id=estudiante_id,
        curso_id=curso_id,
        clase_id=clase_id,
        rubrica_id=rubrica_id,
        fecha=date.fromisoformat(fecha_str),
        texto_original=texto_original,
        texto_anonimizado=texto_anon,
        calificaciones_dimensiones=calificaciones,
        metadata_adicional={"metodo": "MODO_RAFAGA_FASTAPI"}
    )
    db.add(rep)
    db.commit()

    return modo_rafaga(
        request=request,
        curso_id=str(curso_id),
        clase_id=str(clase_id),
        rubrica_id=str(rubrica_id) if rubrica_id else "",
        fecha=fecha_str,
        index=index_actual + 1,
        db=db
    )
