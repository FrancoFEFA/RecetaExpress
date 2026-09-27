from .config import BASICOS_DESPENSA

PROMPT_BASICO = """Tengo estos ingredientes: {ingredientes}.
¿Qué recetas puedo preparar? Devuélveme la respuesta en formato JSON con tres listas: recetas_disponibles, recetas_un_ingrediente y recetas_dos_ingredientes.
Cada receta debe tener nombre, descripcion, ingredientes_utilizados, ingredientes_faltantes, tiempo, dificultad y aprovechamiento."""

PROMPT_MEJORADO = """Contexto: soy un usuario en casa que quiere cocinar sin ir al supermercado.
Objetivo: dada la lista de ingredientes disponibles, sugerir recetas realistas que pueda preparar ahora o con 1 o 2 ingredientes adicionales.
Ingredientes disponibles: {ingredientes}.
Ingredientes básicos de despensa (siempre disponibles, no cuentan como faltantes): {basicos}.
Restricciones:
- No inventes ingredientes que no estén en la lista de disponibles o básicos.
- Indica claramente los ingredientes faltantes.
- Evita recetas repetidas o prácticamente iguales.
- Prioriza recetas que aprovechen la mayor cantidad de ingredientes disponibles.
- No des cantidades absurdas.
Estructura de salida (JSON estricto):
{{
  "recetas_disponibles": [...],
  "recetas_un_ingrediente": [...],
  "recetas_dos_ingredientes": [...]
}}
Cada receta: nombre, descripcion, ingredientes_utilizados, ingredientes_faltantes, tiempo, dificultad, aprovechamiento."""

PROMPT_OPTIMIZADO = """Rol: actúa como chef experto en cocina del hogar, nutrición y aprovechamiento de alimentos.
Contexto: el usuario tiene una despensa limitada y quiere maximizar el uso de lo que ya tiene, descubriendo recetas nuevas a medida que consigue más ingredientes.
Objetivo: generar sugerencias de recetas clasificadas según cuántos ingredientes adicionales (de la lista de disponibles) requiere cada una: 0, 1 o 2. Los ingredientes básicos de despensa no cuentan como faltantes.
Ingredientes disponibles: {ingredientes}.
Ingredientes básicos de despensa (siempre disponibles, no se listan como faltantes): {basicos}.
Instrucciones específicas:
1. Devuelve SOLO recetas culinariamente plausibles y seguras.
2. Para cada receta lista TODOS sus ingredientes, incluyendo disponibles y básicos.
3. Indica exactamente qué ingredientes faltan de la lista de disponibles (excluyendo básicos).
4. La clasificación se determina por len(ingredientes_faltantes): 0 → recetas_disponibles, 1 → recetas_un_ingrediente, 2 → recetas_dos_ingredientes.
5. Ordena cada lista por aprovechamiento descendiente (más ingredientes disponibles usados primero).
6. Evita recetas con nombres o conjuntos de ingredientes prácticamente idénticos.
7. No inventes ingredientes ni cantidades absurdas.
8. No incluyas ingredientes que no estén en disponibles o básicos sin marcarlos como faltantes.
9. Responde ÚNICAMENTE con el JSON solicitado, sin explicaciones adicionales.
Formato de salida (JSON estricto):
{{
  "recetas_disponibles": [
    {{
      "nombre": "string",
      "descripcion": "string",
      "ingredientes_utilizados": ["string"],
      "ingredientes_faltantes": ["string"],
      "tiempo": "string",
      "dificultad": "string",
      "aprovechamiento": "number (porcentaje de ingredientes disponibles usados)"
    }}
  ],
  "recetas_un_ingrediente": [...],
  "recetas_dos_ingredientes": [...]
}}
Ejemplo: si disponibles son [pollo, arroz, cebolla] y básicos [sal, aceite], "pollo frito con arroz" usaría [pollo, arroz] y faltaría [cebolla] → recetas_un_ingrediente."""

PROMPT_META_IMAGEN = """Rol: fotógrafo culinario profesional especializado en food styling.
Tarea: a partir de la receta "{nombre}" cuyos ingredientes principales son {ingredientes}, escribe un prompt optimizado para un generador de imágenes de comida.
El prompt debe describir: el plato final, ingredientes visibles, presentación en plato o bowl, estilo fotográfico (food photography), iluminación natural suave, composición atractiva, perspectiva cenital o 45 grados, ambiente de cocina casera cálida.
Restricciones visuales: sin texto, sin logotipos, sin personas, sin elementos no relacionados con el plato.
Devuelve ÚNICAMENTE un JSON con dos campos:
{{
  "prompt_en": "prompt completo en inglés para el generador de imágenes",
  "prompt_es": "traducción al español del prompt para documentación"
}}"""

PROMPT_JUEZ = """Eres un evaluador imparcial de sistemas de recomendación de recetas.
Tarea: evalúa la siguiente respuesta JSON de recetas según los criterios listados.
Escala 1-5 con anclas:
1 = muy deficiente, incumple la mayoría de las instrucciones;
3 = aceptable, cumple parcialmente;
5 = excelente, cumple todo con precisión y utilidad.
Criterios:
- claridad: ¿Es fácil entender cada receta?
- relevancia: ¿Las recetas responden a los ingredientes disponibles?
- cumplimiento_instrucciones: ¿Respeta las restricciones (no inventar, indicar faltantes, clasificar correctamente)?
- uso_ingredientes: ¿Usa ingredientes disponibles y no inventa otros?
- estructura: ¿El JSON sigue el formato pedido?
- variedad: ¿Hay diversidad de platos?
- utilidad: ¿Sería útil para un usuario real?
Para cada criterio devuelve nota (1-5) y una justificación corta con evidencia textual. Al final, un comentario general.
Devuelve ÚNICAMENTE JSON con esta estructura:
{{
  "criterios": {{
    "claridad": {{"nota": 0, "justificacion": "..."}},
    "relevancia": {{"nota": 0, "justificacion": "..."}},
    "cumplimiento_instrucciones": {{"nota": 0, "justificacion": "..."}},
    "uso_ingredientes": {{"nota": 0, "justificacion": "..."}},
    "estructura": {{"nota": 0, "justificacion": "..."}},
    "variedad": {{"nota": 0, "justificacion": "..."}},
    "utilidad": {{"nota": 0, "justificacion": "..."}}
  }},
  "comentario_general": "..."
}}"""
