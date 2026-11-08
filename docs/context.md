# Contexto del proyecto para agentes de código

> Documento vivo: leer antes de trabajar y actualizar ante cada cambio importante. Antes de commits y push, revisar las secciones afectadas junto con el cambio. Reglas completas en `../AGENTS.md`.

## Objetivo y consigna

TP integrador de ML, grafos y web para una cooperativa de agua. Proyectar consumo a cinco años, conectar planta y barrios con menor costo y verificar cobertura mediante flujo máximo. Consigna leída completa: generales/entregables pp. 1–4; caso elegido pp. 7–8.

Recorrido: datos → regresión → demanda por nodo → Kruskal → Edmonds–Karp → API → frontend. El MST usa costos fijos; las predicciones cambian el diagnóstico de capacidad, no necesariamente las conexiones seleccionadas. La matriz está en `revision-consigna.md` y la última revisión del código en `verificacion-proyecto.md`.

## Responsabilidades y alcance

- Ciro: frontend, visualización y experiencia de uso. Matías: backend, ML e infraestructura de grafos. Contratos, integración, informe y defensa compartidos.
- Aprobado: React + TypeScript estricto + Vite, CSS propio, SVG, vistas Tendidos/Capacidad, escenarios y tabla. Sin autenticación/base de datos ni nuevas tecnologías.
- Ciro ya aportó referencias y autorizó HoloCard en una pestaña propia, LatticeLoader durante la carga y TechText solo si encajaba en el grafo. Se integraron los dos primeros sin dependencias nuevas; TechText se dejó sin aplicar porque anima letras, no grafos. Consultar otras mejoras visuales antes de implementarlas.
- Hosting elegido: Vercel frontend + Render FastAPI. El frontend no se publicó; no publicar servicios ni hacer commit/push por obligación de actualizar contexto.
- El usuario exige pruebas de errores/resultados importantes, no pruebas agregadas solo para aumentar conteo.
- Los problemas y sus soluciones se registran en la sección de errores de IA del informe, sin atribución personal a un integrante. La documentación se organiza por estado, decisiones, verificaciones y pendientes, sin fechas exactas ni hashes de commits.

## Estado del repositorio

Los cambios de backend, entorno reproducible, efectos frontend e informe/documentación se agrupan en commits locales para que el usuario los publique. El push queda a cargo del usuario; no se consultó el remoto ni se hizo push en esta agrupación. Se preservaron los algoritmos manuales, el contrato completo y los datos del proyecto.

Render ya entrega el contrato completo; las correcciones locales posteriores todavía no se publicaron. Revisar rama, cambios y sincronización real antes de integrar o publicar. El historial detallado se consulta en Git.

## Página / frontend

Implementado y probado: React/TypeScript/Vite, paleta de Ciro (`#44749d`, `#c6d4e1`, `#ffffff`, `#ebe7e0`, `#bdb8ad`), CSS propio y SVG para la red. HoloCard y LatticeLoader proceden de React Bits y se adaptaron como código local, sin paquetes adicionales ni Tailwind.

- Tendidos y Capacidad; selección de barrio/arista por mouse/teclado, detalle, tabla con búsqueda, leyenda, costo y demanda.
- Base/+10 %/+30 % multiplican la **tasa anual de crecimiento poblacional**, no directamente el consumo.
- API aislada, validación JSON/relaciones/balance, cancelación y espera de 90 s; errores/reintento y respuesta previa identificada. No hay fallback silencioso a resultados de ejemplo.
- Cada arista seleccionada muestra caudal/utilización; distingue cero, dato ausente, cercanía >=90 % y saturación. Etiquetas verticales al costado; gráfico móvil con scroll interno de 760 px.
- Panel usa el resumen real para demanda/suministro/déficit y cobertura. Diagnóstico incompleto queda como compatibilidad si una respuesta no tiene resumen.
- La API actual incluye planta/candidatos y se prioriza su geometría. JSON de CSV local solo como compatibilidad con respuestas anteriores coincidentes; nunca contiene predicciones ni sustituye errores de API. Sincronizarlo con `python frontend/scripts/sincronizar_datos.py` si cambian CSV.
- A pedido de Ciro no hay distintivo live, estado técnico de API ni hora de respuesta en cabecera. Se conserva texto sencillo de cálculo/error.
- Pestaña «Efectos» con carta Pikachu local, reflejos e inclinación; vista cargada de forma diferida y control de pausa. No participa en ML ni grafos; la API no se vuelve a consultar al cambiar de pestaña.
- LatticeLoader azul/orbit durante solicitudes reales: contador reiniciado por escenario/intento y retirado en éxito/error; no es porcentaje de avance ni tiempo exclusivo del cálculo. Respeta movimiento reducido. La tarjeta conserva imagen sin WebGL y detiene/libera recursos al ocultarse/desmontarse. Procedencia y decisiones en `efectos-visuales.md`.

La revisión de integración en Edge confirmó 16 caudales disponibles, cero Sin dato y déficit visible. Los cambios visuales posteriores mantienen esa integración: desde la tarjeta se volvió a Capacidad con 17 nodos/16 caudales y sin excepciones. Guía: `../frontend/README.md`.

## Datos

Generador estándar Python, semilla 42, una planta, 16 barrios, 600 observaciones sintéticas y 26 candidatos. Consumo mensual, capacidad diaria y costos convencionales. Proyección compuesta cinco años con ruido ±5 %; no son mediciones reales. Pipeline divide por 30 para compatibilizar unidades.

`cargar.py` implementa lectores y formatos de nodos/conexiones. Rutas centralizadas en `config.py` aún relativas al directorio de ejecución: iniciar backend desde la raíz. No se regeneraron ni modificaron CSV durante esta revisión.

## Machine learning

Matías cerró la metodología, justificación de features y evaluación de ML en `entrenar.py`:
- **Separación de validación y test:** Selección de modelo mediante validación cruzada 5-Fold dentro del 80 % de entrenamiento (480 muestras) y reserva estricta del 20 % (120 muestras) como conjunto de prueba final no visto.
- **Justificación de features:** Comparación experimental en validación cruzada entre incluir y excluir variables espaciales (`latitud`, `longitud`, `fila`, `columna`). Excluirlas redujo el MAE de CV de 142.65 a 141.80 m³/mes y evitó sobreajuste por ruido aleatorio en coordenadas que no intervienen en el consumo.
- **Comparación de modelos:** En validación cruzada 5-Fold, Regresión Lineal superó a Árbol de Decisión (MAE CV 141.80 frente a 186.66 m³/mes). Se reentrenó en todo el 80 % y se exportó a `backend/models/modelo_consumo.joblib`.
- **Evaluación final en test (20 %):** MAE = 130.11 m³/mes, RMSE = 172.14 m³/mes, R² = 0.9940, MAPE = 3.57 %. Persistidas en `backend/models/metricas.json` y consumidas por la API.
- **Análisis de errores:** Desglose en test por tipo de zona: Residencial MAE=106.83 (3.79 %), Comercial MAE=128.09 (2.62 %), Industrial MAE=326.67 (4.48 %). El mayor error absoluto en industria responde a la escala de consumo (~8600 frente a ~3500 m³/mes), manteniéndose el error relativo uniforme por debajo del 5 %. Muestra de residuos documentada en JSON e informe.
- `features.py`: funciones `preparar_features_entrenamiento` (con exclusión de espaciales) y `preparar_features_inferencia` (asegura coincidencia exacta con `modelo.feature_names_in_`).
- `evaluar.py`: cálculo de métricas globales (MAE, RMSE, MSE, R², MAPE), evaluación por subgrupos y extracción de residuos.
- `ml/metricas.py`: centraliza lectura/validación de `metricas.json`. `metricas_ml` es nullable en el esquema; si el archivo no existe o es inválido produce `null` sin fallar.

## Grafos e infraestructura

- Union-Find propio con compresión de caminos y rango.
- Kruskal manual en `mst.py`; Edmonds–Karp manual con BFS residual en `flujo.py`.
- NetworkX representa grafos y se ejecuta como referencia adicional, comparando totales con tolerancia 0.1. No se comparan conjuntos de aristas ni todos los flujos por arista.
- `diagnostico.py` reporta todos los flujos como magnitudes no negativas de la representación antisimétrica manual; satura al 100 % con tolerancia. Conserva filtro >=90 % como función aparte.
- Helpers de construcción implementados, aunque algunas funciones principales siguen construyendo sus estructuras directamente.

Una comprobación que requiere cancelar flujo residual produjo máximo 2, esperado. Correcciones locales: Kruskal recibe opcionalmente `nodos_esperados`, incluye aislados y rechaza topología vacía/desconectada; pipeline y consulta MST pasan sus nodos declarados. La API informa HTTP 503 ante imposibilidad de conexión. El test de costo conocido 6 ahora llama a la función productiva mediante CSV temporal en vez de duplicar el algoritmo.

Máximo flujo optimiza suministro total, no reparto equitativo. Puede haber barrios con caudal cero en una solución válida. Distintos máximos pueden distribuir flujos de forma distinta: comparar totales/invariantes, no una asignación única con NetworkX.

## API y contrato

FastAPI en `https://infraestructura-red-api.onrender.com`. `POST /api/simular-red` recibe multiplicador positivo <=5; retorna 17 nodos, 16 MST, 26 candidatos, 16 flujos, resumen y métricas. Semántica efectiva del escenario: tasa poblacional, aunque la descripción del esquema aún mezcla demanda/tasa.

`contrato-api.md` describe el contrato implementado y su corrección local de métricas nullable. Hay rutas auxiliares `/api/red/nodos`, `/conexiones`, `/mst` y `/api/modelo/status`, `/metricas`, `/predecir`. La predicción individual ya coincide con la del lote y rechaza tipos no admitidos (HTTP 422).

CORS actual: cualquier origen sin credenciales. Revisar origen definitivo cuando se publique Vercel. Las pruebas de API del repositorio llaman funciones directamente; se verificó HTTP real por separado.

Resultados observados por POST HTTP 200 en Render:

| Escenario | Demanda m³/día | Abastecido m³/día | Déficit m³/día |
| --- | --- | --- | --- |
| Base | 2167.74 | 1435.18 | 732.56 |
| +10 % | 2192.58 | 1439.69 | 752.89 |
| +30 % | 2242.26 | 1448.71 | 793.55 |

La red actual tiene déficit en los tres escenarios. En base se observó una arista saturada y cinco flujos cero; esto difiere de ejemplos antiguos y no implica error por sí mismo, porque la asignación máxima puede variar. No usar el ejemplo anterior con consumo alterado como si fuera el base actual.

## Pruebas y verificación

Última ejecución en esta revisión:

- Backend: `.venv\Scripts\python.exe -m unittest discover -s backend/tests -v` → **22 aprobadas** en seis archivos. Regresiones de inferencia/métricas y desconexión, costo conocido sobre Kruskal real, capacidades, conservación, pipeline y auxiliares. Las pruebas nuevas reprodujeron fallos antes de corregir el código y luego pasaron.
- Frontend: **37 aprobadas**, cinco archivos; lint aprobado; TypeScript y build aprobados (~263 kB JS / 82 kB gzip más vista diferida ~20 kB / 7 kB gzip e imagen ~49 kB). Nuevas comprobaciones de contador, limpieza, error/éxito, alternativa sin WebGL y navegación sin solicitudes extra.
- Edge con efectos: textura/reflejos e inclinación funcionando, pausa, movimiento reducido estable, tarjeta de 308 px a 390 px sin desbordamiento y retorno a red real con 17 nodos/16 caudales. Sin excepciones observadas. Capturas de QA ignoradas en `.preview/`.
- Métricas reproducidas en memoria en la revisión previa; modelo/JSON/CSV sin cambios. Las regresiones están ahora en `test_regresiones.py` y `test_mst.py`, con soluciones explicadas en la sección de IA.
- HTTP Render: OpenAPI y tres escenarios con contrato completo. Edge: 17 nodos, 26 candidatos, 16 etiquetas, cero Sin dato, déficit y cambio a +30 %. A 390 px no desborda la página. Capturas renovadas en `capturas/`.
- HTTP local con código corregido y ruta temporal de métricas ausentes: simulación 200 con 16 caudales/balance y `metricas_ml: null`, consulta de métricas 200/null, Z16 individual 10128.63 m³/mes y categoría inválida 422. No se publicaron estas correcciones en Render desde esta sesión.
- Instalación desde cero comprobada antes de incorporar los efectos, en una copia separada sin reutilizar `.venv` ni `node_modules`: requirements fijados, `pip check`, 22 tests backend, `npm ci`, las 33 pruebas frontend de esa etapa, lint y build con TypeScript aprobados. npm usó la caché disponible. Los efectos no añaden paquetes y sus verificaciones actuales son las 37 pruebas anteriores. No equivale a prueba en otra máquina ni en Linux.
- El bloqueo anterior de la copia frontend por permisos Windows se resolvió en la nueva comprobación con permisos adecuados. No repetir instalaciones destructivas sobre node_modules mientras haya servidores ajenos usándolo; no detener procesos de otros.

El registro canónico de errores y resolución es la sección de IA de `../Informe.md`. `verificacion-proyecto.md` conserva solo estado técnico, pruebas y tareas de cierre, sin atribuir errores a personas.

## Informe y uso de IA

Se actualizaron informe, contexto, contrato, matriz, plan, README y despliegue. Se renombró la revisión a `verificacion-proyecto.md`, quitando la atribución personal del nombre y centralizando error/detección/solución/prueba en la sección de IA del informe. No afirmar que una corrección está desplegada por haber pasado localmente; los resultados de Render y las pruebas locales quedan diferenciados.

Sección IA armada: Codex/Gemini, paletasdecolores.com.ar, exploración de diseños similares en Figma y patrones de un proyecto personal anterior de Ciro presentes aquí (TypeScript, organización, separación, mocks y contexto). No se inspeccionó el código previo ni se atribuye copia literal. No registrar funciones ajenas al alcance como reutilizadas. El indicador live queda como único desacierto visual señalado por Ciro; su comentario se presenta como observación personal. Revisar aportes adicionales de IA de Matías si los hubo; no inventarlos.

El informe distingue ahora React Bits como biblioteca externa elegida por Ciro y la integración/adaptación hecha con Codex. La procedencia y licencia se conservan en `../frontend/THIRD_PARTY_NOTICES.md`. El registro de errores incluye el ajuste de la prueba nueva de carga que se bloqueaba al combinar reloj simulado e interacción asíncrona.

## Hosting y entorno

API desplegada y contrato completo comprobado; frontend todavía sin publicar. Render desde raíz, build `pip install -r backend/requirements.txt`, inicio `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`. `.python-version` fija Python 3.12.10; si Render tiene `PYTHON_VERSION`, esa variable tiene prioridad y debe coincidir. `frontend/vercel.json` configura Vite, `npm ci`, `npm run build` y dist. Importar con raíz frontend, Node 24.x y `VITE_API_URL` configurable. No se contrató ni publicó nada en esta revisión.

Entorno backend revisado: Python 3.12.10, scikit-learn 1.9.1, pandas 3.1.1, NumPy 2.5.4, SciPy 1.18.1, NetworkX 3.7, Joblib 1.6.0, FastAPI 0.162.2, Uvicorn 0.54.0, Pydantic 2.14.3. `backend/requirements.txt` ya fija dependencias directas y transitivas de ese entorno. Revisarlas junto con el artefacto al actualizar.

Frontend: Node 24.20.0/npm 11.19.0; React 19.3.1, Vite 7.3.7, TypeScript 5.9.3, Vitest 4.1.12, ESLint 10.14.0. `.nvmrc` registra la versión local y engines fija 24.x; Vercel mantiene automáticamente menores/parches de esa versión mayor. Lockfile versionado y overrides limitados de minimatch para herramientas lint. En PowerShell usar `npm.cmd`.

README raíz incluye instalación backend con `.venv\Scripts\python.exe`, tests y `-m uvicorn`; reentrenamiento intencional con `-m backend.app.ml.entrenar`. Frontend desde su carpeta con `npm.cmd ci` / `npm.cmd run dev`. Mantener comandos desde raíz para Python. `instalacion-reproducible.md` detalla el ensayo pendiente en otra computadora y diferencia lo comprobado localmente. `despliegue.md` contiene los pasos concretos de importación en Vercel.

## Próxima secuencia

1. El usuario hace push de los grupos locales y se verifica el comportamiento de las correcciones en Render/página. Ya pasaron 22 tests backend y HTTP local; la integración principal de caudales funciona.
2. Repetir la guía de instalación en otra computadora; las versiones y la comprobación en copia limpia local ya están listas. Matías cierra por separado la metodología de evaluación de ML.
3. Completar pruebas HTTP automatizadas; la verificación HTTP actual se realizó por separado con una API temporal.
4. Revisar con Ciro los efectos implementados. Subir los cambios previstos e importar frontend en Vercel, revisar CORS/HTTPS/inactividad y probar desde otra máquina. La configuración está preparada; no hay despliegue de frontend realizado. Consultar antes de otros cambios visuales.
5. Cerrar informe, registro IA adicional de Matías y defensa con comprensión de modelos, demanda/supersumidero y algoritmos.
