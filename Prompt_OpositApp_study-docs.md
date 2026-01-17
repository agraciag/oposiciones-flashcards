Prompt de trabajo – OpositApp / study-docs

Estoy trabajando en OpositApp, concretamente en el módulo study-docs, que actualmente se ejecuta en:
http://localhost:2998/study-docs

He creado la carpeta “Materiales de Estudio”, cuya estructura inicial es la siguiente:

- /Materiales de Estudio
  - /temario
    - (de momento solo nos interesa el Anexo V – Arquitectura Técnica)
  - /normativa
    - Contendrá la normativa legal y técnica que se utilizará como fuente para desarrollar el contenido de los temas.

Hoy quiero avanzar en la evolución funcional, arquitectónica y de experiencia de usuario del sistema.
Puedes crear los agentes que consideres necesarios.

1. Mejora de la solución actual (study-docs)

La implementación actual de study-docs es funcional, pero presenta limitaciones claras:
- Ventanas de temario y apuntes con tamaño fijo.
- Falta de redimensionado dinámico.
- Dificultad de lectura en sesiones prolongadas.

Objetivo:
Proponer mejoras que permitan redimensionado dinámico, mejor legibilidad y simplicidad.

2. Nuevo formato de estudio: visualización estructurada y colapsable

Además del formato actual, se quiere introducir un segundo formato más sencillo para el estudiante, basado en un preprocesado previo.

Fuente del contenido:
- La estructura se obtiene desde /temario (Anexo V – Arquitectura Técnica).
- El contenido se obtiene desde /normativa.

Ejemplo de visualización deseada:
2. Legislación estatal en materia de régimen del suelo
 └─ Legislación urbanística en la Comunidad Autónoma de Aragón
     ├─ Situaciones
     ├─ Clases
     └─ Categorías del suelo

3. Comportamiento del agente de procesamiento

El agente debe:
- Buscar primero el contenido en /normativa.
- Si no encuentra material suficiente, informar explícitamente.
- Preguntar si el usuario quiere aportar el material o autoriza la búsqueda en Internet.
- No inventar contenido.
- Mantener trazabilidad del proceso.

4. Se espera describir:
- Arquitectura general.
- Agentes y responsabilidades.
- Estrategia de preprocesado.
- Modelo de datos.
- Propuesta de UI.
- Enfoque incremental.
