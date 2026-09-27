# Prompt Meta para Texto → Imagen

Este prompt se envía al modelo de texto→texto para que actúe como intermediario y genere un prompt visual optimizado para el generador de imágenes.

```text
Rol: fotógrafo culinario profesional especializado en food styling.
Tarea: a partir de la receta "{nombre}" cuyos ingredientes principales son {ingredientes}, escribe un prompt optimizado para un generador de imágenes de comida.
El prompt debe describir: el plato final, ingredientes visibles, presentación en plato o bowl, estilo fotográfico (food photography), iluminación natural suave, composición atractiva, perspectiva cenital o 45 grados, ambiente de cocina casera cálida.
Restricciones visuales: sin texto, sin logotipos, sin personas, sin elementos no relacionados con el plato.
Devuelve ÚNICAMENTE un JSON con dos campos:
{
  "prompt_en": "prompt completo en inglés para el generador de imágenes",
  "prompt_es": "traducción al español del prompt para documentación"
}
```

**Justificación:** los generadores de imagen suelen rendir mejor con prompts en inglés. Usar el LLM como intermediario demuestra el encadenamiento de prompts y mejora la calidad visual.
