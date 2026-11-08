# Revisión de cumplimiento de la consigna

Fuente: lectura completa de `enunciado.pdf`, 14 páginas; requisitos generales en páginas 1–4 y TP elegido «Diseño de infraestructura de red» en páginas 7–8. Los demás TPs del documento no se incorporan a nuestro alcance.

Esta revisión contrasta el pedido con el código y la documentación. No reemplaza pruebas de algoritmos ni declara implementados pendientes por aparecer escritos en el informe.

## Evaluación actual

La dirección del proyecto coincide con el TP elegido: cooperativa de agua, regresión de consumo, demandas por nodo, árbol de menor costo y evaluación de capacidad mediante flujo. Los datos sintéticos son una opción expresamente válida. El frontend ya se integra con el backend real, pero el proyecto **todavía no está completo**.

Se completaron los algoritmos manuales, contrato y visualización de caudales/balance reales; se verificó Render y se reprodujeron métricas. Las correcciones locales están probadas y sus errores/detección/resolución se registran en la sección de IA del informe. Quedan publicación de correcciones, metodología final, frontend y entrega; estado en `verificacion-proyecto.md`.

## Requisitos y evidencia

| Requisito y referencia | Evidencia actual | Estado / cierre necesario |
| --- | --- | --- |
| Entender problema, decisión y representación (p. 2) | Informe: planificar agua para barrios, costos y capacidades; planta/barrios como nodos y tendidos como aristas. | Cubierto en el borrador; supuestos fundamentados. |
| Dataset real adaptado o sintético con generador y reglas (p. 2) | Scripts Python entregados, semilla 42, 600 muestras, 16 zonas y 26 candidatos. Reglas de población/tipo/consumo/crecimiento y ruido en informe. | Cubierto como caso sintético reproducible. |
| Campos de zonas y objetivo de consumo (p. 7) | `historial_consumo.csv` incluye los campos propuestos y el objetivo; `zonas.csv` omite la etiqueta para inferencia. Se agregaron fila/columna. | Cubierto. Las tablas son orientativas y permiten modificar columnas (pp. 2–3). |
| Regresión permitida y evaluación MAE/RMSE/R² en test separado (pp. 2 y 7) | Lineal/árbol, split 80/20 y selección de modelo mediante validación cruzada 5-Fold en entrenamiento. Justificación de exclusión de variables espaciales por validación cruzada. Evaluación final inalterada en test reservado (MAE=130.11, RMSE=172.14, R²=0.9940, MAPE=3.57 %) y análisis de errores por tipo de zona. | Cubierto: metodología rigurosa, métricas y residuos persistidos en `metricas.json` y consumidos por la API. |
| Demanda predicha como demanda de nodo (p. 7) | Conversión mensual/diaria, demandas al supersumidero y balance HTTP real. | Implementado y casos conocidos cubiertos; balance y unidades consistentes. |
| Implementar Kruskal o Prim (p. 7) | Kruskal manual con Union-Find, costo comparado con NetworkX y prueba de costo conocido sobre la función real. | Implementado; corrección local de desconexión y nodos aislados probada. Se compara costo, no aristas exactas. |
| Implementar Ford–Fulkerson o Edmonds–Karp y comprobar cobertura (p. 7) | Edmonds–Karp manual, BFS residual, tests conocidos y conservación; 16 caudales y balance disponibles. | Implementado. Se verificó además un caso que requiere cancelación residual. No implica reparto equitativo. |
| Tendidos posibles con red mínima resaltada (p. 7) | SVG, selección, candidatos/MST, tabla/costo y geometría de API completa. | Cubierto y verificado en la página local con Render. |
| Flujo en cada arista y saturación/cercanía (p. 8) | 16 etiquetas con caudal, cero Sin dato en API actual, tabla/detalle y estados diferenciados. | Cubierto y verificado en Edge, incluido móvil. |
| Selector de crecimiento que cambie el diagnóstico (p. 8) | Tres escenarios HTTP reales cambian demanda/abastecido/déficit. Casos conocidos de cobertura/déficit en tests. | Integrado: déficit base 732.56 y +30 % 793.55 m³/día. No se exige cambiar el MST con costos fijos. |
| Backend con cálculos y frontend que consuma API (pp. 2–3) | FastAPI en Render y React/TypeScript; navegador no calcula predicciones, MST o flujo. | Integración completa comprobada; publicar correcciones locales y verificar otra máquina. |
| Código Git con historial incremental (p. 3) | Historial de ambos integrantes; correcciones, entorno, efectos y documentación agrupados en commits locales por tema. | El usuario realiza el push; comprobar después la publicación de las correcciones en Render. |
| Informe con diseño, dataset, features, metodología, algoritmos e integración (pp. 3–4) | Informe con algoritmos, métricas reproducidas, selección por CV, justificación de variables, análisis de errores por zona y sección de IA. | Documentado y alineado con el código implementado. |
| Capturas de frontend funcionando (p. 4) | Tres imágenes de navegador real renovadas con 16 caudales y balance/diagnóstico de déficit. | Disponibles y alineadas con el servicio actual; renovar si cambia la interfaz antes de entregar. |
| Uso de IA: herramientas, partes, prompts, errores y reflexión (p. 3) | Sección 7 con Codex/Gemini, paletasdecolores.com.ar, exploración de diseños en Figma, patrones del proyecto previo de Ciro, instrucciones resumidas y corrección del indicador live. | Sección armada con referencias aclaradas por Ciro; revisar aportes adicionales de Matías si los hubo. No se atribuyen copias literales de código no inspeccionado. |
| Limitaciones y extensiones (p. 4) | Sección 8 con datos sintéticos, simplificación hidráulica, tiempo, incertidumbre, MST/capacidad y pendientes. | Documentado; revisar al cerrar implementación. |
| Demo end-to-end e instalación desde otro entorno (p. 4) | Versiones fijadas, guía de instalación, copia limpia con .venv/node_modules nuevos y 22/33 tests, lint y build aprobados. Página integrada con Render. | Falta repetir instalación y recorrido en otra computadora y la publicación prevista del frontend. La copia local no demuestra compatibilidad en otra máquina. |

## Aclaraciones que evitan trabajo innecesario

- No se pide que el MST cambie de forma al aumentar el crecimiento. Con costos y candidatos fijos puede mantenerse; la predicción interviene en el diagnóstico de flujo y cobertura.
- El selector no aumenta directamente la demanda: multiplica la tasa anual de crecimiento usada por el predictor. La página ya lo aclara.
- El TP requiere modelos permitidos y evaluación, pero no obliga a comparar dos modelos. La comparación elegida debe hacerse con una metodología defendible.
- No se pide un mapa con calles o proveedor geográfico: el esquema con coordenadas y nodos/aristas permite visualizar el caso.
- No se exige un proveedor de hosting ni un dominio. Publicar en Vercel es una decisión del grupo; demo funcionando e instrucciones reproducibles sí son entregables.
- NetworkX aparece sugerido para representar/leer/escribir grafos. La consigna usa «implementar» para los algoritmos requeridos; no dar por cerrado ese punto con una llamada de biblioteca. La posibilidad de usar bibliotecas se menciona expresamente para otro TP en un caso distinto y no se traslada automáticamente al nuestro.

## Trabajo compartido para cerrar la entrega

1. **Página, completado:** etiquetas de caudal de todos los tramos y tratamiento explícito de dato ausente. Revisado en escritorio/móvil sin desbordamiento de página.
2. **Integración verificada:** panel de suministro/déficit/cobertura con datos completos reales. Capturas renovadas; revisar correcciones de backend cuando se publiquen.
3. **Documentación:** conservar las referencias aclaradas por Ciro (paleta, exploración en Figma y patrones de su proyecto anterior) y completar aportes adicionales de Matías si los hubo. No hace falta sumar funciones de otro proyecto que no pertenecen a este TP.
4. **Ambos:** cerrar informe con resultados reproducidos, capturas finales, registro de IA completo y comprensión del código para la defensa oral.
5. **Entrega:** comprobar instalación en otro entorno, demo completa y código final en Git. Publicar frontend en Vercel si se mantiene la decisión del grupo.

## Verificaciones de esta revisión

- Consigna leída completa; requisitos generales y páginas 7–8 contrastados con el proyecto. Los datos fueron verificados contra sus reglas sintéticas y la generación está cubierta en la suite.
- Verificación actual: 22 tests backend y 37 frontend aprobados, más lint y build con TypeScript. Las regresiones reprodujeron los fallos y luego pasaron; métricas/modelo/CSV no se sobrescribieron.
- Render: tres POST con contrato completo. Edge: 16 etiquetas con caudal, cero Sin dato y déficit visible; móvil de 390 px sin desbordamiento. Capturas renovadas.
- Backend y frontend instalados en copia nueva, con dependencias fijadas: 22/33 tests, lint y build con TypeScript aprobados. Se resolvió el bloqueo anterior por permisos Windows. Falta probar otra computadora siguiendo `instalacion-reproducible.md`.
- Error, detección, resolución y pruebas de los casos corregidos se registran en la sección de IA de `Informe.md`. La verificación técnica está en `verificacion-proyecto.md`.
- HTTP local confirmó simulación con métricas null, predicción individual consistente y rechazo de categoría inválida. Las correcciones se registran en commits locales; push a cargo del usuario y despliegue pendiente de verificar. Las capturas existentes corresponden a la verificación previa real en Render.
