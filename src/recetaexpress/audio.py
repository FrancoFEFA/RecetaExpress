import asyncio

import edge_tts

from .config import AUDIO_DIR
from .utils import safe_filename

VOZ = "es-AR-ElenaNeural"


async def _generar_async(texto: str, voz: str, salida: str) -> None:
    await edge_tts.Communicate(texto, voz).save(salida)


def generar_audio(texto: str, nombre_base: str) -> str:
    """Genera un MP3 con la narración de una receta. No requiere API key."""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    path = AUDIO_DIR / f"{safe_filename(nombre_base)}.mp3"
    asyncio.run(_generar_async(texto, VOZ, str(path)))
    return str(path)
