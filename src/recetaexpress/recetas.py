import json
import re
import difflib
from typing import List, Dict, Any, Set
from unidecode import unidecode

from .config import BASICOS_DESPENSA, DATA_DIR
from .prompts import PROMPT_BASICO, PROMPT_MEJORADO, PROMPT_OPTIMIZADO


def cargar_ingredientes(path=None) -> dict:
    path = path or (DATA_DIR / "ingredientes.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalizar_ingrediente(nombre: str) -> str:
    """Lleva a minúsculas, sin acentos y sin espacios extra."""
    return unidecode(nombre.lower().strip())


def _canonical_map(catalogo: List[dict]) -> Dict[str, str]:
    """Mapea cada alias y canonical a su forma canónica normalizada."""
    cmap = {}
    for item in catalogo:
        can = normalizar_ingrediente(item["canonical"])
        for alias in item["alias"]:
            cmap[normalizar_ingrediente(alias)] = can
        cmap[can] = can
    return cmap


def ingredientes_a_canonical(ingredientes: List[str], catalogo: List[dict]) -> List[str]:
    cmap = _canonical_map(catalogo)
    return [cmap.get(normalizar_ingrediente(ing), normalizar_ingrediente(ing)) for ing in ingredientes]


def construir_prompt(version: str, disponibles: List[str], basicos: Set[str] = None) -> str:
    """Construye el prompt según la versión pedida (basico, mejorado, optimizado)."""
    basicos = basicos or BASICOS_DESPENSA
    if version == "basico":
        template = PROMPT_BASICO
    elif version == "mejorado":
        template = PROMPT_MEJORADO
    elif version == "optimizado":
        template = PROMPT_OPTIMIZADO
    else:
        raise ValueError(f"Versión de prompt desconocida: {version}")
    return template.format(
        ingredientes=", ".join(sorted(disponibles)),
        basicos=", ".join(sorted(basicos)),
    )


def _extraer_json(texto: str) -> str:
    """Extrae un bloque JSON de markdown o del primer objeto JSON que encuentre."""
    if "```" in texto:
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", texto)
        if m:
            return m.group(1).strip()
    m = re.search(r"(\{[\s\S]*\})", texto)
    if m:
        return m.group(1).strip()
    return texto.strip()


def parsear_respuesta(texto: str) -> Dict[str, Any]:
    """Parsea la respuesta del LLM a un diccionario Python. Si falla, devuelve estructura vacía con error."""
    raw = _extraer_json(texto)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        return {
            "recetas_disponibles": [],
            "recetas_un_ingrediente": [],
            "recetas_dos_ingredientes": [],
            "_error_parseo": f"JSONDecodeError: {e}. Texto recibido: {raw[:500]}",
        }


def calcular_aprovechamiento(receta: Dict[str, Any], disponibles: Set[str]) -> float:
    """Porcentaje de ingredientes disponibles que la receta aprovecha."""
    usados = set(receta.get("ingredientes_utilizados", []))
    if not disponibles:
        return 0.0
    return round(len(usados & disponibles) / len(disponibles) * 100, 2)


def _firma_ingredientes(receta: Dict[str, Any]) -> str:
    return ",".join(sorted(set(receta.get("ingredientes_utilizados", []))))


def filtrar_recetas(
    recetas: List[Dict[str, Any]],
    umbral_jaccard: float = 0.75,
    umbral_nombre: float = 0.75,
) -> List[Dict[str, Any]]:
    """Elimina recetas prácticamente idénticas por nombre o por conjunto de ingredientes."""
    filtradas = []
    for receta in recetas:
        nombre = receta.get("nombre", "")
        firma = _firma_ingredientes(receta)
        duplicado = False
        for ref in filtradas:
            # Similitud de nombres
            sim_nombre = difflib.SequenceMatcher(
                None, nombre.lower(), ref.get("nombre", "").lower()
            ).ratio()
            if sim_nombre >= umbral_nombre:
                duplicado = True
                break
            # Jaccard de ingredientes
            set_a = set(firma.split(",")) if firma else set()
            set_b = set(_firma_ingredientes(ref).split(",")) if _firma_ingredientes(ref) else set()
            union = set_a | set_b
            if union and len(set_a & set_b) / len(union) >= umbral_jaccard:
                duplicado = True
                break
        if not duplicado:
            filtradas.append(receta)
    return filtradas


def validar_respuesta(
    respuesta: Dict[str, Any],
    disponibles: List[str],
    basicos: Set[str],
    catalogo: List[dict],
) -> Dict[str, Any]:
    """
    Valida y sanea la respuesta del modelo:
    - Normaliza ingredientes usando el catálogo.
    - Detecta ingredientes inventados.
    - Recalcula faltantes y reclasifica según la cantidad real.
    - Filtra duplicados y ordena por aprovechamiento.
    """
    errores = []
    disponibles_can = set(ingredientes_a_canonical(disponibles, catalogo))
    basicos_can = {normalizar_ingrediente(b) for b in basicos}
    permitidos = disponibles_can | basicos_can

    # Asegurar las 3 claves principales
    if "_error_parseo" in respuesta:
        errores.append(respuesta["_error_parseo"])
    for categoria in ["recetas_disponibles", "recetas_un_ingrediente", "recetas_dos_ingredientes"]:
        if categoria not in respuesta:
            respuesta[categoria] = []
            errores.append(f"Falta la clave '{categoria}'; se inicializó vacía.")

    todas = []
    for categoria in ["recetas_disponibles", "recetas_un_ingrediente", "recetas_dos_ingredientes"]:
        for receta in respuesta.get(categoria, []):
            if not isinstance(receta, dict):
                continue
            # Normalizar campos de ingredientes
            for campo in ["ingredientes_utilizados", "ingredientes_faltantes"]:
                vals = receta.get(campo, [])
                if not isinstance(vals, list):
                    vals = [vals]
                receta[campo] = [ingredientes_a_canonical([v], catalogo)[0] for v in vals]

            # Detectar ingredientes inventados
            todos_ing = set(receta.get("ingredientes_utilizados", [])) | set(
                receta.get("ingredientes_faltantes", [])
            )
            inventados = todos_ing - permitidos
            receta["ingredientes_inventados_detectados"] = sorted(inventados)
            if inventados:
                errores.append(
                    f"Receta '{receta.get('nombre')}' inventó ingredientes: {inventados}"
                )

            # Recalcular faltantes reales (excluyendo básicos)
            usados = set(receta.get("ingredientes_utilizados", []))
            faltantes_reales = (usados - disponibles_can) - basicos_can
            receta["ingredientes_faltantes"] = sorted(faltantes_reales)
            receta["ingredientes_utilizados"] = sorted(usados & permitidos)
            receta["aprovechamiento"] = calcular_aprovechamiento(receta, disponibles_can)
            receta["descartada"] = False
            todas.append(receta)

    # Reclasificación determinística
    nueva = {"recetas_disponibles": [], "recetas_un_ingrediente": [], "recetas_dos_ingredientes": []}
    for receta in todas:
        n_falt = len(receta.get("ingredientes_faltantes", []))
        if n_falt == 0:
            nueva["recetas_disponibles"].append(receta)
        elif n_falt == 1:
            nueva["recetas_un_ingrediente"].append(receta)
        elif n_falt <= 2:
            nueva["recetas_dos_ingredientes"].append(receta)
        else:
            # Demasiados faltantes: se marca como descartada
            receta["descartada"] = True
            receta["motivo_descarte"] = f"{n_falt} ingredientes faltantes (>2)"

    # Filtrar duplicados dentro de cada categoría
    for cat in nueva:
        nueva[cat] = filtrar_recetas(nueva[cat])

    # Ordenar por aprovechamiento descendente
    for cat in nueva:
        nueva[cat].sort(key=lambda r: r.get("aprovechamiento", 0), reverse=True)

    return {"respuesta": nueva, "errores": errores}


def generar_recomendaciones(
    cliente_llm: callable,
    version: str,
    disponibles: List[str],
    catalogo: List[dict],
    basicos: Set[str] = None,
) -> Dict[str, Any]:
    """Pipeline completo: construir prompt → llamar LLM → parsear → validar.

    `cliente_llm` debe ser un callable que reciba un prompt y devuelva (texto, metadata).
    El proveedor/modelo se configura externamente (por ejemplo, mediante una lambda).
    """
    basicos = basicos or BASICOS_DESPENSA
    prompt = construir_prompt(version, disponibles, basicos)
    texto, metadata = cliente_llm(prompt)
    respuesta = parsear_respuesta(texto)
    validado = validar_respuesta(respuesta, disponibles, basicos, catalogo)
    return {
        "prompt": prompt,
        "respuesta_cruda": respuesta,
        "respuesta_validada": validado["respuesta"],
        "errores": validado["errores"],
        "metadata": metadata,
    }


def descubrimiento_progresivo(
    cliente_llm: callable,
    version: str,
    secuencia: List[tuple],
    catalogo: List[dict],
    basicos: Set[str] = None,
) -> List[Dict[str, Any]]:
    """Simula agregar ingredientes de a pocos y reporta qué recetas nuevas aparecen."""
    resultados = []
    anteriores = set()
    for paso, ingredientes in secuencia:
        res = generar_recomendaciones(cliente_llm, version, ingredientes, catalogo, basicos)
        actuales = {
            r["nombre"] for cat in res["respuesta_validada"].values() for r in cat
        }
        novedades = actuales - anteriores
        anteriores = actuales
        resultados.append({
            "paso": paso,
            "ingredientes": ingredientes,
            "novedades": sorted(novedades),
            "total_recetas": len(actuales),
            "detalle": res,
        })
    return resultados
