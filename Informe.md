# Informe — Diseño de infraestructura de red de agua

> Estado: borrador de trabajo. Completar cada sección a medida que se implementa y evalúa el proyecto.

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

### Conexiones posibles

Cada arista candidata debe indicar sus nodos extremos, costo de construcción y capacidad máxima de transporte.

`backend/app/data/generar_grafo.py` conecta cada barrio con sus vecinos horizontales y verticales y agrega dos enlaces posibles desde la planta: 26 aristas en total. El grafo candidato es conexo. La distancia se aproxima a partir de las coordenadas; el costo es distancia en metros × 10 × un factor de dificultad entre 0,9 y 1,25. Los enlaces de la planta reciben una capacidad de 2500 m³/día; el resto toma valores sintéticos de 750, 1200, 2000 o 3000 m³/día. Estas capacidades sirven para ensayar el algoritmo y no representan cálculos hidráulicos.

## 3. Modelo predictivo

**Objetivo:** Proyectar el consumo futuro de cada zona a partir de sus características disponibles al momento de predecir.

**Preparación de datos (Features):** Se descartó la variable `nodo_id` por ser un identificador sin valor predictivo. La variable categórica `tipo_zona` (residencial, comercial, industrial) se procesó utilizando *One-Hot Encoding* para que el modelo pueda interpretarla matemáticamente. Como dicta la buena práctica, no se utilizó `consumo_futuro` como variable de entrada.

**Metodología de entrenamiento:** Se utilizó la librería `scikit-learn` en Python. El dataset histórico de 600 registros se dividió aleatoriamente en un 80 % para entrenamiento y un 20 % para testeo.

**Modelos comparados:** Para resolver este problema de regresión continua, se entrenaron y compararon dos modelos: Regresión Lineal y Árboles de Decisión[cite: 2].

**Métricas obtenidas (sobre el 20 % de testeo):**
| Modelo | MAE | RMSE | R² |
| :--- | :--- | :--- | :--- |
| Regresión Lineal | 131.28 | 172.97 | 0.9939 |
| Árbol de Decisión | 197.95 | 308.79 | 0.9807 |

**Análisis de errores:** Ambos modelos lograron un ajuste excelente ($R^{2} > 0.98$), lo cual es esperable dado que los datos son sintéticos y el modelo logra descubrir las reglas que se usaron para generarlos[cite: 2]. Sin embargo, la Regresión Lineal superó al Árbol de Decisión, presentando un error medio absoluto (MAE) menor y un error cuadrático medio (RMSE) mucho más bajo. Esto ocurre porque la regla de generación subyacente (consumo base multiplicado por una tasa de crecimiento constante) describe un comportamiento que la regresión lineal capta de forma natural, mientras que el árbol de decisión intenta aproximarlo mediante escalones discretos. Por lo tanto, el modelo elegido para exportar a la API es la **Regresión Lineal**.

## 4. Algoritmos de grafos

### Red de menor costo
Se implementó el algoritmo de **[Kruskal / Prim - A completar cuál elegiste]** mediante la librería `networkx` sobre las conexiones candidatas[cite: 3]. Este algoritmo calcula el Árbol de Expansión Mínima (MST), permitiendo encontrar la red que conecta a todos los barrios con el menor costo total de construcción posible[cite: 7].

### Diagnóstico de capacidad
Se aplicó el algoritmo de **[Ford-Fulkerson / Edmonds-Karp - A completar cuál elegiste]** sobre la red seleccionada por el paso anterior[cite: 7]. El objetivo fue comparar el flujo máximo de agua que puede transitar por las tuberías contra la demanda proyectada, identificando aristas saturadas[cite: 7].

**Representación de la red y compatibilización de unidades:**
1.  **Fuente y Sumidero:** Se definió el nodo `PLANTA` como el nodo fuente (source). Para representar la demanda simultánea de todos los barrios, se agregó un "súper sumidero" (super-sink) ficticio al grafo. Cada barrio se conectó a este sumidero general con una arista dirigida cuya capacidad máxima es exactamente su demanda predicha.
2.  **Unidades:** Dado que la capacidad máxima de las conexiones candidatas está expresada en m³/día, la proyección de consumo futuro mensual de los nodos devuelta por el modelo se dividió por 30 para obtener una demanda diaria y poder operar de forma coherente en el grafo.

## 5. Integración y aplicación web

El sistema se desarrolló utilizando un monorepo que separa la lógica de cálculo pesada de la interfaz de usuario:

**Backend (API + ML + Grafos):** Construido en Python utilizando FastAPI[cite: 3]. Centraliza los datos procesados, la inferencia del modelo predictivo y la lógica de redes (`networkx`). Expone un pipeline que recibe un escenario desde el usuario (ej. +10% de crecimiento)[cite: 8], recalcula las demandas, reconstruye el MST, corre el flujo máximo y devuelve el diagnóstico empaquetado en formato JSON.

**Frontend (Interfaz de Usuario):** Construido con React y TypeScript[cite: 3]. Consume la API y provee:
- Una visualización de los tendidos posibles, con la red de menor costo resaltada[cite: 7].
- Una vista de la red con el flujo sobre cada arista, coloreando de rojo aquellas saturadas o próximas a su capacidad máxima[cite: 8].
- Un selector de escenarios de crecimiento poblacional que recalcula en tiempo real el diagnóstico[cite: 8].

## 6. Pruebas y resultados

**Pendiente:** Registrar casos de prueba de los algoritmos, métricas del modelo, resultados observados de los escenarios (+10%, +30%) y adjuntar las capturas de pantalla del frontend interactivo funcionando[cite: 4, 8].

## 7. Uso de inteligencia artificial

A lo largo del proyecto se utilizaron herramientas de IA como apoyo técnico:

- **Codex:** Se usó en la etapa inicial para proponer el caso sintético, organizar el borrador del informe y escribir el script base `generar_dataset.py`.
- **Gemini:** Se utilizó como asistente de arquitectura de software y diseño de APIs.
  - *Prompt clave:* "dame una estructura del proyecto (carpetas, archivos, etc) como para ir armando la base antes de hacer cualquier codigo".
  - *Uso e impacto:* Ayudó a definir un monorepo escalable, modulando internamente el backend en `ml/`, `grafos/` y `api/` para cumplir con la consigna de centralizar la lógica y exponerla a React sin romper la regla de usar una única API[cite: 2]. También asistió generando los contratos JSON (esquemas de Pydantic) para poder paralelizar el trabajo entre los dos integrantes del grupo.

*Reflexión:* *[A completar: Casos en los que la IA se equivocó, alucinó una librería o propuso algo incorrecto, y cómo lo solucionaron. Breve reflexión general]*

## 8. Limitaciones y posibles extensiones

**Pendiente:** Documentar las simplificaciones de datos (parámetros puramente didácticos) y del modelo de red, qué conclusiones permiten los resultados y qué mejoras se podrían hacer (por ejemplo, modelar curvas de demanda horaria en lugar de promedios diarios estáticos).

## 9. Instalación y ejecución

Las instrucciones para levantar el proyecto desde cualquier entorno se documentaron en el archivo `README.md` ubicado en la raíz del repositorio[cite: 4].