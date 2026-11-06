# Informe — Diseño de infraestructura de red de agua

> Estado: borrador de trabajo. Completar cada sección a medida que se implementa y evalúa el proyecto.

## 1. Problema y objetivo

Una cooperativa de agua debe planificar los tendidos para abastecer una zona nueva. El sistema debe proyectar la demanda futura de cada zona, encontrar una red que conecte todos los nodos con el menor costo de construcción y comprobar si las capacidades alcanzan para esa demanda.

**Decisiones pendientes:** delimitar la zona de estudio, identificar la planta o fuente de agua, elegir la escala de los nodos y fijar las unidades de demanda, capacidad y costo.

## 2. Datos

### Zonas

El enunciado propone: `nodo_id`, `latitud`, `longitud`, `poblacion`, `tipo_zona`, `consumo_historico_mensual`, `crecimiento_poblacional_estimado` y `consumo_futuro`. Este último campo es la variable que se debe predecir.

**Pendiente:** indicar si los datos son reales o sintéticos. Si son sintéticos, documentar el script, la semilla, las reglas de generación, el número de muestras y las limitaciones. Si son reales, citar las fuentes y las transformaciones.

### Conexiones posibles

Cada arista candidata debe indicar sus nodos extremos, costo de construcción y capacidad máxima de transporte.

**Pendiente:** justificar cómo se generan las aristas, los costos y las capacidades; verificar que el grafo de candidatos sea conexo.

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

**Pendiente:** indicar herramientas usadas, tareas en las que ayudaron y en las que no, ejemplos concretos de prompts, errores detectados y una reflexión breve sobre sus límites.

## 8. Limitaciones y posibles extensiones

**Pendiente:** documentar las simplificaciones de datos y del modelo de red, qué conclusiones permiten los resultados y qué mejoras se podrían hacer.

## 9. Instalación y ejecución

Las instrucciones para reproducir la aplicación deben mantenerse en el `README.md`. Esta sección puede resumir el entorno usado para obtener los resultados del informe.
