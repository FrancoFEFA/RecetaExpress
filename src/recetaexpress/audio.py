import asyncio
from pathlib import Path
import edge_tts
from unidecode import unidecode

from .config import AUDIO_DIR


def _safe_name(nombre: str) -> str:
    normalizado = unidecode(nombre)
    return "".join(c if c.isalnum() else "_" for c in normalizado).lower()


async def _generar_async(texto: str, voz: str, salida: str):
    communicate = edge_tts.Communicate(texto, voz)
    await communicate.save(salida)


def generar_audio(texto: str, nombre_base: str, voz: str = "es-AR-ElenaNeural") -> str:
    """Genera un archivo MP3 con la narración de una receta. No requiere API key."""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    safe = _safe_name(nombre_base)
    path = AUDIO_DIR / f"{safe}.mp3"
    asyncio.run(_generar_async(texto, voz, str(path)))
    return str(path)
