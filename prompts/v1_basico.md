# Prompt 1 — Básico

Representa una consulta típica y deliberadamente simple de un usuario que no conoce técnicas de prompting.

```text
Tengo estos ingredientes: {ingredientes}.
¿Qué recetas puedo preparar? Devuélveme la respuesta en formato JSON con tres listas: recetas_disponibles, recetas_un_ingrediente y recetas_dos_ingredientes.
Cada receta debe tener nombre, descripcion, ingredientes_utilizados, ingredientes_faltantes, tiempo, dificultad y aprovechamiento.
```

**Problemas esperados:** respuesta poco estructurada, ingredientes inventados, clasificación inconsistente, recetas repetidas.
