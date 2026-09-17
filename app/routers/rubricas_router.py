from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Rubrica, DimensionRubrica, Clase

router = APIRouter(prefix="/rubricas", tags=["Rúbricas"])
templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
def index_rubricas(request: Request, db: Session = Depends(get_db)):
    rubricas = db.query(Rubrica).order_by(Rubrica.id).all()
    return templates.TemplateResponse(request, "rubricas/index.html", {
        "active_tab": "rubricas",
        "rubricas": rubricas
    })

@router.get("/modal-crear", response_class=HTMLResponse)
def modal_crear_rubrica(request: Request, db: Session = Depends(get_db)):
    clases = db.query(Clase).order_by(Clase.nombre).all()
    return templates.TemplateResponse(request, "rubricas/modal_rubrica.html", {
        "rubrica": None,
        "clases": clases
    })

@router.get("/modal-editar/{rubrica_id}", response_class=HTMLResponse)
def modal_editar_rubrica(rubrica_id: int, request: Request, db: Session = Depends(get_db)):
    rub = db.query(Rubrica).filter_by(id=rubrica_id).first()
    clases = db.query(Clase).order_by(Clase.nombre).all()
    return templates.TemplateResponse(request, "rubricas/modal_rubrica.html", {
        "rubrica": rub,
        "clases": clases
    })

@router.post("")
async def crear_rubrica(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    nombre = form_data.get("nombre", "").strip()
    descripcion = form_data.get("descripcion", "").strip()
    tipo_escala = form_data.get("tipo_escala", "CONTINUA")
    clase_id_str = form_data.get("clase_id", "")
    clase_id = int(clase_id_str) if clase_id_str and clase_id_str.isdigit() else None

    rub = Rubrica(
        nombre=nombre,
        descripcion=descripcion,
        clase_id=clase_id,
        escala_min=0.0 if tipo_escala == "CONTINUA" else 1.0,
        escala_max=5.0,
        tipo_escala=tipo_escala
    )
    db.add(rub)
    db.flush()

    nombres = form_data.getlist("dim_nombre[]")
    claves = form_data.getlist("dim_clave[]")
    pesos = form_data.getlist("dim_peso[]")
    bajos = form_data.getlist("dim_bajo[]")
    basicos = form_data.getlist("dim_basico[]")
    altos = form_data.getlist("dim_alto[]")
    superiores = form_data.getlist("dim_superior[]")

    for i in range(len(nombres)):
        if nombres[i].strip():
            clave_val = claves[i].strip() if i < len(claves) and claves[i].strip() else f"dim_{i+1}"
            peso_val = float(pesos[i]) if i < len(pesos) and pesos[i] else 0.0
            dim = DimensionRubrica(
                rubrica_id=rub.id,
                nombre=nombres[i].strip(),
                clave=clave_val,
                peso_porcentual=peso_val,
                descriptor_bajo=bajos[i].strip() if i < len(bajos) else None,
                descriptor_basico=basicos[i].strip() if i < len(basicos) else None,
                descriptor_alto=altos[i].strip() if i < len(altos) else None,
                descriptor_superior=superiores[i].strip() if i < len(superiores) else None
            )
            db.add(dim)

    db.commit()
    return RedirectResponse(url="/rubricas", status_code=303)

@router.post("/{rubrica_id}")
async def actualizar_rubrica(rubrica_id: int, request: Request, db: Session = Depends(get_db)):
    rub = db.query(Rubrica).filter_by(id=rubrica_id).first()
    if not rub:
        return RedirectResponse(url="/rubricas", status_code=303)

    form_data = await request.form()
    rub.nombre = form_data.get("nombre", "").strip()
    rub.descripcion = form_data.get("descripcion", "").strip()
    rub.tipo_escala = form_data.get("tipo_escala", "CONTINUA")
    rub.escala_min = 0.0 if rub.tipo_escala == "CONTINUA" else 1.0
    rub.escala_max = 5.0
    clase_id_str = form_data.get("clase_id", "")
    rub.clase_id = int(clase_id_str) if clase_id_str and clase_id_str.isdigit() else None

    # Eliminar dimensiones previas y recrear
    db.query(DimensionRubrica).filter_by(rubrica_id=rub.id).delete()

    nombres = form_data.getlist("dim_nombre[]")
    claves = form_data.getlist("dim_clave[]")
    pesos = form_data.getlist("dim_peso[]")
    bajos = form_data.getlist("dim_bajo[]")
    basicos = form_data.getlist("dim_basico[]")
    altos = form_data.getlist("dim_alto[]")
    superiores = form_data.getlist("dim_superior[]")

    for i in range(len(nombres)):
        if nombres[i].strip():
            clave_val = claves[i].strip() if i < len(claves) and claves[i].strip() else f"dim_{i+1}"
            peso_val = float(pesos[i]) if i < len(pesos) and pesos[i] else 0.0
            dim = DimensionRubrica(
                rubrica_id=rub.id,
                nombre=nombres[i].strip(),
                clave=clave_val,
                peso_porcentual=peso_val,
                descriptor_bajo=bajos[i].strip() if i < len(bajos) else None,
                descriptor_basico=basicos[i].strip() if i < len(basicos) else None,
                descriptor_alto=altos[i].strip() if i < len(altos) else None,
                descriptor_superior=superiores[i].strip() if i < len(superiores) else None
            )
            db.add(dim)

    db.commit()
    return RedirectResponse(url="/rubricas", status_code=303)

@router.delete("/{rubrica_id}")
def eliminar_rubrica(rubrica_id: int, db: Session = Depends(get_db)):
    rub = db.query(Rubrica).filter_by(id=rubrica_id).first()
    if rub:
        db.delete(rub)
        db.commit()
    return RedirectResponse(url="/rubricas", status_code=303)

