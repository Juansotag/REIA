from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Curso, Clase, Estudiante

router = APIRouter(prefix="/cursos-clases", tags=["Cursos y Clases"])
templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
def index_cursos_clases(request: Request, curso_id: str = "", db: Session = Depends(get_db)):
    cursos = db.query(Curso).order_by(Curso.grado, Curso.seccion).all()
    clases = db.query(Clase).order_by(Clase.nombre).all()

    curso_activo = None
    estudiantes_curso = []

    if curso_id and curso_id.isdigit():
        curso_activo = db.query(Curso).filter_by(id=int(curso_id)).first()
    elif cursos:
        curso_activo = cursos[0]

    if curso_activo:
        estudiantes_curso = db.query(Estudiante).join(Estudiante.cursos).filter(
            Curso.id == curso_activo.id,
            Estudiante.activo == True
        ).order_by(Estudiante.apellidos).all()

    return templates.TemplateResponse(request, "cursos_clases/index.html", {
        "active_tab": "cursos_clases",
        "cursos": cursos,
        "clases": clases,
        "curso_activo": curso_activo,
        "estudiantes_curso": estudiantes_curso
    })

# --- CRUD CURSOS ---

@router.get("/modal-curso", response_class=HTMLResponse)
def modal_nuevo_curso(request: Request):
    return templates.TemplateResponse(request, "cursos_clases/modal_curso.html", {
        "curso": None
    })

@router.get("/modal-curso/{curso_id}", response_class=HTMLResponse)
def modal_editar_curso(curso_id: int, request: Request, db: Session = Depends(get_db)):
    curso = db.query(Curso).filter_by(id=curso_id).first()
    return templates.TemplateResponse(request, "cursos_clases/modal_curso.html", {
        "curso": curso
    })

@router.post("/curso")
def crear_curso(
    nombre: str = Form(...),
    grado: int = Form(...),
    seccion: str = Form(...),
    director_curso: str = Form(""),
    anio_lectivo: int = Form(2026),
    db: Session = Depends(get_db)
):
    nuevo_curso = Curso(
        nombre=nombre.strip(),
        grado=grado,
        seccion=seccion.strip().upper(),
        director_curso=director_curso.strip(),
        anio_lectivo=anio_lectivo
    )
    db.add(nuevo_curso)
    db.commit()
    db.refresh(nuevo_curso)
    return RedirectResponse(url=f"/cursos-clases?curso_id={nuevo_curso.id}", status_code=303)

@router.post("/curso/{curso_id}")
def actualizar_curso(
    curso_id: int,
    nombre: str = Form(...),
    grado: int = Form(...),
    seccion: str = Form(...),
    director_curso: str = Form(""),
    anio_lectivo: int = Form(2026),
    db: Session = Depends(get_db)
):
    curso = db.query(Curso).filter_by(id=curso_id).first()
    if curso:
        curso.nombre = nombre.strip()
        curso.grado = grado
        curso.seccion = seccion.strip().upper()
        curso.director_curso = director_curso.strip()
        curso.anio_lectivo = anio_lectivo
        db.commit()
    return RedirectResponse(url=f"/cursos-clases?curso_id={curso_id}", status_code=303)

@router.delete("/curso/{curso_id}")
def eliminar_curso(curso_id: int, db: Session = Depends(get_db)):
    curso = db.query(Curso).filter_by(id=curso_id).first()
    if curso:
        db.delete(curso)
        db.commit()
    return RedirectResponse(url="/cursos-clases", status_code=303)

# --- CRUD CLASES / ASIGNATURAS ---

@router.get("/modal-clase", response_class=HTMLResponse)
def modal_nueva_clase(request: Request):
    return templates.TemplateResponse(request, "cursos_clases/modal_clase.html", {
        "clase": None
    })

@router.get("/modal-clase/{clase_id}", response_class=HTMLResponse)
def modal_editar_clase(clase_id: int, request: Request, db: Session = Depends(get_db)):
    clase = db.query(Clase).filter_by(id=clase_id).first()
    return templates.TemplateResponse(request, "cursos_clases/modal_clase.html", {
        "clase": clase
    })

@router.post("/clase")
def crear_clase(
    nombre: str = Form(...),
    area: str = Form(...),
    descripcion: str = Form(""),
    db: Session = Depends(get_db)
):
    nueva_clase = Clase(
        nombre=nombre.strip(),
        area=area.strip(),
        descripcion=descripcion.strip()
    )
    db.add(nueva_clase)
    db.commit()
    return RedirectResponse(url="/cursos-clases", status_code=303)

@router.post("/clase/{clase_id}")
def actualizar_clase(
    clase_id: int,
    nombre: str = Form(...),
    area: str = Form(...),
    descripcion: str = Form(""),
    db: Session = Depends(get_db)
):
    clase = db.query(Clase).filter_by(id=clase_id).first()
    if clase:
        clase.nombre = nombre.strip()
        clase.area = area.strip()
        clase.descripcion = descripcion.strip()
        db.commit()
    return RedirectResponse(url="/cursos-clases", status_code=303)

@router.delete("/clase/{clase_id}")
def eliminar_clase(clase_id: int, db: Session = Depends(get_db)):
    clase = db.query(Clase).filter_by(id=clase_id).first()
    if clase:
        db.delete(clase)
        db.commit()
    return RedirectResponse(url="/cursos-clases", status_code=303)

# --- GESTIÓN DE ESTUDIANTES EN CURSOS ---

@router.get("/curso/{curso_id}/modal-estudiantes", response_class=HTMLResponse)
def modal_estudiantes_curso(curso_id: int, request: Request, db: Session = Depends(get_db)):
    curso = db.query(Curso).filter_by(id=curso_id).first()
    todos_estudiantes = db.query(Estudiante).filter_by(activo=True).order_by(Estudiante.apellidos).all()
    matriculados_ids = {e.id for e in curso.estudiantes} if curso else set()

    return templates.TemplateResponse(request, "cursos_clases/modal_estudiantes_curso.html", {
        "curso": curso,
        "todos_estudiantes": todos_estudiantes,
        "matriculados_ids": matriculados_ids
    })

@router.post("/curso/{curso_id}/estudiantes")
async def guardar_estudiantes_curso(curso_id: int, request: Request, db: Session = Depends(get_db)):
    curso = db.query(Curso).filter_by(id=curso_id).first()
    if not curso:
        return RedirectResponse(url="/cursos-clases", status_code=303)

    form_data = await request.form()
    ids_raw = form_data.getlist("estudiante_ids[]")
    ids = [int(x) for x in ids_raw if x and x.isdigit()]

    nuevos_estudiantes = db.query(Estudiante).filter(Estudiante.id.in_(ids)).all() if ids else []
    curso.estudiantes = nuevos_estudiantes
    db.commit()

    return RedirectResponse(url=f"/cursos-clases?curso_id={curso.id}", status_code=303)

@router.delete("/curso/{curso_id}/estudiante/{estudiante_id}")
def remover_estudiante_curso(curso_id: int, estudiante_id: int, db: Session = Depends(get_db)):
    curso = db.query(Curso).filter_by(id=curso_id).first()
    est = db.query(Estudiante).filter_by(id=estudiante_id).first()
    if curso and est and est in curso.estudiantes:
        curso.estudiantes.remove(est)
        db.commit()
    return RedirectResponse(url=f"/cursos-clases?curso_id={curso_id}", status_code=303)

# --- GESTIÓN DE ESTUDIANTES EN CLASES / ASIGNATURAS ---

@router.get("/clase/{clase_id}/modal-estudiantes", response_class=HTMLResponse)
def modal_estudiantes_clase(clase_id: int, request: Request, db: Session = Depends(get_db)):
    clase = db.query(Clase).filter_by(id=clase_id).first()
    todos_estudiantes = db.query(Estudiante).filter_by(activo=True).order_by(Estudiante.apellidos).all()
    matriculados_ids = {e.id for e in clase.estudiantes} if clase else set()

    return templates.TemplateResponse(request, "cursos_clases/modal_estudiantes_clase.html", {
        "clase": clase,
        "todos_estudiantes": todos_estudiantes,
        "matriculados_ids": matriculados_ids
    })

@router.post("/clase/{clase_id}/estudiantes")
async def guardar_estudiantes_clase(clase_id: int, request: Request, db: Session = Depends(get_db)):
    clase = db.query(Clase).filter_by(id=clase_id).first()
    if not clase:
        return RedirectResponse(url="/cursos-clases", status_code=303)

    form_data = await request.form()
    ids_raw = form_data.getlist("estudiante_ids[]")
    ids = [int(x) for x in ids_raw if x and x.isdigit()]

    nuevos_estudiantes = db.query(Estudiante).filter(Estudiante.id.in_(ids)).all() if ids else []
    clase.estudiantes = nuevos_estudiantes
    db.commit()

    return RedirectResponse(url="/cursos-clases", status_code=303)


