from app.routers.estudiantes_router import router as estudiantes_router
from app.routers.cursos_clases_router import router as cursos_clases_router
from app.routers.rubricas_router import router as rubricas_router
from app.routers.reportes_router import router as reportes_router
from app.routers.informes_router import router as informes_router
from app.routers.configuracion_router import router as configuracion_router
from app.routers.stt_router import router as stt_router

__all__ = [
    "estudiantes_router",
    "cursos_clases_router",
    "rubricas_router",
    "reportes_router",
    "informes_router",
    "configuracion_router",
    "stt_router"
]
