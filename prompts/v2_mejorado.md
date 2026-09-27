# Prompt 2 — Mejorado

Agrega contexto, objetivo, restricciones y estructura de salida. Es la primera mejora consciente usando técnicas de Fast Prompting.

```text
Contexto: soy un usuario en casa que quiere cocinar sin ir al supermercado.
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
{
  "recetas_disponibles": [...],
  "recetas_un_ingrediente": [...],
  "recetas_dos_ingredientes": [...]
}
Cada receta: nombre, descripcion, ingredientes_utilizados, ingredientes_faltantes, tiempo, dificultad, aprovechamiento.
```

**Técnicas aplicadas:** contexto, objetivo, restricciones, formato de salida estructurado.
