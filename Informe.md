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

**Objetivo:** proyectar el consumo futuro de cada zona a partir de sus características disponibles al momento de predecir.

**Pendiente:** describir variables de entrada, preparación de datos, modelo elegido, separación de entrenamiento y prueba, y resultados de MAE, RMSE y R². Agregar una comparación sencilla y analizar los errores. Evitar usar `consumo_futuro` como variable de entrada.

## 4. Algoritmos de grafos

### Red de menor costo

Implementar Kruskal o Prim sobre las conexiones candidatas. Registrar el costo total y las aristas seleccionadas.

### Diagnóstico de capacidad

Usar Ford–Fulkerson o Edmonds–Karp sobre la red seleccionada. Comparar el flujo que puede suministrarse con la demanda proyectada total e identificar las aristas saturadas o próximas a su límite.

**Pendiente:** explicar cómo se representa la fuente, cómo se incorpora la demanda de cada zona al cálculo de flujo y cómo se compatibilizan las unidades.

## 5. Integración y aplicación web

Explicar la cadena: datos → predicción → demanda por nodo → red de menor costo → diagnóstico de capacidad → API → frontend.

**Pendiente:** incluir la visualización de conexiones candidatas y red seleccionada, el flujo por arista y un selector de escenarios de crecimiento. Mostrar cómo cambia el diagnóstico al modificar la demanda.

## 6. Pruebas y resultados

**Pendiente:** registrar casos de prueba de los algoritmos, métricas del modelo, resultados de los escenarios y capturas del frontend funcionando. Separar los resultados observados de las hipótesis iniciales.

## 7. Uso de inteligencia artificial

**Registro inicial:** se utilizó Codex para organizar el informe, proponer el caso sintético e implementar el primer generador de datos. Un pedido del intercambio fue: «¿Cómo seguimos?». Las reglas y unidades quedaron explícitas para que el grupo pueda revisarlas y explicarlas. Falta registrar las siguientes intervenciones, errores detectados y la reflexión final.

## 8. Limitaciones y posibles extensiones

**Pendiente:** documentar las simplificaciones de datos y del modelo de red, qué conclusiones permiten los resultados y qué mejoras se podrían hacer.

## 9. Instalación y ejecución

Las instrucciones para reproducir la aplicación deben mantenerse en el `README.md`. Esta sección puede resumir el entorno usado para obtener los resultados del informe.
