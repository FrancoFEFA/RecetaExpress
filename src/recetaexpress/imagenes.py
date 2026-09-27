import json
import urllib.parse

import requests

from .config import IMAGE_TIMEOUT, IMAGES_DIR
from .prompts import PROMPT_META_IMAGEN
from .utils import safe_filename

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}"


def generar_prompt_imagen(cliente_llm: callable, receta: dict) -> tuple[dict, dict]:
    """Usa el LLM para construir un prompt visual especializado en inglés y español."""
    ingredientes = receta.get("ingredientes_utilizados", [])
    prompt = PROMPT_META_IMAGEN.format(
        nombre=receta.get("nombre", "plato"),
        ingredientes=", ".join(ingredientes) if ingredientes else "ingredientes varios",
    )
    texto, metadata = cliente_llm(prompt, json_mode=True)
    return json.loads(texto), metadata


def generar_imagen(prompt_en: str, nombre_receta: str, seed: int = 42, width: int = 1024, height: int = 1024) -> str:
    """
    Descarga una imagen desde Pollinations (gratuito, sin API key) y devuelve la ruta local.

    Nota: el endpoint ignora el parámetro `model` (se verificó que `flux`, `gptimage`,
    `turbo` y `sana` devuelven un archivo byte a byte idéntico), por lo que no se
    exponen como parámetro: solo se usa el modelo por defecto del servicio.
    """
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    url = POLLINATIONS_URL.format(prompt=urllib.parse.quote(prompt_en))
    url += f"?width={width}&height={height}&seed={seed}&nologo=true"

    respuesta = requests.get(url, timeout=IMAGE_TIMEOUT)
    respuesta.raise_for_status()

    if "png" in respuesta.headers.get("content-type", "").lower():
        extension = "png"
    else:
        extension = "jpg"
    path = IMAGES_DIR / f"{safe_filename(nombre_receta)}.{extension}"
    path.write_bytes(respuesta.content)
    return str(path)
