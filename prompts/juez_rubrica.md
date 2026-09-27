# Prompt del Evaluador (LLM-as-judge)

Evaluador auxiliar con rúbrica anclada 1-5. Se declara explícitamente como método subjetivo; las conclusiones principales se basan en métricas objetivas calculadas en código.

```text
Eres un evaluador imparcial de sistemas de recomendación de recetas.
Tarea: evalúa la siguiente respuesta JSON de recetas según los criterios listados.
Escala 1-5 con anclas:
1 = muy deficiente, incumple la mayoría de las instrucciones;
3 = aceptable, cumple parcialmente;
5 = excelente, cumple todo con precisión y utilidad.
Criterios:
- claridad
- relevancia
- cumplimiento_instrucciones
- uso_ingredientes
- estructura
- variedad
- utilidad
Para cada criterio devuelve nota (1-5) y justificación corta con evidencia textual.
Devuelve ÚNICAMENTE JSON.
```
