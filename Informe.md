# Informe — Diseño de infraestructura de red de agua

> Informe técnico del caso implementado. Los resultados locales están comprobados; el estado de publicación se distingue de la implementación.

Referencia de requisitos: `enunciado.pdf`, consignas generales y entregables en páginas 1–4 y trabajo «Diseño de infraestructura de red» en páginas 7–8. Ver [estado de cumplimiento y pendientes](docs/revision-consigna.md). Las descripciones siguientes distinguen implementación, resultados reportados y verificaciones pendientes.

## 1. Problema y objetivo

Una cooperativa de agua debe planificar los tendidos para abastecer una zona nueva. El sistema debe proyectar la demanda futura de cada zona, encontrar una red que conecte todos los nodos con el menor costo de construcción y comprobar si las capacidades alcanzan para esa demanda.

**Caso de estudio inicial:** zona ficticia con 16 barrios dispuestos en una cuadrícula de 4 × 4 y una planta identificada como `PLANTA`. Las coordenadas son sintéticas y no describen una red real. El consumo se expresa en m³/mes, la capacidad de los enlaces en m³/día y los costos en unidades convencionales. Para comparar demanda y capacidad se dividirá el consumo mensual proyectado por 30 días.

## 2. Datos

### Zonas

El enunciado propone: `nodo_id`, `latitud`, `longitud`, `poblacion`, `tipo_zona`, `consumo_historico_mensual`, `crecimiento_poblacional_estimado` y `consumo_futuro`. Este último campo es la variable que se debe predecir.

Los datos iniciales son **sintéticos**. `backend/app/data/generar_dataset.py` produce, por defecto y con semilla `42`:

- `planta.csv`: ubicación de la fuente.
- `zonas.csv`: 16 barrios con variables disponibles al predecir; no contiene la respuesta futura.
- `historial_consumo.csv`: 600 observaciones de entrenamiento con la variable objetivo `consumo_futuro`.

La población se sortea entre 200 y 1200 personas; el tipo de zona es residencial, comercial o industrial. La tasa anual de crecimiento se sortea entre 0,5 % y 4 %. Para construir el consumo mensual actual se usa una base de 0,15 m³ por persona y día, multiplicada por 30 días y por factores de tipo de zona (1; 1,45; 2,1), con variación uniforme de ±12 %. El consumo futuro se genera como consumo actual × (1 + crecimiento anual)^5, con variación adicional de ±5 %. Estos parámetros son supuestos didácticos, no mediciones de una cooperativa.

El conjunto de prueba mide cuánto aprende el modelo de **estas reglas simuladas**. Sus métricas no demuestran precisión sobre consumo real.

Este procedimiento sigue la alternativa de dataset sintético admitida por el enunciado (página 2): se entrega el script generador, se declaran las dependencias entre variables y se fija una semilla para reproducir el caso. Las columnas propuestas en la página 7 están en `historial_consumo.csv`; `zonas.csv` omite intencionalmente `consumo_futuro`, porque contiene las zonas para las que hay que predecirlo. `fila` y `columna` son columnas adicionales para construir la cuadrícula; las tablas del enunciado permiten agregar campos.

Se comprobaron los CSV versionados: una planta, 16 zonas, 600 muestras y 26 conexiones; las etiquetas respetan la fórmula de crecimiento compuesto a cinco años con ruido artificial de ±5 %. También pasó el test de generación reproducible y conectividad. Esto valida el generador, no el aprendizaje del modelo ni los algoritmos de red.

### Conexiones posibles

Cada arista candidata debe indicar sus nodos extremos, costo de construcción y capacidad máxima de transporte.

`backend/app/data/generar_grafo.py` conecta cada barrio con sus vecinos horizontales y verticales y agrega dos enlaces posibles desde la planta: 26 aristas en total. El grafo candidato es conexo. La distancia se aproxima a partir de las coordenadas; el costo es distancia en metros × 10 × un factor de dificultad entre 0,9 y 1,25. Los enlaces de la planta reciben una capacidad de 2500 m³/día; el resto toma valores sintéticos de 750, 1200, 2000 o 3000 m³/día. Estas capacidades sirven para ensayar el algoritmo y no representan cálculos hidráulicos.

### Casos de capacidades

El caso de capacidades se elige independientemente del modelo: Original conserva las capacidades iniciales; Progresivo mantiene conexiones, distancias y costos y asigna 2195 m³/día a PLANTA–Z01 y 2500 a los demás candidatos. Se reproduce con `python backend/app/data/generar_caso_progresivo.py`, que no sobrescribe la entrada. Es una regla sintética explícita para mostrar una transición de cobertura con los datos/modelo actuales; no representa un dimensionamiento hidráulico real ni modifica capacidades para forzar el resultado de cada petición. Al cambiar semilla o modelo debe repetirse su validación.

## 3. Modelo predictivo

**Objetivo:** Proyectar el consumo futuro de cada zona a partir de sus características disponibles al momento de predecir.

**Preparación y selección de variables (Features):** 
El dataset histórico cuenta con variables demográficas (`poblacion`), de consumo (`consumo_historico_mensual`), de proyección (`crecimiento_poblacional_estimado`), categóricas (`tipo_zona`) y espaciales (`latitud`, `longitud`, `fila`, `columna`).

- **One-hot encoding:** durante entrenamiento se descarta una categoría de referencia. En inferencia se generan todas las categorías presentes y se alinean con las columnas aprendidas, evitando que el significado cambie al consultar un único barrio.
- **Justificación de variables espaciales:** Se contrastó experimentalmente en validación cruzada el rendimiento del modelo con y sin coordenadas espaciales. La fórmula generadora del consumo depende de la población, el tipo de zona y el crecimiento anual, mientras que las coordenadas y posiciones de cuadrícula fueron diseñadas exclusivamente para la geometría física de la red y las distancias de cañería. En esta comparación, excluir las variables espaciales redujo el error medio (el MAE en validación cruzada bajó de 142.65 a 141.80 m³/mes en la regresión lineal, y de 194.37 a 186.66 m³/mes en el árbol de decisión). Su exclusión simplifica el modelo y coincide con las reglas generadoras. La pequeña diferencia observada en CV no demuestra por sí sola que exista sobreajuste.

**Metodología de entrenamiento y validación:**
Para no utilizar el conjunto de prueba como criterio de decisión ("examen final para elegir modelo"), se implementó una partición estricta en dos etapas:

1. **Partición inicial 80/20:** El dataset de 600 observaciones se dividió aleatoriamente con semilla `42`, reservando el 20 % (120 observaciones) para evaluación, sin usarlo en el ajuste ni en la CV del script actual.
2. **Validación cruzada K-Fold ($K=5$) en entrenamiento:** Dentro del 80 % de entrenamiento (480 observaciones), se compararon los modelos mediante validación cruzada con 5 pliegues para seleccionar la mejor arquitectura y validar la selección de features.

**Comparación de modelos en validación cruzada (5-Fold sobre el 80 % de Train):**

| Modelo y configuración | MAE CV (m³/mes) | RMSE CV (m³/mes) | R² CV |
| :--- | :--- | :--- | :--- |
| **Regresión Lineal (sin espaciales)** | **141.80** | **193.86** | **0.9930** |
| Regresión Lineal (con espaciales) | 142.65 | 194.68 | 0.9930 |
| Árbol de Decisión (sin espaciales) | 186.66 | 288.42 | 0.9846 |
| Árbol de Decisión (con espaciales) | 194.37 | 296.84 | 0.9837 |

**Selección del modelo:**
La regresión lineal sin variables espaciales obtuvo el menor MAE y RMSE medios de CV, con R² medio 0.9930. Se eligió esa configuración y se ajustó en el 80 % de entrenamiento para exportarla. El script fija explícitamente esta elección; no implementa búsqueda automática del ganador para otros datasets. R² es un coeficiente de determinación, no una exactitud de clasificación.

**Evaluación final sobre el conjunto de test reservado (20 %):**
El modelo ajustado se evaluó sobre las 120 observaciones de test. La partición se conservó durante el desarrollo y ya se había consultado en versiones anteriores: estos resultados son una evaluación interna del caso sintético, no una validación externa ciega.

- **MAE:** $130.11\,\text{m}^3/\text{mes}$
- **RMSE:** $172.14\,\text{m}^3/\text{mes}$
- **R²:** $0.9940$
- **MAPE (Error porcentual absoluto medio):** $3.57\,\%$

**Análisis detallado de errores y residuos:**
Para analizar dónde y por qué se producen las discrepancias predictivas, se desglosó el error sobre el conjunto de test por categoría de barrio (`tipo_zona`):

| Tipo de Zona | Muestras ($N$) | Consumo Promedio | MAE (m³/mes) | RMSE (m³/mes) | MAPE (%) | R² |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Residencial** | 82 (68.3 %) | 3557.7 m³/mes | 106.83 | 133.63 | 3.79 % | 0.9885 |
| **Comercial** | 28 (23.3 %) | 5201.4 m³/mes | 128.09 | 157.71 | 2.62 % | 0.9943 |
| **Industrial** | 10 (8.3 %) | 8637.4 m³/mes | 326.67 | 373.51 | 4.48 % | 0.9840 |

*Interpretación de los errores:*

1. **Escala y error relativo:** la industria tiene mayor error absoluto (326.67 frente a 106.83 m³/mes residencial) y también mayor MAPE (4.48 % frente a 3.79 %). La escala de consumo explica parte de la diferencia, pero no permite concluir que ambos ajustes sean equivalentes. Solo hay diez muestras industriales de test. MAPE es un promedio: existen observaciones con errores individuales mayores al 5 %.
2. **Distribución muestral:** el test contiene 82 casos residenciales, 28 comerciales y 10 industriales. Son proporciones próximas a los pesos de generación 65/25/10, no una reproducción exacta ni una muestra de una población real.
3. **Ejemplos de objetivo sintético frente a predicción:** son los primeros casos del test en el orden de la partición, no una muestra estadísticamente representativa. «Real» en las cifras siguientes significa etiqueta sintética observada, no medición de una cooperativa.
   - Nodo `H0182` (Residencial): Real = $1896.35\,\text{m}^3$, Predicho = $1885.44\,\text{m}^3$ (Error: $10.91\,\text{m}^3$ / $0.6\,\%$).
   - Nodo `H0566` (Residencial): Real = $4518.64\,\text{m}^3$, Predicho = $4484.35\,\text{m}^3$ (Error: $34.29\,\text{m}^3$ / $0.8\,\%$).
   - Nodo `H0285` (Comercial): Real = $6934.56\,\text{m}^3$, Predicho = $7118.93\,\text{m}^3$ (Error: $184.37\,\text{m}^3$ / $2.7\,\%$).
   - Nodo `H0078` (Comercial): Real = $7342.12\,\text{m}^3$, Predicho = $7542.74\,\text{m}^3$ (Error: $200.62\,\text{m}^3$ / $2.7\,\%$).
   - Nodo `H0111` (Comercial): Real = $2306.38\,\text{m}^3$, Predicho = $2127.37\,\text{m}^3$ (Error: $179.01\,\text{m}^3$ / $7.8\,\%$).

Todos los artefactos resultantes (modelo entrenado y reporte estructurado en JSON con comparativas de validación y desglose por zonas) se encuentran sincronizados y persistidos en `backend/models/`.

## 4. Algoritmos de grafos

### Red de menor costo
El problema se resuelve con un árbol de expansión mínima (MST): conectar planta y barrios minimizando la suma de costos de construcción. El enunciado pide implementar **Kruskal o Prim** (página 7).

**Implementación manual:** Kruskal en `backend/app/grafos/mst.py`, con `UnionFind`, compresión de caminos y unión por rango. Ordena aristas por costo y acepta un enlace si une componentes distintas. El costo del caso actual es 73066.05 unidades. El código compara el costo con NetworkX usando tolerancia absoluta de 0.1; no compara conjuntos de aristas ni exige igualdad exacta. Ante costos empatados puede haber distintos árboles óptimos. Ahora verifica conexión de todos los nodos esperados y rechaza una topología vacía o desconectada; no presenta un bosque como red completa.

### Diagnóstico de capacidad
El objetivo es comparar la demanda proyectada con el máximo caudal que puede transportar la red elegida. El enunciado pide **Ford–Fulkerson o Edmonds–Karp** (página 7).

**Implementación manual:** Edmonds–Karp en `backend/app/grafos/flujo.py`. Usa BFS para hallar caminos de aumento más cortos en cantidad de aristas y actualiza el flujo en ambos sentidos de la red residual. El total abastecido se compara con NetworkX con tolerancia absoluta de 0.1; no se compara la asignación por arista. Las soluciones máximas pueden distribuir el agua de forma distinta. Una comprobación adicional de revisión que requiere cancelar un flujo previo obtuvo el máximo esperado de 2.

**Representación de la red y compatibilización de unidades:**

1.  **Fuente y Sumidero:** Se definió el nodo `PLANTA` como el nodo fuente (source). Para representar la demanda simultánea de todos los barrios, se agregó un "súper sumidero" (super-sink) ficticio al grafo. Cada barrio se conectó a este sumidero general con una arista dirigida cuya capacidad máxima es exactamente su demanda predicha.
2.  **Unidades:** Dado que la capacidad máxima de las conexiones candidatas está expresada en m³/día, la proyección de consumo futuro mensual de los nodos devuelta por el modelo se dividió por 30 para obtener una demanda diaria y poder operar de forma coherente en el grafo.

**Integración efectiva de predicciones y grafos:** las predicciones determinan la demanda de cada barrio y la capacidad de su conexión al supersumidero. Así pueden cambiar el flujo máximo y el déficit. El MST usa costos fijos y no recibe las demandas como pesos: cambiar el escenario no tiene por qué modificar sus conexiones. Esto es coherente con diseñar primero por costo y después validar capacidad; no es una optimización conjunta de costo y abastecimiento.

## 5. Integración y aplicación web

El sistema se desarrolló utilizando un monorepo que separa la lógica de cálculo pesada de la interfaz de usuario:

**Backend (API + ML + Grafos):** Construido en Python y FastAPI. Centraliza la inferencia y los cálculos de redes. El pipeline recibe el escenario de crecimiento, proyecta demandas, obtiene el MST mediante Kruskal manual, evalúa el flujo máximo hacia el super-sumidero con Edmonds–Karp manual y devuelve la respuesta JSON completa cumpliendo el contrato de `docs/contrato-api.md`: 17 nodos (incluyendo `PLANTA` con demanda $0.0$), 26 conexiones candidatas, 16 flujos del MST y el `resumen_capacidad` con demanda total, caudal abastecido y déficit.

**Frontend (Interfaz de Usuario):** Implementado en React, TypeScript estricto y Vite, con CSS propio y gráfico SVG. Consume `POST /api/simular-red` del servicio de Render y ofrece:

- Tendidos: 26 conexiones candidatas del caso, red de menor costo resaltada, costo y selección de nodos/aristas con detalle.
- Capacidad: flujo y utilización de los tramos informados, distinguiendo cercanía desde 90 % y saturación al 100 %. Los tramos no devueltos se muestran como **Sin dato**, sin asumir flujo cero.
- Escenarios base, +10 % y +30 % que multiplican la tasa de crecimiento poblacional del predictor actual. No equivalen a aumentar directamente la demanda en esos porcentajes.
- Tabla con búsqueda, acceso por teclado, estados de carga/error/reintento y protección frente a respuestas fuera de orden. En móvil el gráfico conserva etiquetas legibles con desplazamiento interno.

La API actual aporta planta, candidatos, todos los flujos y resumen. La página prioriza esos datos y muestra el balance real. Conserva un complemento de geometría CSV para respuestas antiguas coincidentes, sin predicciones ni algoritmos. No hay fallback a resultados simulados ante fallos de API.

La interfaz base fue verificada con la API desplegada. La ampliación de casos y abastecimiento por barrio se verificó contra la API local actualizada y sigue pendiente de publicación; también sigue pendiente el frontend en Vercel.

**Ampliación de capacidad y comparación:** la petición agrega `caso_red` original/progresivo y la respuesta confirma caso/crecimiento. Cada barrio informa demanda, suministro efectivo desde su flujo al supersumidero y déficit. La planta es fuente, no consumidora. Se comprueba suministro no negativo y no superior a demanda; los totales suman las cantidades publicadas por barrio con dos decimales para conservar el balance. La página presenta detalle y tabla por barrio, y consulta tres escenarios del mismo caso para compararlos sin cambiar el escenario principal del gráfico. No calcula predicciones/flujo ni suma caudales de cañerías como consumo de barrios.

El caso Progresivo cubrió Base (2167.62 m³/día) y +10 % (2192.42 m³/día, entrada utilizada ~99.9 %); con +30 % la demanda fue 2242.09, el suministro 2195.00 y el déficit 47.09 m³/día. Son resultados HTTP de la API local con el modelo entregado. El original se conserva y sigue mostrando insuficiencia. Contrato, seis balances y límites en [casos-capacidad.md](docs/casos-capacidad.md).

**Integración verificada:** cada tendido seleccionado muestra caudal/utilización y el panel presenta demanda, abastecimiento y déficit de `resumen_capacidad`, validando su consistencia. El contrato está en [docs/contrato-api.md](docs/contrato-api.md). En la revisión actual no hubo tramos Sin dato; ese estado y el diagnóstico incompleto se conservan para respuestas parciales. No se modificó el frontend para consumir la respuesta completa de Matías.

## 6. Pruebas y resultados

**Backend: 28 pruebas aprobadas**, con `.venv\Scripts\python.exe -m unittest discover -s backend/tests -v`. Incluyen generación reproducible, inferencia individual/lotes, métricas ausentes o inválidas, topología desconectada, Kruskal de costo conocido, capacidades y conservación de flujo, y recorrido ASGI completo de los seis casos/escenarios. Un ejemplo dirigido requiere cancelar un flujo previo para alcanzar máximo 2; protege el uso correcto de la red residual. Las métricas de ML, su desglose y el signo de los residuos se comprueban con valores resueltos a mano.

**Frontend: 43 pruebas aprobadas**, más lint, TypeScript y build. Comprueban contrato, valores inválidos, balances, errores HTTP/timeout, escenarios/casos fuera de orden, cancelación, reintento, comparación sin tablas parciales, ausencia frente a cero, interacción por teclado y alternativa de tarjeta sin WebGL. Las pruebas frontend no prueban por sí solas los algoritmos del backend.

El ejemplo controlado PLANTA–A=70/A–B=35 tiene demanda A=20/B=30 y suministro total 50. Con demandas A=26/B=39 abastece A=26/B=35 y deja déficit 4. Así se distingue el agua en tránsito por una cañería del consumo de cada barrio. Es un caso exclusivo de pruebas, no una predicción fabricada del modelo.

Los resultados actuales de HTTP local, en m³/día, son:

| Caso | Crecimiento | Demanda | Suministro | Déficit |
| --- | --- | --- | --- | --- |
| Original | Base | 2167.62 | 1435.89 | 731.73 |
| Original | +10 % | 2192.42 | 1440.39 | 752.03 |
| Original | +30 % | 2242.09 | 1449.40 | 792.69 |
| Progresivo | Base | 2167.62 | 2167.62 | 0 |
| Progresivo | +10 % | 2192.42 | 2192.42 | 0 |
| Progresivo | +30 % | 2242.09 | 2195.00 | 47.09 |

El costo del MST es 73066.05 en ambos casos: solo cambian capacidades. La entrada progresiva llega aproximadamente al 99.9 % con +10 % y se satura con +30 %. La asignación máxima por barrio puede variar; pequeñas diferencias de centésimas pueden deberse al reparto y redondeo. No se exige un reparto único ni equitativo.

Edge con API local comprobó 17 nodos, 16 barrios, caudales, comparación y transición a déficit; a 390 px no hay desbordamiento de página. Una desconexión conserva el resultado identificado y permite recuperarlo al reintentar. Se probaron seis peticiones HTTP 200 y rechazo 422 de caso desconocido. No se atribuyen estos resultados al despliegue público mientras no se verifique su actualización.

Capturas: [tendidos](docs/capturas/tendidos-escritorio.png), [comparación progresiva local](docs/capturas/caso-progresivo-comparacion.png), [controles móviles locales](docs/capturas/caso-progresivo-movil.png). La captura de tendidos corresponde a la integración anterior con Render, con la misma geometría; las nuevas identifican el caso local.

La instalación limpia previa fue comprobada con versiones fijadas y entornos nuevos. El README permite levantar la demo desde otro entorno. Probar otra computadora sigue siendo recomendable, pero el enunciado no exige otro dataset ni un proveedor de hosting concreto.

## 7. Uso de inteligencia artificial

Esta sección se actualiza durante el desarrollo, como solicita el enunciado (página 3). Distingue asistentes de IA, herramientas de diseño y aportes propios del grupo.

### Herramientas y partes asistidas

| Herramienta o recurso | Uso en el trabajo |
| --- | --- |
| Codex | Análisis de la consigna, organización inicial, script del dataset sintético, esqueleto principal y desarrollo de la página React/TypeScript, cliente de API, pruebas e integración con Render. También se usó para revisar documentación y detectar diferencias entre lo escrito y lo implementado. |
| Codex, ampliación asumida por Ciro | Integración del CSV progresivo preparado por Matías, generador de su regla, selector de casos, suministro/déficit por barrio desde el backend, presentación/comparación en la web y pruebas ASGI, de invariantes y de interacción. Se conservaron el caso original y el modelo; los resultados se verificaron por HTTP y navegador locales. |
| Gemini | Apoyo a la arquitectura del backend y al diseño de API/esquemas, según el registro del grupo. Organización de los módulos `ml/`, `grafos/`, `api/` y contratos JSON para coordinar a los integrantes. |
| [Paletas de Colores](https://paletasdecolores.com.ar/) | Ciro usó esta herramienta para elegir la paleta `#44749d`, `#c6d4e1`, `#ffffff`, `#ebe7e0`, `#bdb8ad`, que después entregó al asistente para implementar los estilos. |
| Figma | Ciro lo exploró de forma preliminar para consultar diseños de páginas de temática parecida como referencia visual. No se afirma que se haya creado un prototipo completo ni utilizado funciones de IA. |
| [React Bits](https://reactbits.dev/) | Ciro eligió HoloCard, LatticeLoader y una referencia de TechText. Se integraron los dos primeros como código externo TypeScript/CSS adaptado con Codex, sin dependencias nuevas. TechText se dejó sin aplicar por no corresponder al grafo. La carta Pikachu procede de la demo oficial: no fue creada por el grupo ni por IA. Se conserva procedencia y licencia en `frontend/THIRD_PARTY_NOTICES.md`. |
| Proyecto web personal anterior de Ciro | Según su declaración, aportó inspiración y patrones de organización, pruebas y documentación para reducir la repetición de errores ya encontrados. Se incorporan como antecedente solo los aspectos presentes en este trabajo, detallados a continuación; no se atribuye a IA la autoría de su código previo. |

El aporte del asistente al frontend partió de un esqueleto principal y se fue ajustando a la consigna, la paleta elegida y las indicaciones de Ciro. Del proyecto personal anterior se tomaron como referencia los aspectos que tienen correspondencia en el repositorio actual:

- TypeScript y organización del frontend en `src/components/`, `src/lib/` y `src/tests/`.
- Separación de interfaz, comunicación con servicios y lógica de negocio: componentes/vistas, cliente en `src/api/` y cálculos de ML/grafos en el backend.
- Patrón de mocks para pruebas del cliente HTTP y de integración de la interfaz, incluidos errores y respuestas fuera de orden.
- Documentación de contexto y continuidad del trabajo, adaptada a `docs/context.md`, `docs/plan-frontend.md` y `AGENTS.md`.

Se registra la reutilización de estos criterios y patrones como antecedente informado por Ciro. No se inspeccionó el proyecto anterior ni se identificaron fragmentos concretos como copia literal; por eso no se atribuye a un archivo actual una procedencia de código que no se haya comprobado.

### Decisiones y responsabilidades del grupo

El grupo eligió el caso de estudio y el reparto de tareas; Ciro definió la dirección visual y revisó la interfaz, y Matías trabaja en backend, ML y grafos. La IA se usó como apoyo para generar y revisar propuestas, no como fuente de mediciones de una cooperativa real ni como sustituto de la comprensión del código. Los datos proceden del generador entregado, con reglas declaradas; las predicciones se calculan con el modelo del backend, no se redactan manualmente en la página.

Las herramientas visuales se registran por su aporte al diseño y no se clasifican automáticamente como IA. El código previo de Ciro se distingue del código generado/adaptado con asistencia. La revisión humana y la defensa de las decisiones corresponden a los integrantes.

### Ejemplos de instrucciones útiles

Los siguientes ejemplos resumen instrucciones de la conversación; se normalizó la redacción y no se presentan como transcripciones completas:

- Analizar el proyecto y la consigna, contrastarlos con la teoría y resumir qué falta y cómo conseguirlo o crearlo.
- Armar un contexto para agentes de código que se mantenga actualizado con las áreas de página, datos, ML, grafos y API.
- Crear la página usando la paleta proporcionada y mantener las predicciones y los algoritmos en el backend.
- Agregar pruebas de cosas que importan y detecten errores, evitando tests hechos únicamente para que pasen.
- Incorporar HoloCard en una pestaña especial y un indicador LatticeLoader durante el cálculo; aplicar TechText al grafo solo si resulta adecuado y consultar otras mejoras visuales.

Como ejemplo registrado para Gemini se conserva: «dame una estructura del proyecto (carpetas, archivos, etc) como para ir armando la base antes de hacer cualquier codigo».

### Errores de la IA detectados y cómo los resolvimos

Durante el desarrollo asistido por IA detectamos propuestas de código y pruebas que necesitaban corrección. El grupo revisó su comportamiento, reprodujo los problemas y aplicó los ajustes siguientes. Se documentan aquí como aprendizaje del uso de IA, sin atribuirlos como errores personales de un integrante.

| Error detectado | Cómo lo detectamos | Cómo lo resolvimos y verificamos |
| --- | --- | --- |
| Codificación categórica dependiente del lote | La misma zona industrial daba 10113.16 m³/mes individualmente y 10128.63 dentro de las 16 zonas. `drop_first=True` eliminaba la única categoría de una consulta individual. | En inferencia generamos las dummies sin eliminar categorías y alineamos con las columnas del modelo entrenado. Rechazamos tipos de zona fuera de los admitidos en el endpoint. Las pruebas comprueban igualdad entre predicciones individuales, lotes por tipo y lote completo para las tres categorías; el endpoint también conserva el resultado. No fue necesario reentrenar el modelo. |
| Prueba nueva de carga bloqueada por el reloj simulado | La prueba del loader agotó su tiempo por combinar el reloj simulado con la interacción asíncrona. TypeScript también detectó una opción de consulta no admitida en el test. | Se retiró la opción inválida y se separó la activación del evento del avance explícito del reloj. La prueba comprueba reinicio del contador, descarte de respuestas antiguas y retiro del loader ante error/éxito, manteniendo las aserciones de comportamiento. Se verificó con pruebas de comportamiento, lint, TypeScript y build. |
| Métricas fijas sin archivo de evaluación válido | Simulamos archivo ausente, JSON roto, campos incompletos y valores no finitos; la propuesta anterior devolvía cifras constantes o inválidas. | Quitamos los valores de respaldo y centralizamos lectura/validación del archivo real. Si no hay métricas válidas se devuelve `null`; la simulación sigue disponible y la página informa su ausencia. Se probaron ambas rutas, datos inválidos y un archivo válido con R² negativo. |
| Una prueba repetía Kruskal en vez de comprobar la función del proyecto | Al leer el test vimos otro bucle de ordenamiento y Union-Find dentro de la prueba: podía pasar aunque fallara la función utilizada por la API. | Reemplazamos ese bucle por un CSV temporal y una llamada a `calcular_red_menor_costo`. La expectativa independiente sigue siendo costo 6, tres aristas y árbol conexo sin ciclos. |
| Una prueba nueva trataba el orden de los extremos como dirección de una cañería | Falló la comparación de candidatos/MST porque Z03–Z04 y Z04–Z03 aparecían en distinto orden, aunque representan la misma conexión no dirigida. | Se normalizaron los extremos como conjunto y se mantuvieron comprobaciones independientes de costo/capacidad y del árbol. Las seis combinaciones por ASGI y la suite backend pasaron. No se alteró el grafo para satisfacer la prueba. |
| Documentación que afirmaba más de lo comprobado | Al contrastarla con el código aparecían un cuaderno vacío descrito como EDA, conteos viejos, resultados de distintas versiones y selección de modelo presentada como automática. | Se ordenaron guías e informe con el estado actual, se identificó la elección explícita del modelo y se separó implementación local de publicación. Se conservaron las cifras reproducidas y se precisaron los límites del análisis de errores. |
| Una red desconectada se presentaba como resultado completo | Un caso con PLANTA–A y B–C devolvía dos componentes sin avisar que no se conectaban todos los nodos. | Kruskal ahora verifica conexión de todos los nodos, incluidos los declarados sin aristas, y rechaza redes vacías/desconectadas. Pipeline y consulta MST pasan los nodos esperados; la API informa indisponibilidad con HTTP 503. Se agregaron casos de regresión para cada situación. |

Las pruebas de regresión reprodujeron los fallos antes de aplicar las correcciones y después pasaron. El estado actual está en [verificacion-proyecto.md](docs/verificacion-proyecto.md); registro local y publicación son estados diferentes.

**Desacierto visual del frontend:**

El único desacierto visual del frontend señalado por Ciro hasta esta revisión fue el indicador de estado tipo «live», que mostraba «Consultando API / API conectada», acompañado por la hora de última respuesta. El asistente lo agregó como parte de la presentación, pero Ciro consideró que no aportaba a la página y pidió quitarlo. Se eliminaron el distintivo y la hora; se conservan mensajes sencillos de cálculo y error para entender el estado de la simulación.

Ciro lo describió informalmente como «es algo que a la IA le gusta poner en páginas web por algún motivo». Se registra como una observación del integrante sobre esa propuesta concreta, no como una explicación técnica general del funcionamiento de la IA.

### Reflexión y verificaciones

La asistencia ayudó a pasar de archivos vacíos a una interfaz integrada, organizar el trabajo y preparar pruebas de escenarios, errores y respuestas desordenadas. La referencia visual y el código previo aportados por Ciro permitieron orientar el diseño hacia soluciones ya conocidas. El indicador «live» mostró que una propuesta de presentación puede resultar innecesaria aunque funcione: la selección de qué conservar la hizo el usuario.

También fue necesario contrastar el texto generado con el código: la presencia de una llamada a NetworkX no demuestra una implementación propia del algoritmo pedido, y las métricas escritas en una respuesta no prueban que se haya reproducido la evaluación. La IA facilita construir y revisar, pero no elimina las pruebas ni la necesidad de explicar cada parte en la defensa.

La suite actual de interfaz, lint, TypeScript y build pasó. Esto no garantiza ausencia de errores ni valida por sí solo la matemática del backend. Los aportes adicionales de IA de los integrantes se agregan solo si se confirman.

## 8. Limitaciones y posibles extensiones

Los efectos elegidos por Ciro se integraron sin alterar el cálculo de la red: HoloCard queda en una pestaña de exploración, cargada al abrirla, y LatticeLoader solo aparece durante solicitudes reales. Su contador incluye espera de red/servidor y no indica porcentaje de progreso. Se adaptaron textos en español, movimiento reducido y alternativa de imagen cuando no hay WebGL. La revisión en Edge comprobó reflejos/inclinación, pausa, móvil sin desbordamiento y regreso a Capacidad con 17 nodos/16 caudales de Render. Detalle: [efectos visuales](docs/efectos-visuales.md).

- Los datos no son mediciones reales: las métricas indican aprendizaje de las reglas sintéticas y no validan un sistema de abastecimiento real.
- Se usan promedios diarios obtenidos de un mes convencional de 30 días; no se modelan picos horarios, estacionalidad ni incertidumbre de las predicciones.
- La red representa capacidades y conectividad, no una simulación hidráulica de presiones, pérdidas de carga, diámetros o bombas.
- Se minimiza costo de conexión y luego se valida capacidad. El sistema todavía no propone ampliaciones ni optimiza simultáneamente costo y abastecimiento.
- El contrato original fue verificado en Render; no se confirmó la publicación del último código de casos/barrios ni del frontend.
- Se corrigieron localmente la inferencia por categorías, métricas de respaldo, test duplicado y control de desconexión; el detalle de error/detección/solución está en la sección de uso de IA. Falta publicar estas correcciones y repetir su validación por HTTP.
- El entrenamiento actual usa CV en entrenamiento y evaluación separada, justifica features y desglosa errores. Métricas, grupos y residuos tienen pruebas de valores conocidos. La exportación permanece fijada a la configuración elegida para este caso; no se busca el mejor modelo para cualquier dataset. Otra computadora y una referencia adicional serían verificaciones útiles, no requisitos funcionales nuevos.
- El flujo máximo prioriza cantidad total abastecida, sin restricciones de equidad. Un barrio puede recibir cero aunque la solución sea máxima; analizar reparto por zona sería una extensión.
- Posibles extensiones: datos reales adaptados y citados, curvas horarias, comparación de escenarios, incertidumbre, alternativas para reforzar tramos y análisis de costos de ampliación.

## 9. Instalación y ejecución

Las instrucciones están en [README.md](README.md), [frontend/README.md](frontend/README.md) y la [guía de instalación reproducible](docs/instalacion-reproducible.md). Las versiones están fijadas y se comprobó instalación limpia en una copia separada, además de las pruebas y compilación actuales. La demo actual se verificó con API local; una prueba adicional en otra computadora sigue siendo recomendable. La publicación prevista en Vercel está preparada, sin confirmación de despliegue actual.

El enunciado exige demo end-to-end e instrucciones reproducibles; no exige contratar servicios, un dominio, AWS Lambda ni publicar en un proveedor determinado. Vercel + Render es una decisión del grupo.
