# Cumplimiento de enunciado.pdf

Fuente: consignas generales y entregables, páginas 1–4; TP «Diseño de infraestructura de red», páginas 7–8. Los otros TPs no pertenecen a este trabajo.

## Requisitos obligatorios

| Requisito | Evidencia | Estado |
| --- | --- | --- |
| Problema, decisión y grafo adecuados | Cooperativa de agua, planta/barrios y tendidos con costo/capacidad; informe secciones 1 y 4 | Implementado/documentado |
| Dataset real adaptado o sintético con reglas/procedimiento | Generador estándar, semilla 42, 600 muestras y reglas de consumo/crecimiento; CSV entregados | Implementado y reproducible |
| Regresión de consumo futuro y MAE/RMSE/R² en test separado | Lineal/árbol permitidos, CV en entrenamiento y evaluación en test; métricas reproducidas, análisis por zona y residuos | Implementado y documentado con límites |
| Predicción como demanda de nodo | Conversión mensual/diaria y capacidad de cada barrio hacia supersumidero | Implementado y probado |
| Kruskal o Prim | Kruskal manual con Union-Find, árbol conexo de costo conocido y validación contra NetworkX | Implementado y probado |
| Ford–Fulkerson o Edmonds–Karp sobre la red | Edmonds–Karp manual con BFS residual, capacidades y conservación | Implementado y probado, incluida cancelación residual |
| Tendidos posibles y MST resaltado | SVG, candidatos/MST, detalle y tabla | Implementado y revisado en navegador |
| Caudal por arista y saturación/cercanía | Todos los flujos, cero distinto de ausente, umbral cercano 90 % y saturación 100 % | Implementado y probado |
| Selector de crecimiento que cambie diagnóstico | Base/+10 %/+30 % cambian demanda y déficit; caso progresivo muestra transición a insuficiencia | Implementado y probado |
| Backend por API y frontend en navegador | FastAPI y React/Vite; cálculos de ML/grafos en Python | Demo local end-to-end comprobada |
| Repositorio Git con historial incremental | Historial de ambos integrantes y grupos de implementación/pruebas/documentación | Existe; verificar que la entrega remota tenga el código final |
| Informe completo | Problema, datos, features, metodología, algoritmos, integración, resultados, capturas y límites | Escrito y contrastado con código |
| Uso de IA | Herramientas, partes asistidas, prompts, errores/detección/soluciones y reflexión | Documentado; agregar solo aportes adicionales que confirme el grupo |
| README para levantar desde otro entorno | Versiones fijadas, comandos y demo local; instalación limpia previa comprobada | Instrucciones entregadas |

## Qué no exige el enunciado

No exige hosting público ni Vercel, otro dataset de prueba, un importador CSV web, elección automática del ganador de ML, mapas reales, base de datos o autenticación. Comparar varios modelos está permitido; entrenar uno de los modelos indicados y evaluarlo correctamente es suficiente.

No exige que el MST cambie al aumentar crecimiento: los costos se conservan y la predicción interviene en el diagnóstico de flujo/cobertura. El TP pide comprobar si la capacidad alcanza, no garantizar cobertura en todos los escenarios.

Las tablas de columnas son orientativas según las consignas generales. El historial tiene el objetivo consumo_futuro; las zonas de inferencia no lo incluyen porque es lo que se predice.

Probar otra computadora es una comprobación útil de las instrucciones, no un entregable adicional al README reproducible. La defensa oral exige comprender cualquier parte del código.

## Mejoras incluidas

El selector Original/Progresivo, la regla reproducible del caso progresivo, suministro/déficit por barrio y comparación de tres escenarios permiten explicar mejor el resultado, sin alterar los objetivos. HoloCard y el loader son efectos elegidos por Ciro; no sustituyen cálculos ni son requisitos académicos.

## Cierre de entrega

No quedan funcionalidades obligatorias identificadas como faltantes. Queda comprobar que la versión final esté disponible en GitHub y preparar la demo/defensa. Si se entrega una URL pública, verificar que Render y el frontend publicado tengan la misma versión funcional; su publicación no se da por hecha.

No se inventan aportes de IA o verificaciones externas. Resultados y límites de pruebas en [verificacion-proyecto.md](verificacion-proyecto.md), contrato en [contrato-api.md](contrato-api.md) y detalle del ejemplo en [casos-capacidad.md](casos-capacidad.md).
