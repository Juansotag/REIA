from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Estudiante, Curso, Clase, Rubrica, Reporte, InformeGenerado

router = APIRouter(tags=["Landing y Tutorial"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
@router.get("/inicio", response_class=HTMLResponse)
@router.get("/tutorial", response_class=HTMLResponse)
def landing_page(request: Request, db: Session = Depends(get_db)):
    total_estudiantes = db.query(Estudiante).filter_by(activo=True).count()
    total_cursos = db.query(Curso).count()
    total_rubricas = db.query(Rubrica).count()
    total_reportes = db.query(Reporte).count()
    total_informes = db.query(InformeGenerado).count()

    return templates.TemplateResponse(request, "landing.html", {
        "active_tab": "inicio",
        "stats": {
            "estudiantes": total_estudiantes,
            "cursos": total_cursos,
            "rubricas": total_rubricas,
            "reportes": total_reportes,
            "informes": total_informes
        }
    })
