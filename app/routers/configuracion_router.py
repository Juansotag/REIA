import os
from dotenv import load_dotenv, set_key
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

load_dotenv()

router = APIRouter(prefix="/configuracion", tags=["Configuración"])
templates = Jinja2Templates(directory="templates")

def enmascarar_key(key: str) -> str:
    if not key or len(key.strip()) < 8:
        return ""
    k = key.strip()
    return f"{k[:7]}••••••••••••••••{k[-4:]}"

@router.get("", response_class=HTMLResponse)
def index_configuracion(request: Request):
    load_dotenv(override=True)
    openai_raw = os.getenv("OPENAI_API_KEY", "").strip()
    anthropic_raw = os.getenv("ANTHROPIC_API_KEY", "").strip()

    return templates.TemplateResponse(request, "configuracion/index.html", {
        "active_tab": "configuracion",
        "llm_provider": os.getenv("LLM_PROVIDER_DEFAULT", "openai"),
        "openai_configurada": bool(openai_raw),
        "openai_mask": enmascarar_key(openai_raw),
        "anthropic_configurada": bool(anthropic_raw),
        "anthropic_mask": enmascarar_key(anthropic_raw),
        "stt_engine": os.getenv("STT_DEFAULT_ENGINE", "hybrid")
    })

@router.post("/guardar", response_class=HTMLResponse)
def guardar_configuracion(
    llm_provider: str = Form("openai"),
    openai_api_key: str = Form(""),
    anthropic_api_key: str = Form(""),
    stt_engine: str = Form("hybrid")
):
    load_dotenv(override=True)
    env_path = os.path.join(os.getcwd(), ".env")

    os.environ["LLM_PROVIDER_DEFAULT"] = llm_provider
    os.environ["STT_DEFAULT_ENGINE"] = stt_engine
    try:
        set_key(env_path, "LLM_PROVIDER_DEFAULT", llm_provider)
        set_key(env_path, "STT_DEFAULT_ENGINE", stt_engine)
    except Exception as e:
        print(f"Error guardando LLM/STT en .env: {e}")

    # Solo actualizar OpenAI si el usuario ingresó una nueva clave
    nueva_openai = openai_api_key.strip()
    if nueva_openai:
        if nueva_openai.upper() in ["DELETE", "BORRAR", "ELIMINAR"]:
            os.environ["OPENAI_API_KEY"] = ""
            try:
                set_key(env_path, "OPENAI_API_KEY", "")
            except Exception:
                pass
        else:
            os.environ["OPENAI_API_KEY"] = nueva_openai
            try:
                set_key(env_path, "OPENAI_API_KEY", nueva_openai)
            except Exception:
                pass

    # Solo actualizar Anthropic si el usuario ingresó una nueva clave
    nueva_anthropic = anthropic_api_key.strip()
    if nueva_anthropic:
        if nueva_anthropic.upper() in ["DELETE", "BORRAR", "ELIMINAR"]:
            os.environ["ANTHROPIC_API_KEY"] = ""
            try:
                set_key(env_path, "ANTHROPIC_API_KEY", "")
            except Exception:
                pass
        else:
            os.environ["ANTHROPIC_API_KEY"] = nueva_anthropic
            try:
                set_key(env_path, "ANTHROPIC_API_KEY", nueva_anthropic)
            except Exception:
                pass

    return HTMLResponse("<span class='save-status success'>Configuración guardada de forma segura en .env y protegida contra exposición.</span>")

