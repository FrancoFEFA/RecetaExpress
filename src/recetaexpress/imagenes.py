import json
import urllib.parse
import requests
from pathlib import Path

from .config import IMAGES_DIR
from .prompts import PROMPT_META_IMAGEN


def generar_prompt_imagen(cliente_llm: callable, receta: dict) -> tuple[dict, dict]:
    """Usa el LLM para construir un prompt visual especializado en inglés y español."""
    ingredientes = receta.get("ingredientes_utilizados", [])
    prompt = PROMPT_META_IMAGEN.format(
        nombre=receta.get("nombre", "plato"),
        ingredientes=", ".join(ingredientes) if ingredientes else "ingredientes varios",
    )
    texto, metadata = cliente_llm(prompt, json_mode=True)
    data = json.loads(texto)
    return data, metadata


def generar_imagen_pollinations(
    prompt_en: str,
    nombre_receta: str,
    seed: int = 42,
    width: int = 1024,
    height: int = 1024,
) -> tuple[str, str]:
    """Genera imagen con Pollinations (gratuito, sin API key). Devuelve (ruta, url)."""
    safe_name = "".join(c if c.isalnum() else "_" for c in nombre_receta).lower()
    encoded = urllib.parse.quote(prompt_en)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=true"
    r = requests.get(url, timeout=120)
    r.raise_for_status()

    content_type = r.headers.get("content-type", "").lower()
    ext = "png" if "png" in content_type else "jpg"
    path = IMAGES_DIR / f"{safe_name}.{ext}"
    with open(path, "wb") as f:
        f.write(r.content)
    return str(path), url


def generar_imagen(
    cliente_llm: callable,
    receta: dict,
    provider_texto: str = "gemini",
    provider_imagen: str = "pollinations",
    seed: int = 42,
) -> dict:
    """Pipeline texto→texto→imagen: genera prompt visual y luego la imagen."""
    prompts, meta_texto = generar_prompt_imagen(cliente_llm, receta)
    prompt_en = prompts.get("prompt_en", "")
    prompt_es = prompts.get("prompt_es", "")

    if provider_imagen == "pollinations":
        path, url = generar_imagen_pollinations(prompt_en, receta.get("nombre", "plato"), seed=seed)
    else:
        raise ValueError(f"Proveedor de imagen no soportado: {provider_imagen}")

    return {
        "prompt_es": prompt_es,
        "prompt_en": prompt_en,
        "url_generacion": url,
        "ruta_imagen": path,
        "metadata_texto": meta_texto,
    }
