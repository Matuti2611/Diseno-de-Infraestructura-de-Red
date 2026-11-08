# Contexto del proyecto para agentes de código

Última actualización: 2026-11-08.

> Documento vivo: leer antes de trabajar y actualizar ante cada cambio importante. Antes de commits y push, revisar y actualizar las secciones afectadas junto con el cambio. Las reglas completas están en `../AGENTS.md`.

## Objetivo y consigna

Trabajo integrador de ML, grafos y desarrollo web para una cooperativa de agua. Proyectar el consumo a cinco años, calcular tendidos de menor costo y comprobar si permiten abastecer la demanda. La consigna indica entrega el 08/11/2026. No se trata de una red de módems.

El 08/11 se releyó el PDF completo: consignas generales pp. 1–4 y TP elegido pp. 7–8. Matriz de cumplimiento en `revision-consigna.md`. El proyecto no se declara completo: además del backend hay pendientes de visualización de todos los caudales, diagnóstico, documentación y entrega. El enunciado exige demo e instrucciones reproducibles; no obliga a publicar en Vercel ni contratar hosting.

Recorrido: datos → regresión → demanda por nodo → Kruskal o Prim → Ford–Fulkerson o Edmonds–Karp → API → frontend.

## Responsabilidades y alcance autorizado

- Usuario: página React, visualización y experiencia de uso.
- Matías: backend, modelo predictivo e infraestructura de grafos.
- Compartido: contrato, integración, pruebas completas, informe y defensa.
- El usuario pide tests que detecten errores relevantes, no pruebas agregadas únicamente para que pasen.
- Se aprobó React + TypeScript estricto + Vite, CSS propio y SVG, con vistas Tendidos y Capacidad, escenarios y tabla. El 08/11 autorizó continuar la página; esta etapa ya está implementada localmente. No volver a pedir aprobación por el mismo alcance.
- Hosting elegido: Vercel para frontend y Render para FastAPI. Efectos decorativos pospuestos. Sin autenticación, base de datos ni servicios nuevos.
- El usuario autorizó agrupar los cambios existentes en commits y continuar con los pendientes del frontend. Se creó y comprobó el commit de implementación de la página, configuración y 22 pruebas; este grupo documental incorpora informe, revisión de consigna y guías actualizadas. El usuario realiza los push; no se autorizó publicar servicios.

## Estado del repositorio

La integración autorizada con Matías quedó en `49707da`, conservando ambos historiales y sin conflictos. El log compartido de Render confirma que ese commit fue publicado. Después se crearon `9031a6e` (despliegue) y `7692bbb` (paleta). Al iniciar esta etapa la rama estaba limpia, `main` dos commits por delante de la referencia local `origin/main`. No se consultó el remoto de nuevo durante esta implementación.

Esta etapa implementa `frontend/` y actualiza documentación y `.gitignore`; no modifica código, datos ni modelo del backend. No se publicó el frontend.

La implementación inicial y sus capturas quedaron registradas en `4b2114e`, comprobado con el log. El siguiente grupo reúne el informe y documentación. No se hizo fetch ni push en esta sesión; la sincronización con el remoto sigue sin comprobarse.

## Página / frontend

**Implementado y probado:** React, TypeScript estricto, Vite y CSS propio con la paleta `#44749d`, `#c6d4e1`, `#ffffff`, `#ebe7e0`, `#bdb8ad`. Texto oscuro derivado; rojo/ámbar para capacidad. Sin biblioteca de animación ni mapas externos.

- Panel con Tendidos y Capacidad, gráfico SVG seleccionable, detalle de barrio/conexión, tabla con búsqueda, leyenda y resumen de demanda/costo/tramos críticos.
- Escenarios base, +10 % y +30 % conectados a API real. El texto aclara que modifican la **tasa de crecimiento poblacional**, como el predictor actual, no directamente el consumo.
- Cliente aislado en `src/api/`, validación JSON y de relaciones nodos/aristas/flujos, cancelación y timeout de 90 segundos. Error, reintento, red vacía y resultado previo identificado por escenario. Respuestas viejas no sobrescriben escenarios nuevos.
- Nunca se sustituyen errores por ejemplos. Los fixtures JSON están solo en tests. Las métricas se muestran como reportadas por API, sin declararlas reproducidas.
- Flujos ausentes: **Sin dato**, no cero. Cercanía desde 90 % y saturación al 100 % se distinguen por flujo/capacidad, pese al booleano actual del backend. No se inventan suministro ni déficit.
- La API omite planta y candidatos. `src/data/casoRed.json` aporta geometría, costos y capacidades de CSV versionados, solo si coinciden barrios y MST con el caso recibido. Si no coinciden, se usa la respuesta sin candidatos locales y se avisa si faltan coordenadas. Se prioriza `tendidos_candidatos` de la API si lo incorpora.
- Sincronización manual: `python frontend/scripts/sincronizar_datos.py` desde raíz. La copia no contiene predicciones ni ejecuta algoritmos. Vercel compila el JSON versionado sin Python.
- En móvil gráfico y tabla tienen desplazamiento interno para mantener etiquetas legibles. Selección por teclado y estados con texto.
- Revisión del usuario: evitar indicadores tipo «en vivo». Se quitaron el distintivo de conexión/API y la hora de última respuesta; solo se conserva el aviso sencillo de cálculo y los errores/reintento. Selector y nota del gráfico explican que el porcentaje aumenta la tasa poblacional y que la red mantiene ubicaciones/costos. Sin cambios al backend.

Guía: `../frontend/README.md`. Decisiones: `plan-frontend.md`. Capturas reales: `capturas/`.

**Próximo paso:** revisión visual del usuario, luego Vercel: raíz `frontend`, build `npm run build`, salida `dist`, Node 24.x y `VITE_API_URL=https://infraestructura-red-api.onrender.com`. Aún no se creó ni publicó ese servicio.

**Pendiente confirmado al releer la consigna:** `MapaRed.tsx` etiqueta solo porcentajes en tramos críticos; no muestra el caudal de cada arista en el gráfico. Al recibir todos los flujos hay que completar esa representación, además de suministro/déficit y estado de cobertura. No basta con que Matías amplíe el JSON para declarar terminada la página.

## Datos

- `generar_dataset.py`: biblioteca estándar, semilla 42; planta, 16 barrios, 600 observaciones sintéticas independientes y 26 aristas candidatas.
- `generar_grafo.py`: cuadrícula 4 × 4 más dos enlaces desde planta.
- Consumo m³/mes, capacidad m³/día, horizonte cinco años, costos convencionales. El pipeline divide por 30 para convertir a diario.
- La evaluación mide aprendizaje de reglas sintéticas, no precisión sobre una cooperativa real.
- `cargar.py` sigue vacío. Rutas de `config.py` relativas: ejecutar backend desde raíz.
- Coordinar cambios CSV con Matías, sincronizar geometría de frontend y revisar diferencias antes de publicar.

## Machine learning

Matías implementó `entrenar.py`: lectura, exclusión ID/objetivo, dummies, partición 80/20 semilla 42 y comparación de regresión lineal/árbol. Exporta regresión lineal a `backend/models/modelo_consumo.joblib`; `predictor.py` la carga. `features.py` y `evaluar.py` siguen vacíos.

Informe y API reportan MAE=131.28, RMSE=172.97 y R²=0.9939; no se reprodujeron aquí y la API los tiene como constantes. La página los identifica como reportados por API (errores en m³/mes).

Pendiente con Matías: separar selección/validación de evaluación final, persistir preprocesamiento/métricas, probar referencia sencilla y evitar fuga. El esquema describe un multiplicador de demanda, pero el predictor multiplica la tasa poblacional: la página refleja el cálculo efectivo; falta alinear documentación del backend.

## Grafos e infraestructura

`mst.py` usa `networkx.minimum_spanning_tree`. `flujo.py` crea arcos en ambos sentidos por cañería, agrega supersumidero y usa `networkx.maximum_flow`. `diagnostico.py` calcula flujo neto y filtra utilización >=90 %. `construir.py` y `union_find.py` siguen vacíos.

Pendiente con Matías: implementación propia exigida frente a llamadas de biblioteca, selección explícita del algoritmo de flujo (informe dice Edmonds–Karp) y tests de mínimo costo, conectividad, ciclos, capacidades, conservación, demanda simultánea y desconexión. Todavía no hay pruebas de estos módulos.

Con costos fijos, cambiar demanda no exige cambiar MST. Un árbol mínimo puede ser insuficiente: mostrar suministro/déficit cuando la API los entregue.

## API y contrato

`POST /api/simular-red` recibe `escenario_crecimiento` (1.0, 1.1, 1.3). Devuelve `nodos`, `tendidos_mst`, `flujos`, `metricas_ml`. FastAPI: `https://infraestructura-red-api.onrender.com`.

Verificación real: 16 barrios, 16 tendidos, dos flujos y demanda base sumada 2167.74 m³/día. Costo MST 73066.05 unidades. El navegador consultó +30 %, con demanda mostrada 2242.3 m³/día. Son observaciones del servicio, no pruebas matemáticas.

**Pendientes de Matías; no se cambió backend en esta etapa:**

1. Planta con coordenadas, candidatos y todos los flujos. El cliente contempla opcionalmente `tendidos_candidatos` con estructura de un tendido.
2. Suministro total, demanda y déficit con unidades; el pipeline calcula parte pero los descarta.
3. Separar cercanía de saturación completa. Hoy el filtro >=90 % marca todos `saturada=True`.
4. Validar escenarios positivos/finitos y errores; alinear semántica de crecimiento.
5. Persistir métricas verificables y fijar dependencias compatibles con modelo.
6. Ajustar CORS al origen definitivo de Vercel. Hoy permite cualquier origen con credenciales; preflight local respondió correctamente.

## Pruebas y verificación

**Frontend, 08/11/2026:**

- `npm.cmd test`: **22 pruebas aprobadas**, tres archivos.
- `npm.cmd run lint`: aprobado.
- `npm.cmd run build`: aprobado; incluye `tsc --noEmit` y Vite. JavaScript ~255 kB / 79 kB gzip.
- Se repitieron las 22 pruebas, lint y build tras quitar indicadores de conexión/hora y aclarar el selector: todo aprobado. Las capturas conservan la primera versión visual, anterior a esos ajustes de texto/cabecera.
- Contrato: números inválidos, duplicados, referencias inexistentes, flujo imposible, campos ausentes; diferencia dato ausente/cero/cercanía/saturación/capacidad cero. Geometría obsoleta no se mezcla con otra red.
- Cliente: request esperado, HTTP fallido, JSON incompatible y timeout.
- Interfaz: búsqueda/restablecer, teclado, escenario, respuestas desordenadas, error/reintento conservando resultado identificado y red vacía sin nodos de ejemplo.
- Edge con API real: escenarios base/+30 %, vistas de tendidos/capacidad, 17 nodos y 26 candidatos. A 390 px la página no desborda y el gráfico mantiene scroll interno. Capturas en `capturas/`.
- Perfiles temporales `.preview/` excluidos del watcher para evitar EBUSY de Edge; no se versionan.
- Se exceptuó `frontend/src/lib/` del ignore genérico de Python para que los helpers de presentación se incluyan al compartir/clonar el proyecto.
- Windows bloqueó esbuild en aislamiento: pruebas/build se ejecutaron con permiso y pasaron.

**Backend:** última ejecución conocida de `test_datos.py`: un test aprobado de repetibilidad, esquema, costos/capacidades positivos y conexión de barrios con planta. No prueba ML, MST, flujo ni pipeline. No se instalaron sus dependencias ni arrancó Python localmente en esta etapa; sí se comprobó el servicio desde navegador.

En la revisión documental del PDF se repitió `test_datos.py`: aprobado. Se comprobaron conteos/columnas de los CSV y la fórmula de las 600 etiquetas (crecimiento a cinco años con ruido ±5 %). No se repitieron tests del frontend porque no cambió código en esta revisión.

**Pendiente:** casos conocidos MST/flujo e integración de demanda simultánea, unidades y déficit; validar ML contra referencia y reservar test final. No presentar los 22 tests de interfaz como validación de algoritmos.

Caso útil: PLANTA–A capacidad 70, A–B capacidad 35; demandas A=20, B=30 m³/día. Base suministro 50/déficit 0. Al multiplicar directamente demandas por 1.3: demanda 65, suministro 61 y déficit 4 en B. No es la semántica del multiplicador de tasa del predictor actual.

## Informe y documentación

`Informe.md` acompaña el desarrollo. Se reescribieron descripciones de ML/grafos para reflejar las llamadas reales y sus límites; se preservan las métricas y la ejecución reportadas por Matías, sin atribuirles reproducción en esta revisión. Se completaron las limitaciones y se quitaron marcas `[cite: ...]`, sustituyéndolas por referencias a páginas de la consigna cuando corresponde. Algoritmos, selección de modelos y análisis de errores siguen pendientes de cierre técnico.

La sección de IA ya incluye herramientas, tareas, ejemplos de instrucciones resumidas, responsabilidades, reflexión y corrección del indicador live. Ciro aclaró que usó paletasdecolores.com.ar y exploró diseños de temática parecida en Figma, sin afirmar prototipado completo o funciones de IA. De su proyecto anterior se documentan solo patrones presentes aquí: TypeScript, componentes/utilidades/tests, separación UI/cliente/backend, mocks y documentación de contexto/continuidad. No se inspeccionó ese proyecto ni se identificaron copias literales; no se atribuye su código a IA. Por pedido expreso de Ciro, registrar únicamente aportes que existan o estén planificados en este proyecto. El indicador live queda como único desacierto visual señalado por Ciro hasta esta revisión; su comentario sobre la IA se registra como observación del integrante. Queda completar el registro de Matías si hubo otras intervenciones.

README raíz y `frontend/README.md`: arranque/pruebas. El plan conserva alternativas y señala implementación y pendientes de API.

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

1. Matías: implementación de algoritmos y tests matemáticos, evaluación reproducible de ML y contrato completo (planta, candidatos, todos los flujos, suministro/déficit).
2. Página: integrar campos nuevos, mostrar todos los caudales y cobertura; probar un escenario que cambie el diagnóstico, sin geometría local cuando la API la provea.
3. Ambos: cerrar informe, uso de IA adicional de Matías si lo hubo, resultados reproducidos, capturas finales y defensa. Referencias de diseño y patrones previos de Ciro ya aclaradas.
4. Verificar instalación/demo completa en otro entorno; registrar código en Git cuando se solicite. Publicar en Vercel conforme a la decisión del grupo y comprobar CORS/HTTPS/despertar de Render.
