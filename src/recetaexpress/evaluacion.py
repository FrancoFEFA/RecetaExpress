import json
from typing import List, Dict, Any

import pandas as pd
import matplotlib.pyplot as plt

from .config import IMAGES_DIR
from .recetas import normalizar_ingrediente, ingredientes_a_canonical


def metricas_objetivas(
    respuesta_validada: Dict[str, List[Dict]],
    disponibles: List[str],
    catalogo: List[dict],
    basicos: set,
) -> Dict[str, Any]:
    """Métricas determinísticas y reproducibles sobre la respuesta del modelo."""
    disponibles_can = set(ingredientes_a_canonical(disponibles, catalogo))
    basicos_can = {normalizar_ingrediente(b) for b in basicos}
    permitidos = disponibles_can | basicos_can

    recetas = []
    for cat in respuesta_validada.values():
        recetas.extend(cat)

    if not recetas:
        return {"n_recetas": 0}

    campos_obligatorios = [
        "nombre",
        "descripcion",
        "ingredientes_utilizados",
        "ingredientes_faltantes",
        "tiempo",
        "dificultad",
        "aprovechamiento",
    ]
    estructura_ok = all(
        all(k in r for k in campos_obligatorios) for r in recetas
    )

    inventados = 0
    for r in recetas:
        todos = set(r.get("ingredientes_utilizados", [])) | set(
            r.get("ingredientes_faltantes", [])
        )
        inventados += len(todos - permitidos)

    no_descartadas = [r for r in recetas if not r.get("descartada", False)]
    categoria_correcta = len(no_descartadas)

    firmas = set()
    for r in recetas:
        firmas.add(",".join(sorted(set(r.get("ingredientes_utilizados", [])))))

    return {
        "n_recetas": len(recetas),
        "estructura_completa_pct": round(int(estructura_ok) * 100, 2),
        "ingredientes_inventados": inventados,
        "categoria_correcta_pct": round(
            categoria_correcta / len(recetas) * 100, 2
        ) if recetas else 0,
        "variedad_firmas": len(firmas),
        "aprovechamiento_promedio": round(
            sum(r.get("aprovechamiento", 0) for r in recetas) / len(recetas), 2
        ) if recetas else 0,
    }


def evaluar_con_juez(
    cliente_llm: callable,
    respuesta_texto: str,
    provider: str = "gemini",
) -> tuple[dict, dict]:
    """Evaluación subjetiva auxiliar mediante LLM-as-judge con rúbrica anclada."""
    from .prompts import PROMPT_JUEZ

    prompt = PROMPT_JUEZ + "\n\nRespuesta a evaluar:\n" + respuesta_texto
    texto, metadata = cliente_llm(prompt, json_mode=True)
    return json.loads(texto), metadata


def comparar_prompts(
    resultados: Dict[str, Dict],
    disponibles: List[str],
    catalogo: List[dict],
    basicos: set,
) -> pd.DataFrame:
    """Tabla comparativa de las tres versiones de prompt con métricas objetivas."""
    filas = []
    for version, data in resultados.items():
        metricas = metricas_objetivas(
            data["respuesta_validada"], disponibles, catalogo, basicos
        )
        filas.append(
            {
                "version_prompt": version,
                **metricas,
                "n_errores_validacion": len(data.get("errores", [])),
                "latencia_s": data.get("metadata", {}).get("latency_seconds", None),
            }
        )
    return pd.DataFrame(filas)


def graficar_comparacion(df: pd.DataFrame, nombre_archivo: str = "comparacion_prompts.png") -> str:
    """Genera un gráfico de barras comparando las versiones de prompt."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    cols = [
        "n_recetas",
        "estructura_completa_pct",
        "categoria_correcta_pct",
        "variedad_firmas",
        "aprovechamiento_promedio",
    ]
    ax = df.set_index("version_prompt")[cols].plot(
        kind="bar", figsize=(10, 6), rot=0
    )
    ax.set_title("Comparación objetiva de versiones de prompt")
    ax.set_ylabel("Valor")
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1))
    plt.tight_layout()
    path = IMAGES_DIR / nombre_archivo
    plt.savefig(path)
    plt.close()
    return str(path)
