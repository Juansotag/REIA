import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.database import init_db
from app.routers import (
    estudiantes_router,
    cursos_clases_router,
    rubricas_router,
    reportes_router,
    informes_router,
    configuracion_router,
    stt_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialización de la base de datos al arrancar
    init_db()
    yield

app = FastAPI(
    title="REIA: Realimentación Estudiantil con Inteligencia Artificial",
    description="Herramienta del GovLab de la Universidad de la Sabana para la construcción ágil y privada de reportes formativos.",
    version="1.0.0",
    lifespan=lifespan
)

# Montar archivos estáticos (CSS, fuentes, imágenes, scripts)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir routers de la aplicación
app.include_router(estudiantes_router)
app.include_router(cursos_clases_router)
app.include_router(rubricas_router)
app.include_router(reportes_router)
app.include_router(informes_router)
app.include_router(configuracion_router)
app.include_router(stt_router)

@app.get("/")
def ruta_raiz():
    return RedirectResponse(url="/reportes")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
