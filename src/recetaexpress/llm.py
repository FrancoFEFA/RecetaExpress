import json
import time
import hashlib
import requests
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types

from .config import (
    GEMINI_API_KEY,
    GEMINI_MODELS,
    TEMPERATURE,
    MAX_RETRIES,
    TIMEOUT,
    CACHE_DIR,
    POLLINATIONS_TEXT_URL,
)


def _cache_key(model: str, prompt: str, temperature: float) -> Path:
    h = hashlib.sha256(f"{model}|{temperature}|{prompt}".encode()).hexdigest()[:16]
    safe_model = model.replace("/", "_").replace(".", "_")
    return CACHE_DIR / f"{safe_model}_{h}.json"


def _load_cache(path: Path) -> Optional[dict]:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _save_cache(path: Path, data: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_text_gemini(
    prompt: str,
    model: Optional[str] = None,
    use_cache: bool = True,
    json_mode: bool = True,
) -> tuple[str, dict]:
    """Genera texto con Gemini. Usa caché, reintentos con backoff y fallback entre modelos."""
    models_to_try = [model] if model else GEMINI_MODELS
    if not models_to_try:
        raise RuntimeError("No hay modelos Gemini configurados.")

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "No se encontró GEMINI_API_KEY. Creá el archivo .env con tu key de Google AI Studio."
        )

    client = genai.Client(api_key=GEMINI_API_KEY)
    last_error = None

    for model_name in models_to_try:
        cache_path = _cache_key(model_name, prompt, TEMPERATURE)
        if use_cache:
            cached = _load_cache(cache_path)
            if cached is not None:
                return cached["text"], cached.get("metadata", {})

        for attempt in range(MAX_RETRIES):
            try:
                config = types.GenerateContentConfig(temperature=TEMPERATURE)
                if json_mode:
                    config.response_mime_type = "application/json"
                start = time.time()
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config,
                )
                latency = time.time() - start
                text = response.text
                metadata = {
                    "model": model_name,
                    "temperature": TEMPERATURE,
                    "latency_seconds": round(latency, 3),
                    "prompt_chars": len(prompt),
                    "provider": "gemini",
                }
                if use_cache:
                    _save_cache(cache_path, {"text": text, "metadata": metadata})
                return text, metadata
            except Exception as e:
                last_error = e
                # Si el modelo no existe o está saturado, pasar al siguiente sin esperar mucho
                if "UNAVAILABLE" in str(e) or "not found" in str(e).lower():
                    time.sleep(1)
                else:
                    time.sleep(2 ** attempt)

    raise RuntimeError(
        f"Fallaron todos los intentos con Gemini ({models_to_try}): {last_error}"
    )


def generate_text_pollinations(prompt: str) -> tuple[str, dict]:
    """Fallback 100% gratuito y sin API key usando Pollinations (modelo openai-fast)."""
    cache_path = _cache_key("pollinations_openai_fast", prompt, 0)
    cached = _load_cache(cache_path)
    if cached is not None:
        return cached["text"], cached.get("metadata", {})

    encoded = requests.utils.quote(prompt)
    url = POLLINATIONS_TEXT_URL.format(prompt=encoded)
    r = requests.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    text = r.text
    metadata = {
        "model": "pollinations/openai-fast",
        "provider": "pollinations",
        "latency_seconds": None,
    }
    _save_cache(cache_path, {"text": text, "metadata": metadata})
    return text, metadata


def generate_text(prompt: str, provider: str = "gemini", **kwargs) -> tuple[str, dict]:
    """Punto de entrada unificado. provider puede ser 'gemini' o 'pollinations'."""
    if provider == "gemini":
        return generate_text_gemini(prompt, **kwargs)
    if provider == "pollinations":
        return generate_text_pollinations(prompt)
    raise ValueError(f"Proveedor desconocido: {provider}")
