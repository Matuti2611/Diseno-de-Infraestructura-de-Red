# Contexto del proyecto para agentes de código

Última actualización: 2026-11-07.

> Documento vivo: leer antes de trabajar y actualizar ante cada cambio importante. Antes de commits y push, revisar y actualizar las secciones afectadas junto con el cambio. Las reglas completas están en `../AGENTS.md`.

## Objetivo y consigna

Trabajo integrador de ML, grafos y desarrollo web para una cooperativa de agua. Se debe proyectar el consumo futuro de las zonas, calcular una red de tendidos de menor costo y comprobar si sus capacidades permiten abastecer esa demanda. La consigna indica entrega el 08/11/2026.

Recorrido esperado: datos → regresión → demanda por nodo → Kruskal o Prim → Ford–Fulkerson o Edmonds–Karp → API → frontend.

## Responsabilidades y forma de trabajo

- Usuario: página en React, visualización de redes y experiencia de uso.
- Matías: backend, modelo predictivo y algoritmos de infraestructura.
- Compartido: contrato de datos, integración, pruebas del recorrido completo, informe y defensa.
- El usuario pide tests que detecten errores relevantes y resultados incorrectos; no tests agregados únicamente para que pasen.
- El usuario pidió definir producto, flujos, datos, arquitectura, riesgos y etapas antes de programar la página. El plan está en `plan-frontend.md`; el 2026-11-07 autorizó guardar esta documentación en un commit y arrancar después de su push. No volver a pedir aprobación para el mismo alcance inicial.

## Estado del repositorio

Base inspeccionada: `3139802`, rama `main`. Los últimos cambios de Matías disponibles en esa base son `98f1d5e` (esquemas Pydantic) y `3139802` (informe). No se hizo fetch para comprobar si hay cambios remotos posteriores.

Esta entrega agrega `AGENTS.md`, este contexto, el plan de frontend y enlaces desde el README. El usuario solicitó un commit local de la documentación y se encarga del push; ese push todavía no está confirmado. La implementación comienza en la etapa siguiente. No se empezó a programar la página ni se instaló ninguna dependencia.

## Página / frontend

**Implementado:** estructura de nombres de archivos en `frontend/`; los archivos de código, `package.json`, `tsconfig.json` y `vite.config.ts` siguen vacíos.

**Base aprobada para la siguiente etapa:** conservar React + TypeScript estricto + Vite; CSS propio y SVG para el grafo de 17 nodos; un panel con vistas Tendidos y Capacidad, selector de escenarios y tabla accesible. El diseño visual detallado se desarrolla dentro de ese alcance.

**Integración prevista:** cliente de API aislado de los componentes y modo demostración explícito mientras Matías desarrolla el backend. Ningún fallback silencioso de API fallida a datos simulados. No calcular MST, predicciones ni flujo en el navegador.

**Próximo paso:** el usuario hace push de la documentación; después acordar los detalles del JSON e inicializar la aplicación y su primera vista con datos de ejemplo identificados como tales. La parte visual puede avanzar mientras se termina de acordar el contrato real.

## Datos

**Implementado:**

- `backend/app/data/generar_dataset.py`: genera datos con semilla 42 por defecto; usa únicamente biblioteca estándar de Python.
- `backend/app/data/generar_grafo.py`: cuadrícula 4 × 4 más dos conexiones candidatas desde la planta.
- `backend/data/raw/planta.csv`: una planta.
- `backend/data/raw/zonas.csv`: 16 barrios para proyectar, sin la variable objetivo.
- `backend/data/raw/historial_consumo.csv`: 600 observaciones sintéticas independientes con `consumo_futuro`; no son mediciones históricas reales.
- `backend/data/raw/aristas_candidatas.csv`: 26 conexiones con distancia, costo y capacidad.

**Reglas relevantes:** consumo en m³/mes, proyección a cinco años, capacidades en m³/día, costos convencionales. Dividir el consumo mensual por 30 antes del diagnóstico. Las reglas detalladas están en `../Informe.md`. La validación con estos datos mide aprendizaje de reglas sintéticas, no precisión sobre una cooperativa real.

**Pendiente:** implementación de `cargar.py` e integración con el modelo y el grafo.

## Machine learning

Los archivos `features.py`, `entrenar.py`, `evaluar.py` y `predictor.py` están vacíos. No hay modelo entrenado, métricas ni artefacto guardado.

Propuesta del informe: comparar regresión lineal y árbol de decisión, transformar `tipo_zona`, excluir identificadores y objetivo de las entradas y reportar MAE, RMSE y R². Para comparar modelos o hiperparámetros, usar validación dentro de entrenamiento y reservar el test para la evaluación final.

## Grafos e infraestructura

Los archivos de construcción del grafo, MST, Union-Find, flujo y diagnóstico están vacíos.

Decisiones por implementar: `PLANTA` como fuente; demandas de barrios conectadas a un supersumidero; tratamiento explícito del flujo sobre la red no dirigida; algoritmos propios para cumplir claramente la consigna. NetworkX puede servir de representación y comprobación.

Con costos fijos, cambiar la demanda modifica el flujo y el diagnóstico; no tiene por qué cambiar el MST. Un árbol de costo mínimo puede resultar insuficiente: mostrar ese resultado y su déficit.

## API y contrato

`backend/app/schemas.py` tiene `EscenarioRequest`, `NodoRed`, `TendidoMST`, `EstadoFlujo`, `MetricasML` y `SimulacionResponse`. El escenario es un multiplicador: 1.0, 1.1 y 1.3 corresponden a base, +10 % y +30 %.

`main.py`, routers y `servicios/pipeline.py` están vacíos. `requirements.txt` también. En el intérprete inspeccionado no estaban instalados Pydantic, FastAPI, scikit-learn ni NetworkX.

Antes de integrar la página, acordar con Matías:

- Cómo obtener todas las aristas candidatas, además del MST.
- Resumen con costo total, demanda, caudal abastecido y déficit, con unidades explícitas.
- Identificación de planta, estados de utilización y umbral de cercanía a saturación.
- Rutas y errores de la API, validación de escenarios y mapeo entre nombres CSV y JSON.
- Disponibilidad de métricas: no fabricar valores mientras el modelo no esté entrenado.

Estas ampliaciones son propuestas; no se modificaron unilateralmente los esquemas ni se acordaron rutas definitivas.

## Pruebas y verificación

Última ejecución disponible: `python -m unittest discover -s backend/tests -v` → **1 test aprobado**, de `test_datos.py`. Verifica generación repetible, esquema básico, costos/capacidades positivos y conexión de todos los barrios con la planta. No demuestra que funcionen ML, MST, flujo, API o frontend.

Se verificó sintaxis de `schemas.py` con `ast.parse`; no se ejecutó Pydantic por falta de la dependencia.

La documentación de esta entrega se revisó con `git diff --check` y comprobación de enlaces locales. La página todavía no permite ejecutar tests, lint, TypeScript ni build porque sus archivos de configuración están vacíos.

Pruebas importantes pendientes:

- MST: costo mínimo conocido, conectividad, ausencia de ciclos y grafo desconectado; aceptar distintas soluciones óptimas ante empates.
- Flujo: respuesta conocida, capacidades, conservación, demanda simultánea y déficit.
- Integración: cambiar predicciones o escenario debe afectar correctamente la demanda y el diagnóstico; comprobar unidades.
- ML: evitar fuga del objetivo y del test, evaluar contra una referencia sencilla.
- Página: escenario enviado correctamente, resultados coherentes, errores, reintento y respuestas fuera de orden; accesibilidad y uso en pantallas pequeñas.

Caso conocido útil: PLANTA–A con capacidad 70 m³/día, A–B con 35; demandas A=20 y B=30. Base: suministro 50 y déficit 0. Con +30 %: demanda 65, suministro 61 y déficit 4 en B.

## Informe y documentación

`Informe.md` reemplazó al PDF vacío. La ampliación de Matías describe entrenamiento, algoritmos, backend y frontend como realizados, aunque sus implementaciones están pendientes. Corregir esas afirmaciones o acompañarlas con código y resultados antes de la entrega.

El README explica generación y prueba de datos, pero aún no puede explicar cómo arrancar una aplicación completa inexistente. Mantenerlo actualizado al implementar cada etapa.

## Entorno y comandos conocidos

- Python probado: 3.12.10.
- Node inspeccionado: 24.20.0; npm: 11.19.0.
- En PowerShell, `npm.ps1` queda bloqueado por la política de scripts; `npm.cmd` funciona sin cambiar esa política.
- Generar datos: `python backend/app/data/generar_dataset.py`.
- Prueba actual: `python -m unittest discover -s backend/tests -v`.
- No hay scripts de frontend, variables de entorno ni despliegue configurados todavía.

## Próxima secuencia

1. Push de la documentación a cargo del usuario y acuerdo de los detalles del contrato con Matías.
2. Usuario: frontend con datos de ejemplo explícitos y pruebas de comportamiento.
3. Matías: entrenamiento, MST, flujo, API y sus pruebas.
4. Integración con API real, escenarios completos, informe y ejecución reproducible.
