# Informe — Diseño de infraestructura de red de agua

> Estado: borrador de trabajo. Completar cada sección a medida que se implementa y evalúa el proyecto.

Referencia de requisitos: `enunciado.pdf`, consignas generales y entregables en páginas 1–4 y trabajo «Diseño de infraestructura de red» en páginas 7–8. Revisión del 08/11/2026: [estado de cumplimiento y pendientes](docs/revision-consigna.md). Las descripciones siguientes distinguen implementación, resultados reportados y verificaciones pendientes.

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

El 08/11/2026 se comprobaron los CSV versionados: una planta, 16 zonas, 600 muestras y 26 conexiones; las etiquetas respetan la fórmula de crecimiento compuesto a cinco años con ruido artificial de ±5 %. También pasó el test existente de generación reproducible y conectividad. Esto valida el generador, no el aprendizaje del modelo ni los algoritmos de red.

### Conexiones posibles

Cada arista candidata debe indicar sus nodos extremos, costo de construcción y capacidad máxima de transporte.

`backend/app/data/generar_grafo.py` conecta cada barrio con sus vecinos horizontales y verticales y agrega dos enlaces posibles desde la planta: 26 aristas en total. El grafo candidato es conexo. La distancia se aproxima a partir de las coordenadas; el costo es distancia en metros × 10 × un factor de dificultad entre 0,9 y 1,25. Los enlaces de la planta reciben una capacidad de 2500 m³/día; el resto toma valores sintéticos de 750, 1200, 2000 o 3000 m³/día. Estas capacidades sirven para ensayar el algoritmo y no representan cálculos hidráulicos.

## 3. Modelo predictivo

**Objetivo:** Proyectar el consumo futuro de cada zona a partir de sus características disponibles al momento de predecir.

**Preparación de datos (Features):** `entrenar.py` descarta `nodo_id` y el objetivo `consumo_futuro` de las entradas. Codifica `tipo_zona` mediante *one-hot encoding*. El código conserva población, consumo histórico, crecimiento, coordenadas, fila y columna. Población, consumo, tipo de zona y crecimiento permiten describir la demanda; coordenadas, fila y columna son variables espaciales que todavía deben justificarse o excluirse en la revisión de features, ya que no participan directamente en la fórmula del objetivo sintético y algunas son redundantes.

**Metodología de entrenamiento:** Se utilizó la librería `scikit-learn` en Python. El dataset histórico de 600 registros se dividió aleatoriamente en un 80 % para entrenamiento y un 20 % para testeo.

El código usa semilla 42 y calcula las métricas sobre el conjunto separado. Ambos modelos se comparan sobre ese mismo test; falta separar la selección del modelo de la evaluación final. El archivo exporta explícitamente la regresión lineal, no realiza una selección automática. Las métricas siguientes fueron incorporadas por Matías; no se reprodujo el entrenamiento en esta revisión y la API todavía las devuelve como constantes.

**Modelos comparados:** Regresión lineal (`LinearRegression`) y árbol de decisión para regresión (`DecisionTreeRegressor`). Ambos están entre las familias permitidas por el enunciado (página 2). Se predice una cantidad de agua, por lo que es un problema de regresión, no de clasificación.

**Métricas obtenidas (sobre el 20 % de testeo):**
| Modelo | MAE | RMSE | R² |
| :--- | :--- | :--- | :--- |
| Regresión Lineal | 131.28 | 172.97 | 0.9939 |
| Árbol de Decisión | 197.95 | 308.79 | 0.9807 |

**Análisis de errores:** En las cifras reportadas, la regresión lineal tiene menor MAE y RMSE y mayor R² que el árbol; es el modelo exportado. Los errores se expresan en m³/mes. El ajuste alto es compatible con un dataset de reglas sintéticas conocidas, pero no demuestra desempeño sobre datos reales. La fórmula de generación tiene productos y crecimiento compuesto: no es estrictamente lineal en todas las entradas. Para justificar las diferencias entre modelos faltan analizar residuos, errores por tipo de zona y una referencia sencilla; las tres métricas globales no explican por sí solas la causa del resultado.

## 4. Algoritmos de grafos

### Red de menor costo
El problema se resuelve con un árbol de expansión mínima (MST): conectar planta y barrios minimizando la suma de costos de construcción. El enunciado pide implementar **Kruskal o Prim** (página 7).

**Código actual:** `mst.py` construye el grafo con NetworkX y delega el cálculo a `networkx.minimum_spanning_tree(..., weight='costo_unidades')`, sin seleccionar el algoritmo mediante un parámetro explícito. El comentario del archivo menciona Kruskal, pero no hay una implementación propia de sus pasos en el repositorio. Falta resolver ese punto con Matías conforme a la exigencia de implementar el algoritmo; no se presenta la llamada a biblioteca como desarrollo propio. NetworkX está sugerido para representar y leer/escribir grafos (página 3).

### Diagnóstico de capacidad
El objetivo es comparar la demanda proyectada con el máximo caudal que puede transportar la red elegida. El enunciado pide **Ford–Fulkerson o Edmonds–Karp** (página 7).

**Código actual:** `flujo.py` arma una red dirigida y llama a `networkx.maximum_flow` sin indicar `flow_func`. Aunque el comentario menciona Edmonds–Karp, esa llamada no documenta ni implementa explícitamente dicho algoritmo. Matías debe cerrar la implementación requerida y sus pruebas antes de atribuir el cálculo final a uno de los algoritmos pedidos.

**Representación de la red y compatibilización de unidades:**
1.  **Fuente y Sumidero:** Se definió el nodo `PLANTA` como el nodo fuente (source). Para representar la demanda simultánea de todos los barrios, se agregó un "súper sumidero" (super-sink) ficticio al grafo. Cada barrio se conectó a este sumidero general con una arista dirigida cuya capacidad máxima es exactamente su demanda predicha.
2.  **Unidades:** Dado que la capacidad máxima de las conexiones candidatas está expresada en m³/día, la proyección de consumo futuro mensual de los nodos devuelta por el modelo se dividió por 30 para obtener una demanda diaria y poder operar de forma coherente en el grafo.

**Integración efectiva de predicciones y grafos:** las predicciones determinan la demanda de cada barrio y la capacidad de su conexión al supersumidero. Así pueden cambiar el flujo máximo y el déficit. El MST usa costos fijos y no recibe las demandas como pesos: cambiar el escenario no tiene por qué modificar sus conexiones. Esto es coherente con diseñar primero por costo y después validar capacidad; no es una optimización conjunta de costo y abastecimiento.

## 5. Integración y aplicación web

El sistema se desarrolló utilizando un monorepo que separa la lógica de cálculo pesada de la interfaz de usuario:

**Backend (API + ML + Grafos):** Construido en Python y FastAPI. Centraliza la inferencia y los cálculos de redes. El pipeline recibe el escenario de crecimiento, recalcula demandas, obtiene el MST y el flujo, y devuelve parte de los resultados como JSON. Todavía descarta el suministro total y filtra los flujos antes de construir la respuesta.

**Frontend (Interfaz de Usuario):** Implementado en React, TypeScript estricto y Vite, con CSS propio y gráfico SVG. Consume `POST /api/simular-red` del servicio de Render y ofrece:

- Tendidos: 26 conexiones candidatas del caso, red de menor costo resaltada, costo y selección de nodos/aristas con detalle.
- Capacidad: flujo y utilización de los tramos informados, distinguiendo cercanía desde 90 % y saturación al 100 %. Los tramos no devueltos se muestran como **Sin dato**, sin asumir flujo cero.
- Escenarios base, +10 % y +30 % que multiplican la tasa de crecimiento poblacional del predictor actual. No equivalen a aumentar directamente la demanda en esos porcentajes.
- Tabla con búsqueda, acceso por teclado, estados de carga/error/reintento y protección frente a respuestas fuera de orden. En móvil el gráfico conserva etiquetas legibles con desplazamiento interno.

La API todavía omite planta y candidatos: la página complementa su geometría/costos/capacidades con los CSV versionados, comprobando coincidencia con los barrios y tendidos recibidos. No calcula predicciones ni algoritmos. Si la red no coincide, descarta ese complemento. La aplicación no contiene un fallback a resultados simulados. El suministro y el déficit total no se muestran porque el contrato todavía no los incluye.

La interfaz está verificada localmente con la API desplegada. Su publicación en Vercel sigue pendiente.

**Avance de cierre del frontend:** cada tendido seleccionado muestra su caudal y utilización en el gráfico, o indica **Sin dato**. Se preparó un panel de demanda, suministro, déficit y cobertura para el campo opcional `resumen_capacidad`, validando consistencia antes de presentarlo. El contrato se documenta en [docs/contrato-api.md](docs/contrato-api.md). El servicio actual todavía no entrega ese resumen ni todos los flujos: la pantalla informa diagnóstico incompleto. La integración final sigue pendiente de datos reales del backend, sin activar ejemplos en producción.

## 6. Pruebas y resultados

**Ejecución de la Red de Menor Costo reportada por Matías:**
Al ejecutar el algoritmo sobre las 26 aristas candidatas generadas, el sistema seleccionó exitosamente 16 conexiones (el mínimo necesario para conectar la planta y los 16 barrios sin formar ciclos). El costo total proyectado para esta obra fue de 73066.05 unidades.

**Ejecución de Diagnóstico de Capacidad reportada por Matías:**
Se realizó una simulación base incrementando artificialmente el consumo histórico en un 20% para forzar el comportamiento de la red. Los resultados demostraron que el sistema detecta correctamente los cuellos de botella:
- **Agua requerida:** 2351.52 m³/día.
- **Agua abastecida (Flujo Máximo):** 1441.97 m³/día.
- **Diagnóstico:** Déficit hídrico. La red de menor costo no posee la capacidad suficiente para esta demanda proyectada.
- **Tramos Críticos:** Se reportaron 2 aristas saturadas al 100% de su capacidad: `Z01 <-> Z05` (1200 m³/día) y `Z05 <-> Z06` (750 m³/día).

Estos valores corresponden a la ejecución de backend descrita por Matías, con consumo alterado para el ejemplo; no son el escenario base HTTP actual. Faltan tests matemáticos con resultados conocidos y revisar la selección/implementación de algoritmos antes de atribuirlos a Kruskal o Edmonds–Karp.

**Verificación del frontend e integración real (08/11/2026):** 33 pruebas aprobadas de contrato, cliente e interacción. Cubren datos inválidos, capacidades incompatibles, HTTP fallido y timeout, cero frente a dato ausente, respuestas desordenadas, error/reintento, conservación del escenario anterior, etiquetas de todos los tendidos y balances inconsistentes. Pasaron lint y build con TypeScript estricto. Estas pruebas no validan los algoritmos del backend.

Un caso mínimo exclusivo de tests fija demandas A=20/B=30 y obtiene suministro 50/déficit 0; otra respuesta fija A=26/B=39 y suministro 61/déficit 4 sobre capacidades PLANTA–A=70/A–B=35. La interfaz presenta ambos balances y cambia el diagnóstico al recibirlos. Son respuestas controladas con resultado conocido; no son predicciones del modelo ni pruebas ejecutadas contra el servicio publicado.

En Edge con Render real se comprobaron 17 nodos dibujados, 26 conexiones candidatas y 16 tendidos MST. La demanda base sumada fue 2167.74 m³/día, con costo 73066.05 unidades. El escenario de +30 % en la tasa mostró 2242.3 m³/día. Se verificaron 16 etiquetas de tendidos: solo se recibieron dos registros de flujo en base; 14 quedan como Sin dato y el diagnóstico como incompleto. A 390 px no se observó desbordamiento horizontal de la página. Se renovaron las capturas tras retirar el indicador live y añadir caudales.

La instalación de dependencias pasó con `npm ci` offline en una copia aislada y el lockfile entregado. Sus pruebas/build no pudieron completarse por permisos de Windows; las comprobaciones aprobadas corresponden al proyecto principal. El arranque desde otra máquina y la demo con el contrato final siguen pendientes.

Capturas de esa revisión, sin resultados fabricados:

- [Tendidos y detalle](docs/capturas/tendidos-escritorio.png).
- [Capacidad y tramos sin dato](docs/capturas/capacidad-escritorio.png).
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

Como ejemplo registrado para Gemini se conserva: «dame una estructura del proyecto (carpetas, archivos, etc) como para ir armando la base antes de hacer cualquier codigo».

### Desacierto visual detectado y corrección

El único desacierto visual del frontend señalado por Ciro hasta esta revisión fue el indicador de estado tipo «live», que mostraba «Consultando API / API conectada», acompañado por la hora de última respuesta. El asistente lo agregó como parte de la presentación, pero Ciro consideró que no aportaba a la página y pidió quitarlo. Se eliminaron el distintivo y la hora; se conservan mensajes sencillos de cálculo y error para entender el estado de la simulación.

Ciro lo describió informalmente como «es algo que a la IA le gusta poner en páginas web por algún motivo». Se registra como una observación del integrante sobre esa propuesta concreta, no como una explicación técnica general del funcionamiento de la IA.

### Reflexión y verificaciones

La asistencia ayudó a pasar de archivos vacíos a una interfaz integrada, organizar el trabajo y preparar pruebas de escenarios, errores y respuestas desordenadas. La referencia visual y el código previo aportados por Ciro permitieron orientar el diseño hacia soluciones ya conocidas. El indicador «live» mostró que una propuesta de presentación puede resultar innecesaria aunque funcione: la selección de qué conservar la hizo el usuario.

También fue necesario contrastar el texto generado con el código: la presencia de una llamada a NetworkX no demuestra una implementación propia del algoritmo pedido, y las métricas escritas en una respuesta no prueban que se haya reproducido la evaluación. La IA facilita construir y revisar, pero no elimina las pruebas ni la necesidad de explicar cada parte en la defensa.

Después de quitar el indicador pasaron nuevamente las 22 pruebas del frontend, lint, TypeScript y build. Eso no garantiza ausencia de otros errores ni valida la matemática del backend. Se completaron las referencias de paleta, uso exploratorio de Figma y patrones del proyecto previo según la aclaración de Ciro. Antes de entregar falta revisar el registro de uso de IA del trabajo de Matías si hubo otras intervenciones.

## 8. Limitaciones y posibles extensiones

- Los datos no son mediciones reales: las métricas indican aprendizaje de las reglas sintéticas y no validan un sistema de abastecimiento real.
- Se usan promedios diarios obtenidos de un mes convencional de 30 días; no se modelan picos horarios, estacionalidad ni incertidumbre de las predicciones.
- La red representa capacidades y conectividad, no una simulación hidráulica de presiones, pérdidas de carga, diámetros o bombas.
- Se minimiza costo de conexión y luego se valida capacidad. El sistema todavía no propone ampliaciones ni optimiza simultáneamente costo y abastecimiento.
- La API omite parte de la geometría, la mayoría de los flujos y el suministro/déficit total. La página identifica lo ausente; completar esos campos y su visualización sigue pendiente.
- Faltan cerrar la implementación de los algoritmos exigidos, sus tests con resultados conocidos, la evaluación final reproducible de ML y un arranque desde un entorno limpio con dependencias compatibles con el modelo.
- Posibles extensiones: datos reales adaptados y citados, curvas horarias, comparación de escenarios, incertidumbre, alternativas para reforzar tramos y análisis de costos de ampliación.

## 9. Instalación y ejecución

Las instrucciones están en [README.md](README.md) y [frontend/README.md](frontend/README.md). La página local usa la API ya desplegada en Render; falta comprobar el arranque completo desde un entorno limpio, fijar dependencias del backend y completar la publicación prevista en Vercel.

El enunciado exige demo end-to-end e instrucciones reproducibles; no exige contratar servicios, un dominio, AWS Lambda ni publicar en un proveedor determinado. Vercel + Render es una decisión del grupo.
