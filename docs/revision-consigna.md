# Revisión de cumplimiento de la consigna

Fecha: 08/11/2026. Fuente: lectura completa de `enunciado.pdf`, 14 páginas; requisitos generales en páginas 1–4 y TP elegido «Diseño de infraestructura de red» en páginas 7–8. Los demás TPs del documento no se incorporan a nuestro alcance.

Esta revisión contrasta el pedido con el código y la documentación. No reemplaza pruebas de algoritmos ni declara implementados pendientes por aparecer escritos en el informe.

## Evaluación actual

La dirección del proyecto coincide con el TP elegido: cooperativa de agua, regresión de consumo, demandas por nodo, árbol de menor costo y evaluación de capacidad mediante flujo. Los datos sintéticos son una opción expresamente válida. El frontend ya se integra con el backend real, pero el proyecto **todavía no está completo**.

Se completaron del lado frontend las etiquetas de caudal y el panel para el balance opcional de abastecimiento. Además de las tareas de Matías quedan la verificación conjunta con datos completos reales, documentación final y entrega. No hace falta sumar páginas comerciales, autenticación, base de datos, efectos decorativos o tecnologías nuevas para cumplir.

## Requisitos y evidencia

| Requisito y referencia | Evidencia actual | Estado / cierre necesario |
| --- | --- | --- |
| Entender problema, decisión y representación (p. 2) | Informe: planificar agua para barrios, costos y capacidades; planta/barrios como nodos y tendidos como aristas. | Cubierto en el borrador; defender los supuestos. |
| Dataset real adaptado o sintético con generador y reglas (p. 2) | Scripts Python entregados, semilla 42, 600 muestras, 16 zonas y 26 candidatos. Reglas de población/tipo/consumo/crecimiento y ruido en informe. | Cubierto como caso sintético; no presentarlo como mediciones reales. |
| Campos de zonas y objetivo de consumo (p. 7) | `historial_consumo.csv` incluye los campos propuestos y el objetivo; `zonas.csv` omite la etiqueta para inferencia. Se agregaron fila/columna. | Cubierto. Las tablas son orientativas y permiten modificar columnas (pp. 2–3). |
| Regresión permitida y evaluación MAE/RMSE/R² en test separado (pp. 2 y 7) | Script con regresión lineal/árbol, split 80/20 y métricas; modelo exportado. | Parcial: reproducir cifras, justificar features espaciales, separar selección del modelo de evaluación final y completar análisis de errores. |
| Demanda predicha como demanda de nodo (p. 7) | Pipeline convierte m³/mes a m³/día; flujo usa esas demandas hacia supersumidero. | Implementado; faltan tests conocidos de unidades y abastecimiento simultáneo. |
| Implementar Kruskal o Prim (p. 7) | `mst.py` delega a `nx.minimum_spanning_tree`; el comentario menciona Kruskal. | Pendiente de Matías: cerrar implementación exigida y pruebas. No declarar desarrollo propio de los pasos del algoritmo. |
| Implementar Ford–Fulkerson o Edmonds–Karp y comprobar cobertura (p. 7) | `flujo.py` arma la red y usa `nx.maximum_flow`, sin `flow_func` explícito; suministro se calcula pero se descarta en respuesta. | Parcial: implementación exigida, capacidades/conservación, suministro/déficit y tests. El comentario no prueba que se ejecuta Edmonds–Karp. |
| Tendidos posibles con red mínima resaltada (p. 7) | SVG, selección de elementos, candidatos/MST y tabla/costo. | Cubierto para el caso actual; planta/candidatos se complementan con CSV versionados hasta tener contrato completo. |
| Flujo en cada arista y saturación/cercanía (p. 8) | Cada arista seleccionada tiene etiqueta de caudal/utilización o Sin dato; tabla/detalle y estados diferenciados. API base informa 2 de 16 tramos. | Frontend preparado y probado; completar todos los flujos en API y verificar los datos reales. |
| Selector de crecimiento que cambie el diagnóstico (p. 8) | Base/+10 %/+30 %, llamadas reales y demanda actualizada; panel preparado para resumen opcional. Un caso controlado pasa de cobertura a déficit al cambiar respuesta. | Falta resumen real del backend y validación de escenarios end-to-end. Los mocks no prueban el predictor ni el algoritmo Python. |
| Backend con cálculos y frontend que consuma API (pp. 2–3) | FastAPI en Render y React/TypeScript; navegador no calcula predicciones, MST o flujo. | Integración real comprobada; completar contrato y verificar desde entorno limpio. |
| Código Git con historial incremental (p. 3) | Hay historial de ambos integrantes y merge conservando trabajo. El frontend actual aún tiene cambios sin commit. | Registrar grupos de cambios cuando el usuario solicite commits y verificar su publicación antes de entregar. |
| Informe con diseño, dataset, features, metodología, algoritmos e integración (pp. 3–4) | `Informe.md`, actualizado para distinguir estado real de propuestas. | Borrador avanzado; Matías debe cerrar algoritmos y resultados reproducibles. |
| Capturas de frontend funcionando (p. 4) | Tres imágenes de navegador real renovadas con etiquetas y diagnóstico incompleto, enlazadas desde informe. | Disponibles; renovar al cerrar integración con resumen real. |
| Uso de IA: herramientas, partes, prompts, errores y reflexión (p. 3) | Sección 7 con Codex/Gemini, paletasdecolores.com.ar, exploración de diseños en Figma, patrones del proyecto previo de Ciro, instrucciones resumidas y corrección del indicador live. | Sección armada con referencias aclaradas por Ciro; revisar aportes adicionales de Matías si los hubo. No se atribuyen copias literales de código no inspeccionado. |
| Limitaciones y extensiones (p. 4) | Sección 8 con datos sintéticos, simplificación hidráulica, tiempo, incertidumbre, MST/capacidad y pendientes. | Documentado; revisar al cerrar implementación. |
| Demo end-to-end e instalación desde otro entorno (p. 4) | Frontend probado contra Render; instalación aislada de dependencias pasó con lockfile. README raíz y guía frontend. | Parcial: build/tests aprobados en proyecto principal, bloqueados por permisos Windows en la copia aislada. Falta demo con contrato completo y ensayo desde otra máquina de frontend/backend. |

## Aclaraciones que evitan trabajo innecesario

- No se pide que el MST cambie de forma al aumentar el crecimiento. Con costos y candidatos fijos puede mantenerse; la predicción interviene en el diagnóstico de flujo y cobertura.
- El selector no aumenta directamente la demanda: multiplica la tasa anual de crecimiento usada por el predictor. La página ya lo aclara.
- El TP requiere modelos permitidos y evaluación, pero no obliga a comparar dos modelos. La comparación elegida debe hacerse con una metodología defendible.
- No se pide un mapa con calles o proveedor geográfico: el esquema con coordenadas y nodos/aristas permite visualizar el caso.
- No se exige un proveedor de hosting ni un dominio. Publicar en Vercel es una decisión del grupo; demo funcionando e instrucciones reproducibles sí son entregables.
- NetworkX aparece sugerido para representar/leer/escribir grafos. La consigna usa «implementar» para los algoritmos requeridos; no dar por cerrado ese punto con una llamada de biblioteca. La posibilidad de usar bibliotecas se menciona expresamente para otro TP en un caso distinto y no se traslada automáticamente al nuestro.

## Trabajo que queda fuera de la implementación de Matías

1. **Página, completado:** etiquetas de caudal de todos los tramos y tratamiento explícito de dato ausente. Revisado en escritorio/móvil sin desbordamiento de página.
2. **Página preparada / integración pendiente:** panel de suministro/déficit/cobertura y pruebas de caso conocido ya implementados. Coordinar `contrato-api.md` con Matías y validar esos campos reales; no inventarlos mientras faltan.
3. **Documentación:** conservar las referencias aclaradas por Ciro (paleta, exploración en Figma y patrones de su proyecto anterior) y completar aportes adicionales de Matías si los hubo. No hace falta sumar funciones de otro proyecto que no pertenecen a este TP.
4. **Ambos:** cerrar informe con resultados reproducidos, capturas finales, registro de IA completo y comprensión del código para la defensa oral.
5. **Entrega:** comprobar instalación en otro entorno, demo completa y código final en Git. Publicar frontend en Vercel si se mantiene la decisión del grupo.

## Verificaciones de esta revisión

- Leído el PDF completo, incluidas las consignas generales y páginas 7–8 del caso elegido.
- Revisados generadores, CSV, entrenamiento, MST/flujo/pipeline/API y gráfico/tabla/adaptación frontend.
- Ejecutado `python -m unittest discover -s backend/tests -p test_datos.py -v`: un test aprobado.
- Comprobados conteos, columnas de CSV y que las 600 etiquetas respetan la regla de cinco años con ruido de ±5 %.
- Tras los avances del frontend pasaron 33 tests, lint y build con TypeScript en el proyecto principal. Se comprobó instalación aislada de dependencias; su build/tests quedaron bloqueados por permisos de Windows y no se declaran aprobados.
- Se revisaron en Edge la API real, 16 etiquetas, diagnóstico incompleto sin resumen, escenarios base/+30 % y móvil de 390 px sin desbordamiento. Se corrigió superposición de etiquetas con nombres de nodos y se renovaron capturas.
- No se modificaron algoritmos ni se reprodujeron métricas de ML. Los cambios previos se agruparon en commits de implementación y documentación por solicitud del usuario; los avances de capacidad forman otro grupo. No se hizo push ni se publicó el frontend.
