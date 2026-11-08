# Contexto del proyecto para agentes de código

Última actualización: 2026-11-08.

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

El 2026-11-07 se ejecutó `git fetch origin`: el remoto avanzó de `3139802` a `7ed8245` con siete commits de Matías (ML, modelo exportado, grafos, API e informe). La rama local conservaba `19e4f36` con el contexto y el plan de frontend.

El usuario autorizó integrar los cambios. Se aplicó un merge conservando ambos historiales; no hubo conflictos de contenido. El código del backend, el modelo y el informe de Matías se conservan sin modificaciones. La integración quedó en `49707da`; el log de Render compartido el 2026-11-08 confirma que ese commit ya fue publicado por el usuario en GitHub. El frontend continúa sin implementar y no se instalaron dependencias nuevas en este entorno.

## Página / frontend

**Implementado:** estructura de nombres de archivos en `frontend/`; los archivos de código, `package.json`, `tsconfig.json` y `vite.config.ts` siguen vacíos.

**Base aprobada para la siguiente etapa:** conservar React + TypeScript estricto + Vite; CSS propio y SVG para el grafo de 17 nodos; un panel con vistas Tendidos y Capacidad, selector de escenarios y tabla accesible. El diseño visual detallado se desarrolla dentro de ese alcance.

**Paleta aportada por el usuario (2026-11-08):** `#44749d` principal, `#c6d4e1` apoyo, `#ffffff` superficies, `#ebe7e0` fondo y `#bdb8ad` separadores decorativos. Los roles y consideraciones de contraste están en `plan-frontend.md`. Los efectos decorativos quedan para después; no agregar bibliotecas de animación para esta primera etapa. Solo se documentó la paleta: todavía no hay CSS ni interfaz implementados.

**Integración prevista:** cliente de API aislado de los componentes y modo demostración explícito mientras Matías desarrolla el backend. Ningún fallback silencioso de API fallida a datos simulados. No calcular MST, predicciones ni flujo en el navegador.

**Próximo paso:** inicializar la aplicación y su primera vista con la paleta elegida; acordar con Matías los campos faltantes de la API ya publicada y verificada. La parte visual puede avanzar con datos de ejemplo identificados como tales mientras se completa el contrato real.

## Datos

**Implementado:**

- `backend/app/data/generar_dataset.py`: genera datos con semilla 42 por defecto; usa únicamente biblioteca estándar de Python.
- `backend/app/data/generar_grafo.py`: cuadrícula 4 × 4 más dos conexiones candidatas desde la planta.
- `backend/data/raw/planta.csv`: una planta.
- `backend/data/raw/zonas.csv`: 16 barrios para proyectar, sin la variable objetivo.
- `backend/data/raw/historial_consumo.csv`: 600 observaciones sintéticas independientes con `consumo_futuro`; no son mediciones históricas reales.
- `backend/data/raw/aristas_candidatas.csv`: 26 conexiones con distancia, costo y capacidad.

**Reglas relevantes:** consumo en m³/mes, proyección a cinco años, capacidades en m³/día, costos convencionales. Dividir el consumo mensual por 30 antes del diagnóstico. Las reglas detalladas están en `../Informe.md`. La validación con estos datos mide aprendizaje de reglas sintéticas, no precisión sobre una cooperativa real.

El pipeline ya carga `zonas.csv` con Pandas y el MST carga las aristas. `cargar.py` sigue vacío. Las rutas de datos y modelo en `config.py` son relativas al directorio de ejecución: por ahora, iniciar desde la raíz del repositorio.

## Machine learning

Matías implementó `entrenar.py`: lectura del historial, exclusión del ID y objetivo, variables dummies, partición 80/20 con semilla 42 y comparación de regresión lineal y árbol. Exporta la regresión lineal a `backend/models/modelo_consumo.joblib`, incluido en el repositorio. `predictor.py` carga ese archivo y prepara las variables para predecir. `features.py` y `evaluar.py` siguen vacíos.

El informe y el endpoint reportan MAE=131.28, RMSE=172.97 y R²=0.9939 para la regresión lineal; son valores incorporados por Matías, todavía no reproducidos en este entorno. La API tiene esas métricas escritas como constantes.

Pendientes de revisión: comparación de modelos en validación reservando test para el final; persistencia reproducible de métricas y preprocesamiento. El predictor multiplica la tasa de crecimiento poblacional por el escenario, aunque el esquema lo describe como multiplicador de demanda: acordar la semántica antes de diseñar los textos de la página.

## Grafos e infraestructura

`mst.py` lee los CSV y usa `networkx.minimum_spanning_tree`; `flujo.py` crea arcos en ambos sentidos por cañería, incorpora el supersumidero y usa `networkx.maximum_flow`. `diagnostico.py` calcula el flujo neto por arista y filtra usos de al menos 90 %. Los archivos `construir.py` y `union_find.py` siguen vacíos.

Pendientes de revisión con Matías: algoritmos propios frente a llamadas de biblioteca según la consigna; `maximum_flow` no selecciona explícitamente Edmonds–Karp aunque el informe lo nombra; comprobar conservación, capacidades, demanda simultánea y desconexión con casos conocidos. No hay pruebas de esos módulos todavía.

Con costos fijos, cambiar la demanda modifica el flujo y el diagnóstico; no tiene por qué cambiar el MST. Un árbol de costo mínimo puede resultar insuficiente: mostrar ese resultado y su déficit.

## API y contrato

`backend/app/schemas.py` tiene `EscenarioRequest`, `NodoRed`, `TendidoMST`, `EstadoFlujo`, `MetricasML` y `SimulacionResponse`. El escenario es un multiplicador: 1.0, 1.1 y 1.3 corresponden a base, +10 % y +30 %.

`main.py` registra FastAPI y el router de `routes_flujo.py`. Existe `POST /api/simular-red`, que acepta `escenario_crecimiento` y devuelve `SimulacionResponse`. El pipeline carga zonas, predice, convierte demanda a m³/día, calcula MST y flujo y filtra tramos con utilización >=90 %. `requirements.txt` contiene FastAPI, Uvicorn, Pandas, scikit-learn, NetworkX y Joblib sin versiones fijadas. En el intérprete inspeccionado esas dependencias siguen sin instalarse; no se importó la aplicación ni se cargó el modelo durante el merge.

Antes de integrar la página, acordar con Matías:

- El endpoint actual no devuelve todas las aristas candidatas ni incluye `PLANTA` en la lista de nodos; ambas cosas son necesarias para el dibujo completo.
- El pipeline calcula costo y caudal abastecido pero los descarta al armar la respuesta; agregar demanda y déficit, con unidades explícitas.
- `flujos` contiene solo tramos con utilización >=90 %, todos marcados `saturada=True`; acordar devolver todos los tramos y diferenciar cercanía de saturación completa.
- Validación de escenarios positivos y finitos, errores de API y mapeo entre nombres CSV y JSON.
- Disponibilidad de métricas: no fabricar valores mientras el modelo no esté entrenado.

Estas ampliaciones son propuestas; durante la integración se preservaron los esquemas y el backend de Matías. CORS actualmente permite cualquier origen con credenciales; revisar la configuración al definir los entornos.

## Pruebas y verificación

Última ejecución disponible: `python -m unittest discover -s backend/tests -v` → **1 test aprobado**, de `test_datos.py`. Verifica generación repetible, esquema básico, costos/capacidades positivos y conexión de todos los barrios con la planta. No demuestra que funcionen ML, MST, flujo, API o frontend.

En la integración se ejecutó la prueba existente de datos y se comprobó la sintaxis de los módulos Python con `ast.parse`, sin importar dependencias. No se validó la API, el modelo serializado ni los algoritmos en ejecución por falta de sus dependencias. Tampoco hay tests de esas partes en el repositorio: los archivos previstos siguen vacíos.

La documentación de esta entrega se revisó con `git diff --check` y comprobación de enlaces locales. La página todavía no permite ejecutar tests, lint, TypeScript ni build porque sus archivos de configuración están vacíos.

Pruebas importantes pendientes:

- MST: costo mínimo conocido, conectividad, ausencia de ciclos y grafo desconectado; aceptar distintas soluciones óptimas ante empates.
- Flujo: respuesta conocida, capacidades, conservación, demanda simultánea y déficit.
- Integración: cambiar predicciones o escenario debe afectar correctamente la demanda y el diagnóstico; comprobar unidades.
- ML: evitar fuga del objetivo y del test, evaluar contra una referencia sencilla.
- Página: escenario enviado correctamente, resultados coherentes, errores, reintento y respuestas fuera de orden; accesibilidad y uso en pantallas pequeñas.

Caso conocido útil: PLANTA–A con capacidad 70 m³/día, A–B con 35; demandas A=20 y B=30. Base: suministro 50 y déficit 0. Con +30 %: demanda 65, suministro 61 y déficit 4 en B.

## Informe y documentación

`Informe.md` reemplazó al PDF vacío. Matías agregó métricas y ejemplos de ejecución junto con el backend. Todavía presenta el frontend como realizado aunque está vacío, deja pendientes los nombres de algoritmos y contiene marcas de citas sin resolver (`[cite: ...]`). Revisar también las afirmaciones sobre Edmonds–Karp y el método de selección del modelo antes de entregar.

El README explica generación y prueba de datos. Matías ya agregó el backend pero falta documentar instalación, versiones y arranque desde la raíz. Mantenerlo actualizado al implementar cada etapa.

## Hosting y despliegue

El usuario eligió **Vercel para la página y Render para FastAPI** el 2026-11-07. `despliegue.md` contiene la comparación y los pasos de configuración. El 2026-11-08 compartió el log de un intento de despliegue hecho desde Render: el servicio pudo clonar el repositorio y seleccionar `49707da`, por lo que el push de la integración ya está confirmado por ese log. Tras un primer fallo por la ruta de requirements, el usuario informó build exitoso y compartió `https://infraestructura-red-api.onrender.com`. Se comprobaron por HTTP la documentación, el contrato OpenAPI y una simulación base: los tres respondieron 200. No se conoce el plan elegido.

Vercel también soporta FastAPI: no asumir que exige una Lambda externa ni que Python lo hace inviable. Antes de optar por funciones, medir el paquete con las dependencias científicas y comprobar la lectura del modelo/CSV. Para Render gratuito, contemplar suspensión tras inactividad y demora al reiniciar. Un VPS autoadministrado requiere administrar el servidor; Lambda agrega empaquetado, permisos y exposición HTTP.

La página se desarrollará con dirección de API configurable. La elección de hosting no exige cambiar el stack aprobado. Quedan pendientes probar dependencias/versiones y memoria del backend, configurar rutas/entornos y CORS, y validar el recorrido completo por HTTPS. El modelo se entrena antes de publicar, no por petición.

Configuración prevista: Render desde la raíz completa, build `pip install -r backend/requirements.txt`, arranque `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` y Python 3.12.10 como base local conocida. Vercel desde `frontend/`, build `npm run build`, salida `dist` y dirección de API en `VITE_API_URL` cuando se implemente el cliente. La versión de Python por sí sola no garantiza compatibilidad con el modelo: fijar las bibliotecas del entrenamiento.

El problema anterior de acceso al repositorio dejó de bloquear el deploy: Render ya lo clonó. El frontend todavía está vacío y no puede desplegarse hasta implementar y probar su build.

Fallo anterior resuelto: Render ejecutaba `pip install -r requirements.txt` desde la raíz, aunque el archivo está en `backend/requirements.txt`. Se indicó corregir el Build Command y el siguiente despliegue ya responde. El log inicial confirmó Python 3.12.10. El 2026-11-08 se verificaron `GET /docs`, `GET /openapi.json` y `POST /api/simular-red` con `escenario_crecimiento=1.0`: HTTP 200, 16 barrios, 16 tendidos MST, 2 tramos de flujo reportados y demanda diaria sumada de 2167.74 m³/día. Estos resultados verifican el recorrido HTTP y la carga del modelo; no demuestran la corrección matemática de predicciones, métricas o algoritmos.

## Entorno y comandos conocidos

- Python probado: 3.12.10.
- Node inspeccionado: 24.20.0; npm: 11.19.0.
- En PowerShell, `npm.ps1` queda bloqueado por la política de scripts; `npm.cmd` funciona sin cambiar esa política.
- Generar datos: `python backend/app/data/generar_dataset.py`.
- Prueba actual: `python -m unittest discover -s backend/tests -v`.
- El backend ahora tiene requisitos declarados, pero no se instalaron en esta sesión. El arranque previsto desde la raíz es `python -m uvicorn backend.app.main:app --reload`; todavía no se verificó aquí.
- No hay scripts ni configuración de entorno de frontend. Render ya tiene un servicio configurado y `PYTHON_VERSION=3.12.10`; arranque y simulación base públicos verificados por HTTP. El cliente de la página deberá usar `https://infraestructura-red-api.onrender.com` como dirección configurable.

## Próxima secuencia

1. Acordar los campos/semántica pendientes del contrato con Matías; la API base ya está disponible para integrar.
2. Usuario: frontend con datos de ejemplo explícitos y pruebas de comportamiento.
3. Matías: pruebas del backend agregado y ajustes de contrato, validación y algoritmos necesarios.
4. Integración con API real, escenarios completos, informe y ejecución reproducible.
