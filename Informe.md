# Informe — Diseño de infraestructura de red de agua

> Estado: borrador de trabajo. Completar cada sección a medida que se implementa y evalúa el proyecto.

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

El conjunto de prueba permitirá medir cuánto aprende un modelo de **estas reglas simuladas**. Sus métricas no demostrarán precisión sobre consumo real.

Este procedimiento sigue la alternativa de dataset sintético admitida por el enunciado (página 2): se entrega el script generador, se declaran las dependencias entre variables y se fija una semilla para reproducir el caso. Las columnas propuestas en la página 7 están en `historial_consumo.csv`; `zonas.csv` omite intencionalmente `consumo_futuro`, porque contiene las zonas para las que hay que predecirlo. `fila` y `columna` son columnas adicionales para construir la cuadrícula; las tablas del enunciado permiten agregar campos.

Se comprobaron los CSV versionados: una planta, 16 zonas, 600 muestras y 26 conexiones; las etiquetas respetan la fórmula de crecimiento compuesto a cinco años con ruido artificial de ±5 %. También pasó el test de generación reproducible y conectividad. Esto valida el generador, no el aprendizaje del modelo ni los algoritmos de red.

### Conexiones posibles

Cada arista candidata debe indicar sus nodos extremos, costo de construcción y capacidad máxima de transporte.

`backend/app/data/generar_grafo.py` conecta cada barrio con sus vecinos horizontales y verticales y agrega dos enlaces posibles desde la planta: 26 aristas en total. El grafo candidato es conexo. La distancia se aproxima a partir de las coordenadas; el costo es distancia en metros × 10 × un factor de dificultad entre 0,9 y 1,25. Los enlaces de la planta reciben una capacidad de 2500 m³/día; el resto toma valores sintéticos de 750, 1200, 2000 o 3000 m³/día. Estas capacidades sirven para ensayar el algoritmo y no representan cálculos hidráulicos.

## 3. Modelo predictivo

**Objetivo:** Proyectar el consumo futuro de cada zona a partir de sus características disponibles al momento de predecir.

**Preparación de datos (Features):** `entrenar.py` descarta `nodo_id` y el objetivo `consumo_futuro` de las entradas. Codifica `tipo_zona` mediante *one-hot encoding*. El código conserva población, consumo histórico, crecimiento, coordenadas, fila y columna. Población, consumo, tipo de zona y crecimiento permiten describir la demanda; coordenadas, fila y columna son variables espaciales que todavía deben justificarse o excluirse en la revisión de features, ya que no participan directamente en la fórmula del objetivo sintético y algunas son redundantes.

**Metodología de entrenamiento:** Se utilizó la librería `scikit-learn` en Python. El dataset histórico de 600 registros se dividió aleatoriamente en un 80 % para entrenamiento y un 20 % para testeo.

El código usa semilla 42 y calcula las métricas sobre el conjunto separado. Ambos modelos se comparan sobre ese mismo test: falta separar la elección del modelo de la evaluación final. El script exporta explícitamente la regresión lineal a `backend/models/modelo_consumo.joblib` y escribe métricas en `backend/models/metricas.json`. La API lee y valida ese archivo; si falta o es inválido devuelve `null`, sin cifras de respaldo. La corrección se explica en la sección de errores de IA.

**Modelos comparados:** Regresión lineal (`LinearRegression`) y árbol de decisión para regresión (`DecisionTreeRegressor`). Ambos están entre las familias permitidas por el enunciado (página 2). Se predice una cantidad de agua, por lo que es un problema de regresión, no de clasificación.

**Métricas obtenidas (sobre el 20 % de testeo):**
| Modelo | MAE | RMSE | R² |
| :--- | :--- | :--- | :--- |
| Regresión Lineal | 131.28 | 172.97 | 0.9939 |
| Árbol de Decisión | 197.95 | 308.79 | 0.9807 |

**Análisis de errores:** En las cifras reproducidas, la regresión lineal tiene menor MAE y RMSE y mayor R² que el árbol; es el modelo exportado. Los errores se expresan en m³/mes. El ajuste alto es compatible con un dataset de reglas sintéticas conocidas, pero no demuestra desempeño sobre datos reales. La fórmula de generación tiene productos y crecimiento compuesto: no es estrictamente lineal en todas las entradas. Para profundizar el análisis entre modelos se recomienda a futuro evaluar residuos, errores por tipo de zona y una referencia sencilla.

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

La interfaz está verificada localmente con la API desplegada. Su publicación en Vercel sigue pendiente.

**Integración verificada:** cada tendido seleccionado muestra caudal/utilización y el panel presenta demanda, abastecimiento y déficit de `resumen_capacidad`, validando su consistencia. El contrato está en [docs/contrato-api.md](docs/contrato-api.md). En la revisión actual no hubo tramos Sin dato; ese estado y el diagnóstico incompleto se conservan para respuestas parciales. No se modificó el frontend para consumir la respuesta completa de Matías.

## 6. Pruebas y resultados

**Ejecución de la Red de Menor Costo reportada por Matías:**
Al ejecutar el algoritmo sobre las 26 aristas candidatas generadas, el sistema seleccionó exitosamente 16 conexiones (el mínimo necesario para conectar la planta y los 16 barrios sin formar ciclos). El costo total proyectado para esta obra fue de 73066.05 unidades.

**Registro histórico de diagnóstico reportado por Matías, distinto del caso actual:**
Se realizó una simulación base incrementando artificialmente el consumo histórico en un 20% para forzar el comportamiento de la red. Los resultados demostraron que el sistema detecta correctamente los cuellos de botella:
- **Agua requerida:** 2351.52 m³/día.
- **Agua abastecida (Flujo Máximo):** 1441.97 m³/día.
- **Diagnóstico:** Déficit hídrico. La red de menor costo no posee la capacidad suficiente para esta demanda proyectada.
- **Tramos Críticos:** Se reportaron 2 aristas saturadas al 100% de su capacidad: `Z01 <-> Z05` (1200 m³/día) y `Z05 <-> Z06` (750 m³/día).

Esas cifras se conservan como registro de la ejecución descrita por Matías, con consumo alterado; no se reprodujeron en esta revisión ni son el escenario HTTP base actual. Los resultados actuales se presentan más abajo.

**Verificación del backend:** 22 pruebas aprobadas mediante `.venv\Scripts\python.exe -m unittest discover -s backend/tests -v`. Cubren datos, Union-Find, Kruskal productivo con costo conocido e invariantes de la red real, flujo conocido PLANTA–A–B, conservación, pipeline y regresiones de inferencia/métricas/desconexión. Los tests de rutas llaman funciones directamente; la verificación HTTP se realiza por separado. El detalle de los problemas y sus correcciones está en la sección de errores de IA.

Se reprodujeron en memoria las métricas de ambos modelos con los datos y split declarados, sin sobrescribir el modelo ni los JSON versionados; coinciden con la tabla de la sección 3. La instalación nueva del backend en `.venv` y la ejecución de la suite pasaron con Python 3.12.10 y scikit-learn 1.9.1.

**Verificación del frontend e integración real:** 33 pruebas aprobadas de contrato, cliente e interacción. Cubren datos inválidos, capacidades incompatibles, HTTP fallido y timeout, cero frente a dato ausente, respuestas desordenadas, error/reintento, conservación del escenario anterior, etiquetas de todos los tendidos y balances inconsistentes. Pasaron lint y build con TypeScript estricto. Estas pruebas no validan los algoritmos del backend.

Un caso mínimo exclusivo de tests fija demandas A=20/B=30 y obtiene suministro 50/déficit 0; otra respuesta fija A=26/B=39 y suministro 61/déficit 4 sobre capacidades PLANTA–A=70/A–B=35. La interfaz presenta ambos balances y cambia el diagnóstico al recibirlos. Son respuestas controladas con resultado conocido; no son predicciones del modelo ni pruebas ejecutadas contra el servicio publicado.

En Edge con Render real se comprobaron 17 nodos, 26 candidatos, 16 tendidos y 16 caudales, sin tramos Sin dato. La pantalla muestra déficit en los tres escenarios. A 390 px no se observó desbordamiento horizontal de la página. Se renovaron las capturas con el contrato completo.

| Escenario de tasa poblacional | Demanda m³/día | Abastecido m³/día | Déficit m³/día |
| --- | --- | --- | --- |
| Base | 2167.74 | 1435.18 | 732.56 |
| +10 % | 2192.58 | 1439.69 | 752.89 |
| +30 % | 2242.26 | 1448.71 | 793.55 |

Los tres POST respondieron HTTP 200 con contrato completo. En base se observó una arista saturada; una asignación de flujo distinta a la histórica puede ser igualmente máxima. No se interpreta que un tramo con flujo cero esté sin información ni que el objetivo garantice reparto equitativo entre barrios.

Se fijaron versiones de dependencias Python compatibles con el modelo y Node 24.x con lockfile para frontend. En una copia separada, con `.venv` y `node_modules` nuevos, pasaron instalación, `pip check`, 22 pruebas backend, 33 frontend, lint y build con TypeScript. npm usó la caché disponible; los permisos adecuados resolvieron el bloqueo de la comprobación anterior. La integración con el contrato completo ya se verificó en la página local y Render; falta repetir el arranque y recorrido desde otra computadora y publicar el frontend previsto.

Capturas de esa revisión, sin resultados fabricados:

- [Tendidos y detalle](docs/capturas/tendidos-escritorio.png).
- [Capacidad, caudales y déficit real](docs/capturas/capacidad-escritorio.png).
- [Gráfico en móvil](docs/capturas/red-movil.png).

## 7. Uso de inteligencia artificial

Esta sección se actualiza durante el desarrollo, como solicita el enunciado (página 3). Distingue asistentes de IA, herramientas de diseño y aportes propios del grupo.

### Herramientas y partes asistidas

| Herramienta o recurso | Uso en el trabajo |
| --- | --- |
| Codex | Análisis de la consigna, organización inicial, script del dataset sintético, esqueleto principal y desarrollo de la página React/TypeScript, cliente de API, pruebas e integración con Render. También se usó para revisar documentación y detectar diferencias entre lo escrito y lo implementado. |
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
| Prueba nueva de carga bloqueada por el reloj simulado | La prueba del loader agotó su tiempo por combinar el reloj simulado con la interacción asíncrona. TypeScript también detectó una opción de consulta no admitida en el test. | Se retiró la opción inválida y se separó la activación del evento del avance explícito del reloj. La prueba comprueba reinicio del contador, descarte de respuestas antiguas y retiro del loader ante error/éxito, manteniendo las aserciones de comportamiento. Pasaron las 37 pruebas frontend, lint, TypeScript y build. |
| Métricas fijas sin archivo de evaluación válido | Simulamos archivo ausente, JSON roto, campos incompletos y valores no finitos; la propuesta anterior devolvía cifras constantes o inválidas. | Quitamos los valores de respaldo y centralizamos lectura/validación del archivo real. Si no hay métricas válidas se devuelve `null`; la simulación sigue disponible y la página informa su ausencia. Se probaron ambas rutas, datos inválidos y un archivo válido con R² negativo. |
| Una prueba repetía Kruskal en vez de comprobar la función del proyecto | Al leer el test vimos otro bucle de ordenamiento y Union-Find dentro de la prueba: podía pasar aunque fallara la función utilizada por la API. | Reemplazamos ese bucle por un CSV temporal y una llamada a `calcular_red_menor_costo`. La expectativa independiente sigue siendo costo 6, tres aristas y árbol conexo sin ciclos. |
| Una red desconectada se presentaba como resultado completo | Un caso con PLANTA–A y B–C devolvía dos componentes sin avisar que no se conectaban todos los nodos. | Kruskal ahora verifica conexión de todos los nodos, incluidos los declarados sin aristas, y rechaza redes vacías/desconectadas. Pipeline y consulta MST pasan los nodos esperados; la API informa indisponibilidad con HTTP 503. Se agregaron casos de regresión para cada situación. |

Las pruebas de regresión reprodujeron los fallos antes de aplicar las correcciones. Después pasaron las **22 pruebas del backend**, incluyendo el test de Kruskal que ahora llama al código real. Los cambios se agrupan en commits locales por tema; el usuario realiza el push y todavía falta verificar las correcciones desplegadas. El estado de verificación está en [verificacion-proyecto.md](docs/verificacion-proyecto.md).

**Desacierto visual del frontend:**

El único desacierto visual del frontend señalado por Ciro hasta esta revisión fue el indicador de estado tipo «live», que mostraba «Consultando API / API conectada», acompañado por la hora de última respuesta. El asistente lo agregó como parte de la presentación, pero Ciro consideró que no aportaba a la página y pidió quitarlo. Se eliminaron el distintivo y la hora; se conservan mensajes sencillos de cálculo y error para entender el estado de la simulación.

Ciro lo describió informalmente como «es algo que a la IA le gusta poner en páginas web por algún motivo». Se registra como una observación del integrante sobre esa propuesta concreta, no como una explicación técnica general del funcionamiento de la IA.

### Reflexión y verificaciones

La asistencia ayudó a pasar de archivos vacíos a una interfaz integrada, organizar el trabajo y preparar pruebas de escenarios, errores y respuestas desordenadas. La referencia visual y el código previo aportados por Ciro permitieron orientar el diseño hacia soluciones ya conocidas. El indicador «live» mostró que una propuesta de presentación puede resultar innecesaria aunque funcione: la selección de qué conservar la hizo el usuario.

También fue necesario contrastar el texto generado con el código: la presencia de una llamada a NetworkX no demuestra una implementación propia del algoritmo pedido, y las métricas escritas en una respuesta no prueban que se haya reproducido la evaluación. La IA facilita construir y revisar, pero no elimina las pruebas ni la necesidad de explicar cada parte en la defensa.

Después de quitar el indicador pasaron nuevamente las 22 pruebas del frontend, lint, TypeScript y build. Eso no garantiza ausencia de otros errores ni valida la matemática del backend. Se completaron las referencias de paleta, uso exploratorio de Figma y patrones del proyecto previo según la aclaración de Ciro. Antes de entregar falta revisar el registro de uso de IA del trabajo de Matías si hubo otras intervenciones.

## 8. Limitaciones y posibles extensiones

Los efectos elegidos por Ciro se integraron sin alterar el cálculo de la red: HoloCard queda en una pestaña de exploración, cargada al abrirla, y LatticeLoader solo aparece durante solicitudes reales. Su contador incluye espera de red/servidor y no indica porcentaje de progreso. Se adaptaron textos en español, movimiento reducido y alternativa de imagen cuando no hay WebGL. La revisión en Edge comprobó reflejos/inclinación, pausa, móvil sin desbordamiento y regreso a Capacidad con 17 nodos/16 caudales de Render. Detalle: [efectos visuales](docs/efectos-visuales.md).

- Los datos no son mediciones reales: las métricas indican aprendizaje de las reglas sintéticas y no validan un sistema de abastecimiento real.
- Se usan promedios diarios obtenidos de un mes convencional de 30 días; no se modelan picos horarios, estacionalidad ni incertidumbre de las predicciones.
- La red representa capacidades y conectividad, no una simulación hidráulica de presiones, pérdidas de carga, diámetros o bombas.
- Se minimiza costo de conexión y luego se valida capacidad. El sistema todavía no propone ampliaciones ni optimiza simultáneamente costo y abastecimiento.
- El contrato completo ya está publicado en Render y verificado desde la página local. La publicación del frontend sigue pendiente.
- Se corrigieron localmente la inferencia por categorías, métricas de respaldo, test duplicado y control de desconexión; el detalle de error/detección/solución está en la sección de uso de IA. Falta publicar estas correcciones y repetir su validación por HTTP.
- Falta separar selección/evaluación final de ML y profundizar análisis de errores. Las dependencias compatibles ya están fijadas; falta comprobar la instalación en otra computadora.
- El flujo máximo prioriza cantidad total abastecida, sin restricciones de equidad. Un barrio puede recibir cero aunque la solución sea máxima; analizar reparto por zona sería una extensión.
- Posibles extensiones: datos reales adaptados y citados, curvas horarias, comparación de escenarios, incertidumbre, alternativas para reforzar tramos y análisis de costos de ampliación.

## 9. Instalación y ejecución

Las instrucciones están en [README.md](README.md), [frontend/README.md](frontend/README.md) y la [guía de instalación reproducible](docs/instalacion-reproducible.md). Las versiones están fijadas y se verificaron backend/frontend en una copia nueva, sus pruebas y compilación, además de la página local con Render. Falta comprobar el recorrido completo en otra computadora y completar la publicación prevista en Vercel; su configuración de build ya está preparada.

El enunciado exige demo end-to-end e instrucciones reproducibles; no exige contratar servicios, un dominio, AWS Lambda ni publicar en un proveedor determinado. Vercel + Render es una decisión del grupo.
