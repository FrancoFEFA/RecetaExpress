import json
import urllib.parse
import requests
import time
from pathlib import Path
from typing import List, Tuple
from unidecode import unidecode

from .config import IMAGES_DIR
from .prompts import PROMPT_META_IMAGEN

# Modelos de Pollinations ordenados por preferencia de calidad.
# Todos fueron verificados como funcionales sin API key.
MODELOS_POLLINATIONS = ["flux", "gptimage", "turbo", "sana"]


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


def _safe_name(nombre: str) -> str:
    # Normaliza a ASCII para nombres de archivo portables y predecibles
    normalizado = unidecode(nombre)
    return "".join(c if c.isalnum() else "_" for c in normalizado).lower()


def generar_imagen_pollinations(
    prompt_en: str,
    nombre_receta: str,
    seed: int = 42,
    width: int = 1024,
    height: int = 1024,
    modelo: str = "flux",
) -> tuple[str, str]:
    """Genera imagen con Pollinations (gratuito, sin API key). Devuelve (ruta, url)."""
    safe_name = _safe_name(nombre_receta)
    encoded = urllib.parse.quote(prompt_en)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&seed={seed}&nologo=true&model={modelo}"
    )
    r = requests.get(url, timeout=180)
    r.raise_for_status()

    content_type = r.headers.get("content-type", "").lower()
    ext = "png" if "png" in content_type else "jpg"
    path = IMAGES_DIR / f"{safe_name}.{ext}"
    with open(path, "wb") as f:
        f.write(r.content)
    return str(path), url


def generar_imagen_con_fallback(
    prompt_en: str,
    nombre_receta: str,
    seed: int = 42,
    width: int = 1024,
    height: int = 1024,
    modelos: List[str] = None,
) -> tuple[str, str, str]:
    """
    Intenta generar la imagen con varios modelos en orden hasta que uno funcione.
    Devuelve (ruta, url, modelo_usado).
    """
    modelos = modelos or MODELOS_POLLINATIONS
    last_error = None
    for modelo in modelos:
        try:
            path, url = generar_imagen_pollinations(
                prompt_en, nombre_receta, seed=seed, width=width, height=height, modelo=modelo
            )
            return path, url, modelo
        except Exception as e:
            last_error = e
            time.sleep(1)
    raise RuntimeError(
        f"No se pudo generar imagen con ningún modelo ({modelos}): {last_error}"
    )


def generar_comparativa_modelos(
    prompt_en: str,
    nombre_receta: str,
    seed: int = 42,
    modelos: List[str] = ("sana", "flux", "gptimage"),
    width: int = 512,
    height: int = 512,
) -> List[dict]:
    """Genera la misma imagen con varios modelos para comparar calidad."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    comparativa_dir = IMAGES_DIR / "comparativa"
    comparativa_dir.mkdir(exist_ok=True)

    resultados = []
    for modelo in modelos:
        try:
            path, url = generar_imagen_pollinations(
                prompt_en, f"{nombre_receta}_{modelo}", seed=seed,
                width=width, height=height, modelo=modelo,
            )
            # Mover a carpeta comparativa con nombre limpio (sobrescribe si ya existe)
            dest = comparativa_dir / f"{_safe_name(nombre_receta)}_{modelo}.jpg"
            Path(path).replace(dest)
            resultados.append({
                "modelo": modelo,
                "ruta": str(dest),
                "url": url,
                "tamano_bytes": dest.stat().st_size,
            })
        except Exception as e:
            resultados.append({
                "modelo": modelo,
                "ruta": None,
                "url": None,
                "error": str(e),
            })
    return resultados


def generar_imagen(
    cliente_llm: callable,
    receta: dict,
    provider_texto: str = "gemini",
    provider_imagen: str = "pollinations",
    seed: int = 42,
    width: int = 1024,
    height: int = 1024,
    modelo: str = "flux",
) -> dict:
    """Pipeline texto→texto→imagen: genera prompt visual y luego la imagen."""
    prompts, meta_texto = generar_prompt_imagen(cliente_llm, receta)
    prompt_en = prompts.get("prompt_en", "")
    prompt_es = prompts.get("prompt_es", "")

    if provider_imagen == "pollinations":
        # Cadena de fallback: primero el modelo pedido, luego el resto en orden de calidad
        cadena = [modelo] if modelo else []
        cadena += [m for m in MODELOS_POLLINATIONS if m not in cadena]
        path, url, modelo_usado = generar_imagen_con_fallback(
            prompt_en,
            receta.get("nombre", "plato"),
            seed=seed,
            width=width,
            height=height,
            modelos=cadena,
        )
    else:
        raise ValueError(f"Proveedor de imagen no soportado: {provider_imagen}")

    return {
        "prompt_es": prompt_es,
        "prompt_en": prompt_en,
        "url_generacion": url,
        "ruta_imagen": path,
        "modelo_imagen": modelo_usado,
        "metadata_texto": meta_texto,
    }
