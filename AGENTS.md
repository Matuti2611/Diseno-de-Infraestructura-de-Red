# Instrucciones para agentes de código

Estas instrucciones aplican a todo el repositorio.

## Antes de trabajar

- Leer `docs/context.md` para conocer el estado real, el reparto de tareas, las decisiones y los bloqueos. Para la página, leer también `docs/plan-frontend.md`.
- Revisar la rama, `git status` y los cambios existentes. Preservar el trabajo de ambos integrantes.
- Comparar la documentación con el código: el informe contiene propuestas escritas como realizadas que todavía no tienen implementación.
- Antes de una implementación grande, presentar arquitectura, alternativas razonables, archivos afectados, riesgos, pruebas y cambios de datos; esperar la aprobación del usuario cuando ese alcance aún no esté autorizado. Consultar en `docs/context.md` el alcance ya aprobado para evitar pedirlo nuevamente.

## Mantener el contexto actualizado

`docs/context.md` es un documento vivo y debe actualizarse cada vez que haya un cambio importante: funcionalidad nueva, cambio de contrato o arquitectura, dependencia, resultado de pruebas, bloqueo o cambio de responsabilidades.

- Antes de cada commit y de cada push, revisar el contexto y actualizar las secciones afectadas dentro del mismo conjunto de cambios. Actualizar el estado y las verificaciones, no solo metadatos.
- Registrar qué funciona, qué está propuesto, qué falta, qué se verificó y el próximo paso concreto. Mantener secciones diferenciadas para página, datos, ML, grafos, API y pruebas.
- Comprobar el resultado de commit/push antes de afirmar que se realizó. Una referencia local `origin/main` no demuestra que se consultó el remoto en esa sesión.
- Si un commit o push cambia un bloqueo o estado de sincronización relevante, reflejarlo en el contexto. No crear commits destinados únicamente a mantener referencias administrativas.
- Describir el estado actual y conservar solo las decisiones históricas que ayuden a entenderlo. No guardar secretos, tokens ni rutas personales necesarias solo en una máquina.
- Mantener la documentación ordenada por temas, sin fechas exactas ni hashes de commits. Conservar versiones de herramientas, comandos y resultados técnicos necesarios para reproducir el proyecto; el historial detallado se consulta en Git.

## Implementación y pruebas

- El usuario trabaja principalmente en la página; Matías en backend, ML e infraestructura de grafos. Los contratos, la integración y el informe se coordinan entre ambos.
- La lógica de predicción, MST y flujo pertenece al backend. El navegador presenta resultados y valida las entradas de la interfaz.
- No agregar tecnologías o servicios sin explicar qué problema resuelven y comprobar si lo existente alcanza. Autenticación, base de datos y servicios externos requieren una necesidad concreta y aprobación según el alcance pedido.
- Los tests deben detectar errores concretos: resultados conocidos, invariantes de grafos, validaciones, errores de red y comportamiento del usuario. No agregar pruebas solo para aumentar el conteo o reflejar línea por línea la implementación.
- Diferenciar fixtures de pruebas, modo demostración y resultados reales. No inventar métricas ni mostrar resultados simulados como si vinieran del modelo.
- Al cerrar una etapa, ejecutar las verificaciones aplicables. En el frontend previsto: tests, lint, TypeScript y build. Si una verificación no se puede ejecutar, registrar el motivo; no declararla aprobada.
- Mantener el informe alineado con lo efectivamente implementado y probado.

## Git y servicios

- Hacer commits pequeños por cambios relacionados cuando el usuario los solicite. La obligación de actualizar contexto no autoriza por sí sola commits ni push.
- No hacer force push, resets destructivos, merges importantes ni borrado de datos sin la autorización correspondiente.
- Consultar la etapa vigente en `docs/context.md`. La página local está implementada y la API está en Render; antes de publicar el frontend, seguir la decisión Vercel + Render y el alcance aprobado por el usuario.
