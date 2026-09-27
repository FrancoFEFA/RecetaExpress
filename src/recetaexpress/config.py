import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
IMAGES_DIR = ROOT / "images"
AUDIO_DIR = ROOT / "audio"
PROMPTS_DIR = ROOT / "prompts"
CACHE_DIR = ROOT / "data" / "respuestas"

for d in (DATA_DIR, IMAGES_DIR, AUDIO_DIR, CACHE_DIR):
    d.mkdir(parents=True, exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODELS = ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash"]
TEMPERATURE = 0.3
MAX_RETRIES = 3
TIMEOUT = 60

# Fallback gratuito y sin API key para texto→texto (Pollinations)
POLLINATIONS_TEXT_MODEL = "openai-fast"
POLLINATIONS_TEXT_URL = "https://text.pollinations.ai/{prompt}"

# Ingredientes básicos de despensa: siempre disponibles, no se consideran faltantes.
BASICOS_DESPENSA = {"sal", "pimienta", "aceite", "agua", "azucar"}
