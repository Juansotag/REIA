from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from app.services.stt_service import STTService

router = APIRouter(prefix="/api/stt", tags=["Speech-to-Text"])

@router.post("/transcribe")
async def transcribir_endpoint(audio_file: UploadFile = File(...)):
    audio_bytes = await audio_file.read()
    texto = STTService.transcribir_audio(audio_bytes, audio_file.filename or "audio.webm")
    return JSONResponse({"texto": texto})
