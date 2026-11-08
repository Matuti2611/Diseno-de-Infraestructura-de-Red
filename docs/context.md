# Contexto del proyecto para agentes de código

Última actualización: 2026-11-08.

> Documento vivo: leer antes de trabajar y actualizar ante cada cambio importante. Antes de commits y push, revisar y actualizar las secciones afectadas junto con el cambio. Las reglas completas están en `../AGENTS.md`.

## Objetivo y consigna

Trabajo integrador de ML, grafos y desarrollo web para una cooperativa de agua. Proyectar el consumo a cinco años, calcular tendidos de menor costo y comprobar si permiten abastecer la demanda. La consigna indica entrega el 08/11/2026. No se trata de una red de módems.

El 08/11 se releyó el PDF completo: consignas generales pp. 1–4 y TP elegido pp. 7–8. Matriz de cumplimiento en `revision-consigna.md`. La página ya puede mostrar todos los caudales y un diagnóstico de cobertura mediante una extensión opcional preparada en frontend; faltan los campos reales del backend, validación conjunta y entrega. El enunciado exige demo e instrucciones reproducibles; no obliga a publicar en Vercel ni contratar hosting.

Recorrido: datos → regresión → demanda por nodo → Kruskal o Prim → Ford–Fulkerson o Edmonds–Karp → API → frontend.

## Responsabilidades y alcance autorizado

- Usuario: página React, visualización y experiencia de uso.
- Matías: backend, modelo predictivo e infraestructura de grafos.
- Compartido: contrato, integración, pruebas completas, informe y defensa.
- El usuario pide tests que detecten errores relevantes, no pruebas agregadas únicamente para que pasen.
- Se aprobó React + TypeScript estricto + Vite, CSS propio y SVG, con vistas Tendidos y Capacidad, escenarios y tabla. El 08/11 autorizó continuar la página; esta etapa ya está implementada localmente. No volver a pedir aprobación por el mismo alcance.
- Hosting elegido: Vercel para frontend y Render para FastAPI. Efectos decorativos pospuestos. Sin autenticación, base de datos ni servicios nuevos.
- El usuario autorizó agrupar los cambios existentes en commits y continuar con los pendientes del frontend. Se crearon y comprobaron los commits de implementación inicial y documentación. El siguiente grupo completa etiquetas de caudal, panel de balance opcional y pruebas de capacidad. El usuario realiza los push; no se autorizó publicar servicios.

## Estado del repositorio

La integración autorizada con Matías quedó en `49707da`, conservando ambos historiales y sin conflictos. El log compartido de Render confirma que ese commit fue publicado. Después se crearon `9031a6e` (despliegue) y `7692bbb` (paleta). Al iniciar esta etapa la rama estaba limpia, `main` dos commits por delante de la referencia local `origin/main`. No se consultó el remoto de nuevo durante esta implementación.

Esta etapa implementa `frontend/` y actualiza documentación y `.gitignore`; no modifica código, datos ni modelo del backend. No se publicó el frontend.

La implementación inicial quedó en `4b2114e` y el informe/documentación en `77a492a`, comprobados con el log; el árbol quedó limpio entre esa agrupación y el trabajo nuevo. Esta etapa continúa con el cierre del frontend y su contrato de capacidad. No se hizo fetch ni push en esta sesión; la sincronización con el remoto sigue sin comprobarse.

## Página / frontend

**Implementado y probado:** React, TypeScript estricto, Vite y CSS propio con la paleta `#44749d`, `#c6d4e1`, `#ffffff`, `#ebe7e0`, `#bdb8ad`. Texto oscuro derivado; rojo/ámbar para capacidad. Sin biblioteca de animación ni mapas externos.

- Panel con Tendidos y Capacidad, gráfico SVG seleccionable, detalle de barrio/conexión, tabla con búsqueda, leyenda y resumen de demanda/costo/tramos críticos.
- Escenarios base, +10 % y +30 % conectados a API real. El texto aclara que modifican la **tasa de crecimiento poblacional**, como el predictor actual, no directamente el consumo.
- Cliente aislado en `src/api/`, validación JSON y de relaciones nodos/aristas/flujos, cancelación y timeout de 90 segundos. Error, reintento, red vacía y resultado previo identificado por escenario. Respuestas viejas no sobrescriben escenarios nuevos.
- Nunca se sustituyen errores por ejemplos. Los fixtures JSON están solo en tests. Las métricas se muestran como reportadas por API, sin declararlas reproducidas.
- Flujos ausentes: **Sin dato**, no cero. Cercanía desde 90 % y saturación al 100 % se distinguen por flujo/capacidad, pese al booleano actual del backend. No se inventan suministro ni déficit.
- Cada tendido del MST tiene etiqueta de caudal/utilización en el gráfico; los no informados quedan explícitos. En tramos verticales las etiquetas se ubican al costado para no tapar nombres de nodos. Se preserva selección por teclado con lectura del caudal.
- Panel de abastecimiento preparado para `resumen_capacidad` con demanda/suministro/déficit y estado de cobertura. Es una extensión opcional propuesta, no implementada en Python ni disponible en Render. Sin resumen muestra **Diagnóstico incompleto**; no deduce cobertura aun con todos los caudales. Se valida consistencia con nodos/balance y costos/capacidades de candidatos frente al MST.
- La API omite planta y candidatos. `src/data/casoRed.json` aporta geometría, costos y capacidades de CSV versionados, solo si coinciden barrios y MST con el caso recibido. Si no coinciden, se usa la respuesta sin candidatos locales y se avisa si faltan coordenadas. Se prioriza `tendidos_candidatos` de la API si lo incorpora.
- Sincronización manual: `python frontend/scripts/sincronizar_datos.py` desde raíz. La copia no contiene predicciones ni ejecuta algoritmos. Vercel compila el JSON versionado sin Python.
- En móvil gráfico y tabla tienen desplazamiento interno para mantener etiquetas legibles. Selección por teclado y estados con texto.
- Revisión del usuario: evitar indicadores tipo «en vivo». Se quitaron el distintivo de conexión/API y la hora de última respuesta; solo se conserva el aviso sencillo de cálculo y los errores/reintento. Selector y nota del gráfico explican que el porcentaje aumenta la tasa poblacional y que la red mantiene ubicaciones/costos. Sin cambios al backend.

Guía: `../frontend/README.md`. Decisiones: `plan-frontend.md`. Capturas reales: `capturas/`.

**Próximo paso:** coordinar `contrato-api.md` con Matías y probar sus campos reales en la página. La presentación y los tests del balance ya están preparados. Después, comprobar demo completa/publicación prevista en Vercel: raíz `frontend`, build `npm run build`, salida `dist`, Node 24.x y `VITE_API_URL=https://infraestructura-red-api.onrender.com`. Aún no se creó ni publicó ese servicio.

**Cierre pendiente:** recibir todos los flujos y el resumen real, contrastar el contrato publicado y repetir escenarios cubiertos/con déficit de extremo a extremo. Esa validación no se reemplaza con los mocks; la representación del caudal y del resumen ya está implementada del lado frontend.

## Datos

- `generar_dataset.py`: biblioteca estándar, semilla 42; planta, 16 barrios, 600 observaciones sintéticas independientes y 26 aristas candidatas.
- `generar_grafo.py`: cuadrícula 4 × 4 más dos enlaces desde planta.
- Consumo m³/mes, capacidad m³/día, horizonte cinco años, costos convencionales. El pipeline divide por 30 para convertir a diario.
- La evaluación mide aprendizaje de reglas sintéticas, no precisión sobre una cooperativa real.
- `cargar.py` sigue vacío. Rutas de `config.py` relativas: ejecutar backend desde raíz.
- Coordinar cambios CSV con Matías, sincronizar geometría de frontend y revisar diferencias antes de publicar.

## Machine learning

Matías implementó `entrenar.py`: lectura, exclusión ID/objetivo, dummies, partición 80/20 semilla 42 y comparación de regresión lineal/árbol. Exporta regresión lineal a `backend/models/modelo_consumo.joblib`; `predictor.py` la carga. Las métricas de evaluación del conjunto de prueba se persisten en `backend/models/metricas.json` y son leídas dinámicamente por la API.

Métricas reproducidas y persistidas: MAE=131.28 m³/mes, RMSE=172.97 m³/mes y R²=0.9939 (frente a Árbol de Decisión: MAE=197.95, RMSE=308.79, R²=0.9807).

El multiplicador de escenario se aplica sobre la tasa de crecimiento poblacional proyectada (`crecimiento_poblacional_estimado *= multiplicador`), preservando la semántica del modelo y la presentación del frontend.

## Grafos e infraestructura

Implementación manual propia conforme a la consigna:
- `union_find.py`: Estructura `UnionFind` con compresión de caminos y unión por rango.
- `mst.py`: Algoritmo de Kruskal manual ordenando aristas por costo y previniendo ciclos con `UnionFind`. Valida coincidencia de costo exacto frente a `networkx.minimum_spanning_tree`.
- `flujo.py`: Algoritmo de Edmonds–Karp manual con búsqueda en anchura (`bfs_manual`) para caminos de aumento residuales. Conecta cada barrio al `SUPER_SUMIDERO` con capacidad igual a su demanda diaria proyectada. Valida coincidencia exacta de caudal máximo abastecido frente a `networkx.maximum_flow`.
- `diagnostico.py`: `obtener_estados_flujo` reporta la magnitud neta de caudal para los 16 tendidos del MST, porcentaje de utilización y saturación al 100 %. `obtener_aristas_saturadas` preserva el filtrado >=90 %.

## API y contrato

`POST /api/simular-red` recibe `escenario_crecimiento` (validado positivo y finito: `0.0 < escenario <= 5.0`). Cumple con la especificación completa acordada en `contrato-api.md`:
1. `nodos`: Contiene 17 nodos (la `PLANTA` con sus coordenadas de `planta.csv`, `tipo_zona="PLANTA"` y demanda 0.0, más los 16 barrios).
2. `tendidos_mst`: Los 16 enlaces elegidos por Kruskal con origen, destino, costo y capacidad máxima.
3. `tendidos_candidatos`: Las 26 alternativas de tendidos disponibles en la red con costo y capacidad.
4. `flujos`: 16 registros (la totalidad del MST) con magnitud no negativa, capacidad y booleano `saturada`.
5. `resumen_capacidad`: Objeto con `demanda_total_m3_dia`, `caudal_abastecido_m3_dia` y `deficit_m3_dia`. Cumple la invariante matemática `demanda_total == caudal_abastecido + deficit`.
6. `metricas_ml`: Cargadas dinámicamente desde `backend/models/metricas.json`.
7. CORS configurado con `allow_credentials=False` para compatibilidad estricta con orígenes comodín (`*`) y navegadores modernos.

## Pruebas y verificación

**Backend, 08/11/2026:**

- `python -m unittest discover -s backend/tests -v`: **10 pruebas aprobadas** (0.081 s).
  - `test_datos.py`: 1 test de repetibilidad y conectividad inicial del dataset sintético.
  - `test_mst.py`: 3 tests:
    1. Operaciones básicas de `UnionFind` y detección de ciclos.
    2. Caso pequeño controlado (4 nodos con descarte de aristas redundantes).
    3. Invariantes de Kruskal en el grafo real: 17 nodos conexos, 16 aristas (árbol acíclico), pesos positivos y coincidencia exacta con NetworkX (costo 73066.05).
  - `test_flujo.py`: 2 tests:
    1. Caso controlado resuelto a mano PLANTA–A–B de `contrato-api.md`:
       - Caso cubierto (demandas 20 y 30, capacidades 70 y 35): flujo total 50, déficit 0.
       - Caso insuficiente (demandas 26 y 39, capacidades 70 y 35): cuello de botella en A–B satura en 35, suministro 61, déficit 4.
    2. Invariantes en red completa: respeto de capacidades máximas y conservación de caudal en cada barrio intermedio frente al super-sumidero. Coincidencia con NetworkX.
  - `test_pipeline.py`: 4 tests:
    1. Simulación base completa: 17 nodos, 16 tendidos, 16 flujos, 26 candidatos, balance consistente.
    2. Crecimiento monótono de demanda al aumentar escenario (1.0 -> 1.1 -> 1.3).
    3. Validación del endpoint API con respuesta estructurada según esquema.
    4. Rechazo de escenarios inválidos (menores o iguales a cero).

- `npm.cmd test`: **33 pruebas aprobadas**, cuatro archivos.
- `npm.cmd run lint`: aprobado.
- `npm.cmd run build`: aprobado; incluye `tsc --noEmit` y Vite. JavaScript ~257 kB / 80 kB gzip.
- Se repitieron pruebas, lint y build tras restaurar dependencias y cerrar las etiquetas: todo aprobado. `npm.cmd ls --depth=0` también confirmó dependencias válidas. Las capturas se renovaron con caudales y sin el indicador/hora.
- Contrato: números inválidos, duplicados, referencias inexistentes, flujo imposible, campos ausentes; diferencia dato ausente/cero/cercanía/saturación/capacidad cero. Geometría obsoleta no se mezcla con otra red.
- Cliente: request esperado, HTTP fallido, JSON incompatible y timeout.
- Interfaz: búsqueda/restablecer, teclado, escenario, respuestas desordenadas, error/reintento conservando resultado identificado y red vacía sin nodos de ejemplo.
- Capacidad: etiquetas incluso en tramos no críticos, cero frente a dato ausente, balance consistente, rechazo de resúmenes incompatibles/candidatos contradictorios y transición de cobertura a déficit con respuestas controladas. Caso resuelto a mano exclusivo de tests en `src/tests/fixtures/capacidad.ts`; no representa predicciones del modelo ni se usa en producción.
- Edge con API real: base/+30 %, vistas tendidos/capacidad, 17 nodos, 26 candidatos y 16 etiquetas: dos caudales reales y 14 Sin dato. Se confirma diagnóstico incompleto al faltar resumen. A 390 px la página no desborda y el gráfico mantiene scroll interno de 760 px. Capturas en `capturas/`.
- Perfiles temporales `.preview/` excluidos del watcher para evitar EBUSY de Edge; no se versionan.
- Se exceptuó `frontend/src/lib/` del ignore genérico de Python para que los helpers de presentación se incluyan al compartir/clonar el proyecto.
- Windows bloqueó esbuild en aislamiento: pruebas/build se ejecutaron con permiso y pasaron.
- Instalación aislada: `npm ci --offline --no-audit --no-fund` pasó con el lockfile en una copia sin node_modules. Build/tests de esa copia se bloquearon por permisos de Windows tanto en aislamiento (esbuild) como al elevar (lectura de package.json); no se declaran aprobados allí. El ensayo en otra máquina sigue pendiente.
- En un primer intento dentro de `.preview/`, npm resolvió el frontend principal y afectó node_modules al encontrar ejecutables en uso. Se restauraron sus dependencias con la caché/lockfile, sin cambiar versiones; el proyecto principal volvió a pasar las 33 pruebas, lint y build. No modificar ni detener procesos de desarrollo ajenos al QA propio.

**Backend:** última ejecución conocida de `test_datos.py`: un test aprobado de repetibilidad, esquema, costos/capacidades positivos y conexión de barrios con planta. No prueba ML, MST, flujo ni pipeline. No se instalaron sus dependencias ni arrancó Python localmente en esta etapa; sí se comprobó el servicio desde navegador.

En la revisión documental del PDF se repitió `test_datos.py`: aprobado. Se comprobaron conteos/columnas de los CSV y la fórmula de las 600 etiquetas (crecimiento a cinco años con ruido ±5 %). No se repitieron tests del frontend porque no cambió código en esta revisión.

**Pendiente:** casos conocidos MST/flujo e integración de demanda simultánea, unidades y déficit; validar ML contra referencia y reservar test final. No presentar los 22 tests de interfaz como validación de algoritmos.

Caso útil: PLANTA–A capacidad 70, A–B capacidad 35; demandas A=20, B=30 m³/día. Base suministro 50/déficit 0. Al multiplicar directamente demandas por 1.3: demanda 65, suministro 61 y déficit 4 en B. No es la semántica del multiplicador de tasa del predictor actual.

## Informe y documentación

`Informe.md` acompaña el desarrollo. Se reescribieron descripciones de ML/grafos para reflejar las llamadas reales y sus límites; se preservan las métricas y la ejecución reportadas por Matías, sin atribuirles reproducción en esta revisión. Se completaron las limitaciones y se quitaron marcas `[cite: ...]`, sustituyéndolas por referencias a páginas de la consigna cuando corresponde. Algoritmos, selección de modelos y análisis de errores siguen pendientes de cierre técnico.

La sección de IA ya incluye herramientas, tareas, ejemplos de instrucciones resumidas, responsabilidades, reflexión y corrección del indicador live. Ciro aclaró que usó paletasdecolores.com.ar y exploró diseños de temática parecida en Figma, sin afirmar prototipado completo o funciones de IA. De su proyecto anterior se documentan solo patrones presentes aquí: TypeScript, componentes/utilidades/tests, separación UI/cliente/backend, mocks y documentación de contexto/continuidad. No se inspeccionó ese proyecto ni se identificaron copias literales; no se atribuye su código a IA. Por pedido expreso de Ciro, registrar únicamente aportes que existan o estén planificados en este proyecto. El indicador live queda como único desacierto visual señalado por Ciro hasta esta revisión; su comentario sobre la IA se registra como observación del integrante. Queda completar el registro de Matías si hubo otras intervenciones.

README raíz y `frontend/README.md`: arranque/pruebas. El plan y matriz reflejan el cierre de etiquetas y panel preparado. `contrato-api.md` contiene una propuesta precisa para Matías, estados compatibles y caso conocido, sin afirmar cambios de backend.

## Hosting y despliegue

API desplegada por el usuario en Render. El fallo de requirements se corrigió usando raíz completa y build `pip install -r backend/requirements.txt`. Arranque `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`; log con `PYTHON_VERSION=3.12.10`. Docs, OpenAPI y simulaciones respondieron 200. No se conoce el plan contratado.

Frontend compilado localmente, **sin publicación en Vercel**. `VITE_API_URL` configurable, sin secretos. Modelo entrenado antes del deploy, nunca por petición. Faltan CORS definitivo, HTTPS desde página publicada y carga tras inactividad. No hace falta Lambda ni VPS para esta arquitectura. Ver `despliegue.md`.

## Entorno y comandos conocidos

- Python conocido 3.12.10. Backend desde raíz: `python -m uvicorn backend.app.main:app --reload` (no ejecutado localmente en esta etapa).
- Datos: `python backend/app/data/generar_dataset.py`. Prueba: `python -m unittest discover -s backend/tests -v`.
- Node 24.20.0, npm 11.19.0. PowerShell: `npm.cmd` sin cambiar política.
- Frontend: `cd frontend`, `npm.cmd ci`, `npm.cmd run dev`; `http://127.0.0.1:5173`.
- React 19.3.1, Vite 7.3.7, TypeScript 5.9.3, Vitest 4.1.12, ESLint 10.14.0, TypeScript-ESLint 8.72.1. Lockfile versionado.
- Overrides limitados a minimatch de herramientas lint: 11.0.5 para GHSA-g3hv-75wg-m249. Árbol/lint comprobados; instalación final reportó cero vulnerabilidades conocidas.
- Se detiene el servidor local de QA al cerrar esta etapa; iniciar `npm.cmd run dev` para revisar.

## Próxima secuencia

1. Backend finalizado: Kruskal manual, Edmonds–Karp manual, persistencia de `metricas.json`, suite de 10 tests unitarios y matemáticos, y contrato API completo (`PLANTA`, candidatos, 16 flujos del MST y `resumen_capacidad` consistente).
2. Integración y despliegue: actualizar servicio en Render con los cambios del backend y verificar la respuesta real de extremo a extremo con el frontend.
3. Ambos: cerrar informe (`Informe.md`), reflejar los resultados reproducidos de ML/grafos, capturas finales y preparar la defensa.
