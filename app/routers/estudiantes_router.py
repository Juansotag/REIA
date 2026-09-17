import uuid
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, Response
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Estudiante, Curso, Clase
from app.services.excel_service import ExcelService

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])
templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
def index_estudiantes(request: Request, db: Session = Depends(get_db)):
    cursos = db.query(Curso).order_by(Curso.grado).all()
    estudiantes = db.query(Estudiante).filter_by(activo=True).order_by(Estudiante.apellidos).limit(50).all()
    total = db.query(Estudiante).filter_by(activo=True).count()

    return templates.TemplateResponse(request, "estudiantes/index.html", {
        "active_tab": "estudiantes",
        "cursos": cursos,
        "estudiantes": estudiantes,
        "total_estudiantes": total
    })

@router.get("/tabla", response_class=HTMLResponse)
def tabla_estudiantes(request: Request, curso_id: str = "", q: str = "", db: Session = Depends(get_db)):
    query = db.query(Estudiante).filter_by(activo=True)

    if curso_id and curso_id.isdigit():
        query = query.join(Estudiante.cursos).filter(Curso.id == int(curso_id))

    if q:
        q_clean = f"%{q.strip()}%"
        query = query.filter(
            (Estudiante.nombres.ilike(q_clean)) |
            (Estudiante.apellidos.ilike(q_clean)) |
            (Estudiante.numero_documento.ilike(q_clean)) |
            (Estudiante.uuid_anonimo.ilike(q_clean))
        )

    estudiantes = query.order_by(Estudiante.apellidos).limit(50).all()
    return templates.TemplateResponse(request, "estudiantes/tabla.html", {
        "estudiantes": estudiantes
    })

@router.get("/modal-crear", response_class=HTMLResponse)
def modal_crear_estudiante(request: Request, db: Session = Depends(get_db)):
    cursos = db.query(Curso).order_by(Curso.grado).all()
    return templates.TemplateResponse(request, "estudiantes/modal_form.html", {
        "estudiante": None,
        "cursos": cursos
    })

@router.get("/modal-editar/{estudiante_id}", response_class=HTMLResponse)
def modal_editar_estudiante(estudiante_id: int, request: Request, db: Session = Depends(get_db)):
    est = db.query(Estudiante).filter_by(id=estudiante_id).first()
    cursos = db.query(Curso).order_by(Curso.grado).all()
    return templates.TemplateResponse(request, "estudiantes/modal_form.html", {
        "estudiante": est,
        "cursos": cursos
    })

@router.post("", response_class=HTMLResponse)
def crear_estudiante(
    request: Request,
    nombres: str = Form(...),
    apellidos: str = Form(...),
    tipo_documento: str = Form("TI"),
    numero_documento: str = Form(...),
    genero: str = Form("Masculino"),
    edad: int = Form(14),
    grado_actual: int = Form(9),
    curso_id: str = Form(""),
    acudiente_nombre: str = Form(""),
    acudiente_contacto: str = Form(""),
    db: Session = Depends(get_db)
):
    pronombre = "él" if genero == "Masculino" else "ella"
    uuid_anon = f"EST_{random_suffix()}"

    est = Estudiante(
        uuid_anonimo=uuid_anon,
        tipo_documento=tipo_documento,
        numero_documento=numero_documento,
        nombres=nombres.strip(),
        apellidos=apellidos.strip(),
        genero=genero,
        pronombre=pronombre,
        edad=edad,
        grado_actual=grado_actual,
        acudiente_nombre=acudiente_nombre.strip() or None,
        acudiente_contacto=acudiente_contacto.strip() or None
    )

    if curso_id and curso_id.isdigit():
        curso = db.query(Curso).filter_by(id=int(curso_id)).first()
        if curso:
            est.cursos.append(curso)

    db.add(est)
    db.commit()

    estudiantes = db.query(Estudiante).filter_by(activo=True).order_by(Estudiante.apellidos).limit(50).all()
    return templates.TemplateResponse(request, "estudiantes/tabla.html", {
        "estudiantes": estudiantes
    })

@router.post("/{estudiante_id}", response_class=HTMLResponse)
def editar_estudiante(
    estudiante_id: int,
    request: Request,
    nombres: str = Form(...),
    apellidos: str = Form(...),
    tipo_documento: str = Form("TI"),
    numero_documento: str = Form(...),
    genero: str = Form("Masculino"),
    edad: int = Form(14),
    grado_actual: int = Form(9),
    curso_id: str = Form(""),
    acudiente_nombre: str = Form(""),
    acudiente_contacto: str = Form(""),
    db: Session = Depends(get_db)
):
    est = db.query(Estudiante).filter_by(id=estudiante_id).first()
    if est:
        est.nombres = nombres.strip()
        est.apellidos = apellidos.strip()
        est.tipo_documento = tipo_documento
        est.numero_documento = numero_documento.strip()
        est.genero = genero
        est.pronombre = "él" if genero == "Masculino" else "ella"
        est.edad = edad
        est.grado_actual = grado_actual
        est.acudiente_nombre = acudiente_nombre.strip() or None
        est.acudiente_contacto = acudiente_contacto.strip() or None

        if curso_id and curso_id.isdigit():
            curso = db.query(Curso).filter_by(id=int(curso_id)).first()
            if curso and curso not in est.cursos:
                est.cursos = [curso]

        db.commit()

    estudiantes = db.query(Estudiante).filter_by(activo=True).order_by(Estudiante.apellidos).limit(50).all()
    return templates.TemplateResponse(request, "estudiantes/tabla.html", {
        "estudiantes": estudiantes
    })

@router.delete("/{estudiante_id}", response_class=HTMLResponse)
def eliminar_estudiante(estudiante_id: int, request: Request, db: Session = Depends(get_db)):
    est = db.query(Estudiante).filter_by(id=estudiante_id).first()
    if est:
        est.activo = False
        db.commit()

    estudiantes = db.query(Estudiante).filter_by(activo=True).order_by(Estudiante.apellidos).limit(50).all()
    return templates.TemplateResponse(request, "estudiantes/tabla.html", {
        "estudiantes": estudiantes
    })

@router.get("/modal-importar", response_class=HTMLResponse)
def modal_importar(request: Request):
    return templates.TemplateResponse(request, "estudiantes/modal_import.html", {})

@router.post("/importar", response_class=HTMLResponse)
async def importar_estudiantes(request: Request, archivo: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await archivo.read()
    registros = ExcelService.importar_estudiantes(content, archivo.filename)

    for r in registros:
        doc = r["numero_documento"]
        existente = db.query(Estudiante).filter_by(numero_documento=doc).first()
        if not existente:
            est = Estudiante(
                uuid_anonimo=f"EST_{random_suffix()}",
                tipo_documento=r["tipo_documento"],
                numero_documento=doc,
                nombres=r["nombres"],
                apellidos=r["apellidos"],
                genero=r["genero"],
                pronombre=r["pronombre"],
                edad=r["edad"],
                grado_actual=r["grado_actual"],
                acudiente_nombre=r["acudiente_nombre"] or None,
                acudiente_contacto=r["acudiente_contacto"] or None
            )
            # Asociar curso correspondiente al grado
            curso = db.query(Curso).filter_by(grado=r["grado_actual"]).first()
            if curso:
                est.cursos.append(curso)
            db.add(est)

    db.commit()

    estudiantes = db.query(Estudiante).filter_by(activo=True).order_by(Estudiante.apellidos).limit(50).all()
    return templates.TemplateResponse(request, "estudiantes/tabla.html", {
        "estudiantes": estudiantes
    })

@router.get("/exportar")
def exportar_estudiantes(db: Session = Depends(get_db)):
    estudiantes = db.query(Estudiante).filter_by(activo=True).order_by(Estudiante.grado_actual, Estudiante.apellidos).all()
    xlsx_bytes = ExcelService.exportar_estudiantes_excel(estudiantes)

    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Nomina_Estudiantes_REIA_2026.xlsx"}
    )

def random_suffix():
    return uuid.uuid4().hex[:8]
