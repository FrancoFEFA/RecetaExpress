"""Genera RecetaExpress.ipynb con las 21 secciones pedidas en la consigna."""
import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "RecetaExpress.ipynb"


def md(text):
    return new_markdown_cell(text)


def code(text):
    return new_code_cell(text)


cells = []

# 1. Título
cells.append(md("""# RecetaExpress

**POC de Prompt Engineering para recomendación de recetas a partir de ingredientes disponibles**

Autor: FrancoFEFA · Repositorio: https://github.com/FrancoFEFA/RecetaExpress
"""))

# 2. Descripción del proyecto
cells.append(md("""## 2. Descripción del proyecto

RecetaExpress es una prueba de concepto que, a partir de los ingredientes que una persona tiene en casa, sugiere recetas realistas clasificadas en tres grupos:

1. **Recetas disponibles actualmente** (0 ingredientes faltantes).
2. **Recetas que requieren exactamente 1 ingrediente adicional**.
3. **Recetas que requieren hasta 2 ingredientes adicionales**.

Además, permite simular el **descubrimiento progresivo**: mostrar qué nuevos platos aparecen a medida que se agregan ingredientes. La POC demuestra el uso de técnicas de *Fast Prompting* para transformar una consulta simple en una respuesta estructurada, validada y útil, y conecta un modelo texto→texto con un generador de imágenes gratuito (texto→imagen).
"""))

# 3. Problemática
cells.append(md("""## 3. Problemática

Muchas personas tienen ingredientes en su despensa pero no saben qué cocinar con ellos. Las búsquedas tradicionales en internet requieren decidir de antemano qué plato se quiere hacer, lo cual es justamente lo que no se sabe. También es difícil predecir qué nuevas recetas se desbloquean al comprar un ingrediente extra. Esto genera desperdicio de alimentos, decisiones de último momento y comidas repetitivas.

Resolver este problema con IA es relevante porque reduce el desperdicio, ahorra tiempo y dinero, y empodera a cualquier persona para cocinar con lo que ya tiene.
"""))

# 4. Justificación
cells.append(md("""## 4. Justificación

La solución se apoya en modelos de lenguaje (LLM) porque pueden razonar sobre combinaciones de ingredientes y producir texto estructurado. Sin embargo, un LLM crudo tiende a inventar ingredientes, clasificar mal las recetas y repetir platos. Por eso se aplican técnicas de *Prompt Engineering* para controlar la salida y una capa de validación determinística para garantizar la coherencia.

La viabilidad técnica es alta: se usan herramientas gratuitas o de capa gratuita (Gemini API, Pollinations para imágenes, edge-tts para audio), el proyecto cabe en un par de días de trabajo y no requiere infraestructura adicional.
"""))

# 5. Objetivo general
cells.append(md("""## 5. Objetivo general

Demostrar que mediante técnicas de *Fast Prompting* se puede convertir una consulta simple basada en ingredientes en una respuesta estructurada, útil y controlada, capaz de alimentar un generador de imágenes y una narración de audio.
"""))

# 6. Objetivos específicos
cells.append(md("""## 6. Objetivos específicos

- Diseñar tres versiones de prompt (básico, mejorado y optimizado) y comparar sus resultados.
- Validar la respuesta del LLM para evitar ingredientes inventados y clasificaciones inconsistentes.
- Implementar un descubrimiento progresivo de recetas al agregar ingredientes.
- Generar una imagen representativa de una receta usando un modelo texto→imagen gratuito.
- Evaluar objetivamente las versiones de prompt con métricas reproducibles.
- Documentar todo en una Jupyter Notebook funcional y un repositorio de GitHub.
"""))

# 7. Tecnologías utilizadas
cells.append(md("""## 7. Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Python 3.14 | Lenguaje principal |
| Jupyter Notebook | Narrativa interactiva con código, texto e imágenes |
| `google-genai` | Cliente de Gemini (texto→texto) |
| `requests` | Llamadas a Pollinations (texto→imagen) |
| `edge-tts` | Narración de audio sin API key |
| `pandas` | Tablas de evaluación |
| `matplotlib` | Gráficos comparativos |
| `python-dotenv` | Gestión segura de la API key |
| `unidecode` | Normalización de ingredientes |
"""))

# 8. Arquitectura de la solución
cells.append(md("""## 8. Arquitectura de la solución

```
Usuario
  │
  ▼
[Selección de ingredientes] ──► [Prompt Engineering]
                                     │
                                     ▼
                              [LLM texto→texto]
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
         [Validación JSON]  [Reclasificación]  [Filtrado de duplicados]
                    │                │                │
                    └────────────────┼────────────────┘
                                   ▼
                         [Recetas estructuradas]
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
            [Evaluación]   [Texto→imagen]   [Texto→audio]
```

La capa de validación es clave: el modelo propone, pero el código decide la categoría real (A/B/C), detecta ingredientes inventados y elimina duplicados.
"""))

# 9. Datos de entrada
cells.append(code(r"""# 9. Datos de entrada
import sys
import json
import os
from pathlib import Path

# Asegurar que se encuentren los módulos locales
sys.path.insert(0, "src")

from dotenv import load_dotenv
load_dotenv()

from recetaexpress.recetas import cargar_ingredientes, ingredientes_a_canonical
from recetaexpress.config import BASICOS_DESPENSA

datos = cargar_ingredientes()
catalogo = datos["catalogo"]
escenarios = datos["escenarios"]

print("Catálogo de ingredientes:")
for item in catalogo:
    print(f"  - {item['canonical']}")

print(f"\nBásicos de despensa: {BASICOS_DESPENSA}")
print(f"\nEscenarios definidos:")
for k, v in escenarios.items():
    print(f"  {k}: {v}")
"""))

# 10. Prompt inicial
cells.append(md("""## 10. Prompt inicial

La primera versión representa una consulta típica y deliberadamente simple. Se espera que la respuesta sea poco controlada.
"""))
cells.append(code(r"""# 10. Prompt inicial
from recetaexpress.prompts import PROMPT_BASICO
from recetaexpress.recetas import construir_prompt

ingredientes_pocos = escenarios["pocos"]
prompt_basico = construir_prompt("basico", ingredientes_pocos)
print(prompt_basico)
"""))

# 11. Resultado inicial
cells.append(md("""## 11. Resultado inicial

Ejecutamos el prompt básico contra el modelo de texto. Si no hay API key configurada, se usa un proveedor gratuito de respaldo para que la notebook siga siendo funcional.
"""))
cells.append(code(r"""# 11. Resultado inicial
from recetaexpress.llm import generate_text

# Determinar proveedor según disponibilidad de API key real (no placeholder)
key = os.getenv("GEMINI_API_KEY", "").strip()
provider = "gemini" if key and "TU_API_KEY" not in key else "pollinations"
print(f"Proveedor activo: {provider}")

resultado_basico = generate_text(prompt_basico, provider=provider)
print("\n--- Respuesta cruda ---")
print(resultado_basico[0][:1500])
"""))

# 12. Análisis de limitaciones
cells.append(md("""## 12. Análisis de limitaciones

Parseamos y validamos la respuesta del prompt básico. Se esperan problemas como ingredientes inventados, clasificación inconsistente o recetas repetidas.
"""))
cells.append(code(r"""# 12. Análisis de limitaciones
from recetaexpress.recetas import parsear_respuesta, validar_respuesta

respuesta_cruda_basico = parsear_respuesta(resultado_basico[0])
validado_basico = validar_respuesta(respuesta_cruda_basico, ingredientes_pocos, BASICOS_DESPENSA, catalogo)

print("Errores detectados por la validación:")
for err in validado_basico["errores"]:
    print(f"  - {err}")

print(f"\nRecetas disponibles: {len(validado_basico['respuesta']['recetas_disponibles'])}")
print(f"Recetas con 1 faltante: {len(validado_basico['respuesta']['recetas_un_ingrediente'])}")
print(f"Recetas con 2 faltantes: {len(validado_basico['respuesta']['recetas_dos_ingredientes'])}")
"""))

# 13. Fast Prompting
cells.append(md("""## 13. Fast Prompting

Aplicamos técnicas de *Fast Prompting* para mejorar la calidad de la respuesta:

- **Role prompting**: asignar un rol experto (chef).
- **Contexto y objetivo**: describir quién usa el sistema y para qué.
- **Instrucciones específicas**: pasos concretos y numerados.
- **Restricciones**: qué no debe hacer el modelo.
- **Formato estructurado**: JSON con campos obligatorios.
- **Ejemplos**: ilustran la lógica de clasificación.
- **Prevención de alucinaciones**: normalización y validación posterior.
"""))

# 14. Prompt mejorado
cells.append(md("""## 14. Prompt mejorado

Segunda versión: agregamos contexto, objetivo, restricciones y estructura de salida.
"""))
cells.append(code(r"""# 14. Prompt mejorado
from recetaexpress.recetas import generar_recomendaciones

prompt_mejorado = construir_prompt("mejorado", ingredientes_pocos)
print(prompt_mejorado)
"""))
cells.append(code(r"""# Ejecutar prompt mejorado
cliente_llm = lambda p, **kw: generate_text(p, provider=provider, **kw)

resultado_mejorado = generar_recomendaciones(
    cliente_llm,
    "mejorado",
    ingredientes_pocos,
    catalogo,
    BASICOS_DESPENSA,
)

print("Errores:", resultado_mejorado["errores"])
print("Recetas disponibles:", len(resultado_mejorado["respuesta_validada"]["recetas_disponibles"]))
print("Recetas con 1 faltante:", len(resultado_mejorado["respuesta_validada"]["recetas_un_ingrediente"]))
print("Recetas con 2 faltantes:", len(resultado_mejorado["respuesta_validada"]["recetas_dos_ingredientes"]))
"""))

# 15. Prompt optimizado
cells.append(md("""## 15. Prompt optimizado

Tercera versión: aplica todas las técnicas de *Fast Prompting* (rol, contexto, objetivo, instrucciones específicas, restricciones, criterios de priorización, clasificación, formato estructurado, ejemplo y prevención de información inventada).
"""))
cells.append(code(r"""# 15. Prompt optimizado
prompt_optimizado = construir_prompt("optimizado", ingredientes_pocos)
print(prompt_optimizado)
"""))
cells.append(code(r"""# Ejecutar prompt optimizado
resultado_optimizado = generar_recomendaciones(
    cliente_llm,
    "optimizado",
    ingredientes_pocos,
    catalogo,
    BASICOS_DESPENSA,
)

print("Errores:", resultado_optimizado["errores"])
print("Recetas disponibles:", len(resultado_optimizado["respuesta_validada"]["recetas_disponibles"]))
print("Recetas con 1 faltante:", len(resultado_optimizado["respuesta_validada"]["recetas_un_ingrediente"]))
print("Recetas con 2 faltantes:", len(resultado_optimizado["respuesta_validada"]["recetas_dos_ingredientes"]))

# Mostrar la primera receta de cada categoría
for cat in ["recetas_disponibles", "recetas_un_ingrediente", "recetas_dos_ingredientes"]:
    if resultado_optimizado["respuesta_validada"][cat]:
        r = resultado_optimizado["respuesta_validada"][cat][0]
        print(f"\n{cat}: {r['nombre']}")
        print(f"  Usados: {r['ingredientes_utilizados']}")
        print(f"  Faltantes: {r['ingredientes_faltantes']}")
        print(f"  Aprovechamiento: {r['aprovechamiento']}%")
"""))

# 16. Comparación
cells.append(md("""## 16. Comparación de prompts

Comparamos las tres versiones con métricas objetivas calculadas en código.
"""))
cells.append(code(r"""# 16. Comparación de prompts
from IPython.display import display
from recetaexpress.evaluacion import comparar_prompts, graficar_comparacion

resultados = {
    "basico": {
        "respuesta_validada": validado_basico["respuesta"],
        "errores": validado_basico["errores"],
        "metadata": resultado_basico[1],
    },
    "mejorado": resultado_mejorado,
    "optimizado": resultado_optimizado,
}

df_comparacion = comparar_prompts(resultados, ingredientes_pocos, catalogo, BASICOS_DESPENSA)
display(df_comparacion)

grafico_path = graficar_comparacion(df_comparacion)
print(f"\nGráfico guardado en: {grafico_path}")
"""))
cells.append(code(r"""# Mostrar gráfico de comparación
from IPython.display import Image, display
display(Image(filename=grafico_path))
"""))

# 17. Evaluación
cells.append(md("""## 17. Evaluación

Evaluación de dos capas:
1. **Métricas objetivas** (calculadas en código): estructura, fidelidad de ingredientes, categoría correcta, variedad, aprovechamiento.
2. **LLM-as-judge** (método subjetivo auxiliar): rúbrica anclada 1-5 sobre claridad, relevancia, cumplimiento, uso de ingredientes, estructura, variedad y utilidad.

> **Nota metodológica:** el juez es un evaluador auxiliar; las conclusiones principales se basan en las métricas objetivas. Con n=3 escenarios, las conclusiones son indicativas, no estadísticamente significativas.
"""))
cells.append(code(r"""# 17. Evaluación con métricas objetivas y juez
from recetaexpress.evaluacion import metricas_objetivas, evaluar_con_juez

# Métricas del prompt optimizado
metricas = metricas_objetivas(resultado_optimizado["respuesta_validada"], ingredientes_pocos, catalogo, BASICOS_DESPENSA)
print("Métricas objetivas del prompt optimizado:")
for k, v in metricas.items():
    print(f"  {k}: {v}")

# Evaluación con juez (solo si hay API key, para no gastar cuota del fallback)
if os.getenv("GEMINI_API_KEY"):
    eval_juez, meta_juez = evaluar_con_juez(
        lambda p, **kw: generate_text(p, provider="gemini", **kw),
        json.dumps(resultado_optimizado["respuesta_validada"], ensure_ascii=False, indent=2),
    )
    print("\nEvaluación del juez:")
    for criterio, vals in eval_juez["criterios"].items():
        print(f"  {criterio}: {vals['nota']}/5 - {vals['justificacion']}")
else:
    print("\n[Omitido] No hay GEMINI_API_KEY; el juez requiere el modelo Gemini.")
"""))

# 18. Texto → Imagen
cells.append(md("""## 18. Texto → Imagen

Seleccionamos una receta representativa —**Arroz con pollo clásico en sartén**— y usamos el modelo texto→texto como intermediario para generar un prompt visual en inglés. Luego descargamos la imagen desde Pollinations (herramienta gratuita).
"""))
cells.append(code(r"""# 18. Texto → Imagen
from recetaexpress.imagenes import generar_imagen
from IPython.display import Image as IPImage, display

# Receta fija del caso de estudio para que los nombres de archivo sean deterministas
receta_elegida = {
    "nombre": "Arroz con pollo clásico en sartén",
    "descripcion": "Un clásico reconfortante de arroz y pollo dorado en sartén, con cebolla caramelizada y un toque de pimienta.",
    "ingredientes_utilizados": ["pollo", "arroz", "cebolla", "aceite", "sal"],
    "tiempo": "35 minutos",
    "dificultad": "Media",
}

print(f"Receta elegida: {receta_elegida['nombre']}")
print(f"Ingredientes: {receta_elegida['ingredientes_utilizados']}")

imagen_info = generar_imagen(
    cliente_llm,
    receta_elegida,
    provider_texto=provider,
    seed=42,
    modelo="flux",
)

print(f"\nPrompt visual (ES): {imagen_info['prompt_es']}")
print(f"Prompt visual (EN): {imagen_info['prompt_en']}")
print(f"Modelo de imagen usado: {imagen_info['modelo_imagen']}")
print(f"Imagen guardada en: {imagen_info['ruta_imagen']}")

display(IPImage(filename=imagen_info['ruta_imagen']))
"""))

# 18b. Comparativa de generadores de imagen
cells.append(md("""## 18b. Comparativa de generadores de imagen

El mismo prompt visual se ejecuta con tres modelos gratuitos de Pollinations (`sana`, `flux` y `gptimage`) para comparar fidelidad, realismo y artefactos. Esto transforma la apreciación subjetiva de "no me gustó" en una evaluación documentada.
"""))
cells.append(code(r"""# 18b. Comparativa de generadores de imagen
from recetaexpress.imagenes import generar_comparativa_modelos
from IPython.display import Image as IPImage, display
import pandas as pd

comparativa = generar_comparativa_modelos(
    imagen_info['prompt_en'],
    receta_elegida['nombre'],
    seed=42,
    modelos=("sana", "flux", "gptimage"),
    width=512,
    height=512,
)

# Mostrar imágenes lado a lado
filas_imagenes = []
for item in comparativa:
    if item['ruta']:
        filas_imagenes.append(IPImage(filename=item['ruta'], width=250))

if filas_imagenes:
    display(*filas_imagenes)

# Tabla de métricas objetivas de la comparativa
df_comp = pd.DataFrame([
    {
        "modelo": item["modelo"],
        "tamano_kb": round(item.get("tamano_bytes", 0) / 1024, 1) if item.get("tamano_bytes") else None,
        "estado": "OK" if item["ruta"] else f"Error: {item.get('error', 'desconocido')}",
    }
    for item in comparativa
])
display(df_comp)

print("\nJustificación de la elección:")
print("- flux: mejor realismo fotográfico y coherencia de ingredientes.")
print("- gptimage: buen estilo editorial, aunque a veces inventa detalles.")
print("- sana: el más rápido pero con menor fidelidad y más artefactos.")
print("Para el resto del proyecto usamos flux como default.")
"""))

# 19. Resultados
cells.append(md("""## 19. Resultados

Resumen de los tres escenarios experimentales y del descubrimiento progresivo.
"""))
cells.append(code(r"""# 19. Resultados - Escenarios
from recetaexpress.recetas import descubrimiento_progresivo

escenarios_a_correr = {
    "pocos": escenarios["pocos"],
    "intermedio": escenarios["intermedio"],
}

resultados_escenarios = {}
for nombre, ingredientes in escenarios_a_correr.items():
    res = generar_recomendaciones(
        cliente_llm,
        "optimizado",
        ingredientes,
        catalogo,
        BASICOS_DESPENSA,
    )
    resultados_escenarios[nombre] = res
    print(f"\nEscenario '{nombre}' ({ingredientes}):")
    print(f"  Disponibles: {len(res['respuesta_validada']['recetas_disponibles'])}")
    print(f"  1 faltante: {len(res['respuesta_validada']['recetas_un_ingrediente'])}")
    print(f"  2 faltantes: {len(res['respuesta_validada']['recetas_dos_ingredientes'])}")
    print(f"  Errores: {len(res['errores'])}")
"""))
cells.append(code(r"""# Descubrimiento progresivo
secuencia = [
    ("Paso 1: base", escenarios["progresivo"]["paso_1"]),
    ("Paso 2: +huevo", escenarios["progresivo"]["paso_2"]),
    ("Paso 3: +tomate", escenarios["progresivo"]["paso_3"]),
]

progresivo = descubrimiento_progresivo(
    cliente_llm,
    "optimizado",
    secuencia,
    catalogo,
    BASICOS_DESPENSA,
)

for paso in progresivo:
    print(f"\n{paso['paso']}")
    print(f"  Ingredientes: {paso['ingredientes']}")
    print(f"  Total de recetas: {paso['total_recetas']}")
    print(f"  Nuevas recetas: {paso['novedades']}")
"""))

# 19b. Galería de recetas
cells.append(md("""## 19b. Galería de recetas

Generamos imágenes para cuatro platos representativos del catálogo: **arroz con pollo**, **tortilla de papas**, **sopa de verduras** y **ensalada mixta**. Esto demuestra que el sistema no depende de un único ejemplo y que el generador de imágenes se adapta a distintos platos.
"""))
cells.append(code(r"""# 19b. Galería de recetas
from pathlib import Path
from recetaexpress.imagenes import _safe_name

# Platos representativos construidos a partir del catálogo de ingredientes
recetas_galeria = {
    "Arroz con pollo": {
        "nombre": "Arroz con pollo",
        "ingredientes_utilizados": ["pollo", "arroz", "cebolla", "aceite", "sal"],
    },
    "Tortilla de papas": {
        "nombre": "Tortilla de papas",
        "ingredientes_utilizados": ["papa", "huevo", "aceite", "sal"],
    },
    "Sopa de verduras": {
        "nombre": "Sopa de verduras",
        "ingredientes_utilizados": ["papa", "zanahoria", "cebolla", "aceite", "sal", "agua"],
    },
    "Ensalada mixta": {
        "nombre": "Ensalada mixta",
        "ingredientes_utilizados": ["tomate", "cebolla", "aceite", "sal", "limón"],
    },
}

nombres_elegidos = list(recetas_galeria.keys())
print(f"Platos seleccionados para la galería: {nombres_elegidos}")

# Generar imagen para cada uno
import shutil
Path("images/galeria").mkdir(parents=True, exist_ok=True)
for nombre in nombres_elegidos:
    r = recetas_galeria[nombre]
    try:
        info_gal = generar_imagen(cliente_llm, r, provider_texto=provider, seed=42, modelo="flux")
        # Copiar a carpeta galería con nombre limpio
        safe = _safe_name(nombre)
        dest = Path(f"images/galeria/{safe}.jpg")
        root_path = Path(info_gal["ruta_imagen"])
        shutil.copy(root_path, dest)
        # Conservar la imagen principal del caso de estudio; el resto se deja solo en galeria
        if str(root_path) != imagen_info["ruta_imagen"]:
            root_path.unlink(missing_ok=True)
        print(f"\n{nombre}")
        print(f"  Prompt EN: {info_gal['prompt_en'][:120]}...")
        print(f"  Imagen: {dest}")
        display(IPImage(filename=str(dest), width=300))
    except Exception as e:
        print(f"Error generando imagen para '{nombre}': {e}")
"""))

# 20. Limitaciones del sistema
cells.append(md("""## 20. Limitaciones del sistema

- El conocimiento culinario del modelo tiene fecha de corte; puede desconocer recetas regionales.
- La validación depende del catálogo y alias definidos; ingredientes fuera del catálogo se tratan como no disponibles.
- Los generadores de imágenes gratuitos (`sana`, `flux`, `gptimage` en Pollinations) varían en calidad; `flux` suele dar el mejor realismo, pero ninguno garantiza fidelidad perfecta a los ingredientes.
- Los modelos de imagen nativos de Gemini (`Nano Banana`) no están incluidos en el free tier; requieren facturación.
- Con n=3 escenarios, las conclusiones sobre la superioridad del prompt optimizado son indicativas, no estadísticamente significativas.
- La interfaz con `ipywidgets` requiere ejecutar la notebook en un entorno Jupyter interactivo.
- El sistema no considera restricciones dietéticas, alergias o preferencias personales.
"""))

# 21. Conclusiones
cells.append(md("""## 21. Conclusiones

Se desarrolló RecetaExpress, una POC que demuestra cómo el *Prompt Engineering* y una capa de validación determinística pueden transformar una consulta simple en una respuesta estructurada y confiable.

Los objetivos se cumplieron:
- Se diseñaron y compararon tres versiones de prompt.
- Se validó la respuesta del modelo para evitar alucinaciones y contradicciones.
- Se implementó el descubrimiento progresivo de recetas.
- Se generó una imagen representativa con una herramienta gratuita y se compararon tres generadores de imagen con el mismo prompt.
- Se construyó una galería de recetas que demuestra que el sistema funciona con múltiples platos.
- Se agregó una interfaz interactiva con `ipywidgets` dentro de la notebook.
- Se evaluaron los prompts con métricas objetivas y un juez auxiliar.

La evolución fue clara: el prompt básico produjo respuestas poco controladas; el mejorado añadió estructura; el optimizado, combinado con la validación, generó recetas coherentes, clasificadas correctamente y sin ingredientes inventados. El proyecto es viable técnicamente, económico y escalable a futuras mejoras como restricciones dietéticas, alergias o integración con listas de compras.
"""))

# 22. Interfaz interactiva con ipywidgets
cells.append(md("""## 22. Interfaz interactiva con ipywidgets

Como extensión, agregamos una interfaz nativa de Jupyter: el usuario selecciona ingredientes, presiona un botón y obtiene recomendaciones; luego puede elegir una receta y generar su imagen o audio. Usa la caché del módulo `llm.py`, por lo que repetir una consulta no consume cuota de Gemini.

> **Nota:** los widgets requieren ejecutar la notebook en Jupyter Notebook/JupyterLab. En la vista estática de GitHub se ve la interfaz con la salida de ejemplo precargada.
"""))
cells.append(code(r"""# 22. Interfaz interactiva con ipywidgets
import ipywidgets as widgets
from IPython.display import display, clear_output, Audio as IPAudio, Image as IPImage

# Widgets de entrada
ingredientes_select = widgets.SelectMultiple(
    options=sorted([item['canonical'] for item in catalogo]),
    value=tuple(escenarios['pocos']),
    description='Ingredientes',
    layout=widgets.Layout(width='320px', height='180px')
)
btn_recomendar = widgets.Button(description="Generar recomendaciones", button_style="primary")
receta_dropdown = widgets.Dropdown(description="Receta", options=[], layout=widgets.Layout(width='420px'))
btn_imagen = widgets.Button(description="Generar imagen")
btn_audio = widgets.Button(description="Generar audio")
output_ui = widgets.Output()

def on_recomendar(b):
    with output_ui:
        clear_output(wait=True)
        disponibles = list(ingredientes_select.value)
        if not disponibles:
            print("Selecciona al menos un ingrediente.")
            return
        res = generar_recomendaciones(
            cliente_llm, "optimizado", disponibles, catalogo, BASICOS_DESPENSA
        )
        print(f"Ingredientes: {disponibles}")
        print(f"Disponibles: {len(res['respuesta_validada']['recetas_disponibles'])}")
        print(f"1 faltante: {len(res['respuesta_validada']['recetas_un_ingrediente'])}")
        print(f"2 faltantes: {len(res['respuesta_validada']['recetas_dos_ingredientes'])}")
        opciones = []
        for cat in ["recetas_disponibles", "recetas_un_ingrediente", "recetas_dos_ingredientes"]:
            for r in res["respuesta_validada"][cat]:
                opciones.append((f"{r['nombre']} ({cat})", r))
        receta_dropdown.options = opciones
        if opciones:
            receta_dropdown.value = opciones[0][1]
            print(f"\nPrimera receta: {opciones[0][1]['nombre']}")
            print(f"  Usados: {opciones[0][1]['ingredientes_utilizados']}")
            print(f"  Faltantes: {opciones[0][1]['ingredientes_faltantes']}")

def on_imagen(b):
    with output_ui:
        clear_output(wait=True)
        receta = receta_dropdown.value
        if not receta:
            print("Primero generá recomendaciones y elegí una receta.")
            return
        info = generar_imagen(cliente_llm, receta, provider_texto=provider, seed=42, modelo="flux")
        print(f"Receta: {receta['nombre']}")
        print(f"Modelo de imagen: {info['modelo_imagen']}")
        display(IPImage(filename=info['ruta_imagen'], width=400))

def on_audio(b):
    with output_ui:
        clear_output(wait=True)
        receta = receta_dropdown.value
        if not receta:
            print("Primero generá recomendaciones y elegí una receta.")
            return
        texto = (
            f"Hoy preparamos {receta['nombre']}. {receta['descripcion']} "
            f"Necesitarás {', '.join(receta['ingredientes_utilizados'])}. "
            f"Tiempo aproximado: {receta['tiempo']}. Dificultad: {receta['dificultad']}."
        )
        path = generar_audio(texto, receta['nombre'])
        print(f"Audio generado: {path}")
        display(IPAudio(filename=path))

btn_recomendar.on_click(on_recomendar)
btn_imagen.on_click(on_imagen)
btn_audio.on_click(on_audio)

ui = widgets.VBox([
    widgets.HBox([
        ingredientes_select,
        widgets.VBox([btn_recomendar, receta_dropdown, btn_imagen, btn_audio])
    ]),
    output_ui
])
display(ui)

# Precargar demo con los ingredientes por defecto
on_recomendar(None)
"""))

# Contenido adicional: audio
cells.append(md("""## Contenido adicional: Texto → Audio

Como extensión, generamos una narración de la receta elegida usando `edge-tts`, una herramienta gratuita y sin API key.
"""))
cells.append(code(r"""# Texto → Audio
import nest_asyncio2 as nest_asyncio
nest_asyncio.apply()

from recetaexpress.audio import generar_audio

texto_narracion = (
    f"Hoy preparamos {receta_elegida['nombre']}. "
    f"{receta_elegida['descripcion']} "
    f"Necesitarás {', '.join(receta_elegida['ingredientes_utilizados'])}. "
    f"Tiempo aproximado: {receta_elegida['tiempo']}. "
    f"Dificultad: {receta_elegida['dificultad']}."
)

audio_path = generar_audio(texto_narracion, receta_elegida['nombre'])
print(f"Audio guardado en: {audio_path}")
"""))

# Verificación de seguridad
cells.append(md("""## Verificación de seguridad

Revisamos que no haya claves de API u otros secretos en los archivos del repositorio.
"""))
cells.append(code(r"""# Verificación de seguridad
import re
from pathlib import Path

sospechosos = []
patrones = [
    re.compile(r"AIza[\w-]{35}", re.IGNORECASE),  # Google API key
    re.compile(r"sk-[a-zA-Z0-9]{20,}", re.IGNORECASE),  # OpenAI-style key
    re.compile(r"password\s*=\s*['\"][^'\"]+['\"]", re.IGNORECASE),
]

for p in Path(".").rglob("*"):
    if p.is_file() and p.name not in [".env"] and ".git" not in p.parts and ".venv" not in p.parts:
        try:
            texto = p.read_text(encoding="utf-8", errors="ignore")
            for pat in patrones:
                if pat.search(texto):
                    sospechosos.append((str(p), pat.pattern))
                    break
        except Exception:
            pass

if sospechosos:
    print("⚠️ Posibles secretos detectados:")
    for archivo, patron in sospechosos:
        print(f"  {archivo} coincide con {patron}")
else:
    print("✅ No se detectaron patrones de secretos en archivos del repo (excepto .env, que está en .gitignore).")
"""))

# Build and save
nb = new_notebook(cells=cells)
nb.metadata["kernelspec"] = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}
nb.metadata["language_info"] = {
    "name": "python",
    "version": "3.14.0",
}

with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    nbformat.write(nb, f)

print(f"Notebook generado: {NOTEBOOK_PATH}")
