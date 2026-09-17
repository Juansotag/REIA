"""
Servicio de Speech-to-Text (STT) para REIA.
GovLab: Universidad de la Sabana.
Gestiona el respaldo de transcripción de audio mediante OpenAI Whisper en backend.
"""

import os
import io

class STTService:

    @staticmethod
    def transcribir_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return "Grabación procesada localmente (Configure OPENAI_API_KEY en .env para transcripción Whisper en backend)."

        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = filename

            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="es"
            )
            return transcript.text
        except Exception as e:
            print(f"[STTService] Error en Whisper: {e}")
            return f"Error al procesar audio en Whisper: {str(e)}"
