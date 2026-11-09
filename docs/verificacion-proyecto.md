# Verificación técnica del proyecto

Estado: integración completa verificada con Render y correcciones adicionales comprobadas localmente. Correcciones, entorno, efectos y documentación se agrupan en commits locales; el usuario realiza el push. Falta verificar las correcciones en Render y publicar el frontend.

## Estado comprobado

- Kruskal manual con Union-Find; Edmonds–Karp manual con BFS y flujo residual. NetworkX sirve de representación y referencia de totales con tolerancia 0.1.
- API con planta, 26 candidatos, 16 tendidos, sus 16 caudales y resumen de abastecimiento.
- Frontend consume el contrato real, presenta caudales/balance y conserva estados explícitos para datos ausentes.
- Nuevo entrenamiento reproducido sin sobrescribir el modelo, con métricas en archivo temporal: el JSON completo coincide con el entregado. Selección y comparación por CV de cinco pliegues dentro del 80 % de entrenamiento; exclusión de espaciales comparada allí. Lineal sin espaciales: MAE CV 141.80; test MAE 130.11/RMSE 172.14/R² 0.9940/MAPE 3.57 %. Desglose por tipo de zona y muestras de residuos presentes.

## Correcciones y registro de uso de IA

El registro de errores, cómo se detectaron, cómo se resolvieron y qué pruebas los verifican está en la [sección de uso de IA del informe](../Informe.md#errores-de-la-ia-detectados-y-cómo-los-resolvimos). No se atribuyen como errores personales de un integrante.

Las correcciones locales incluyen codificación estable en inferencia, ausencia explícita de métricas mediante null, prueba de Kruskal sobre la función real y control de topología desconectada. No se modificaron modelo serializado ni datos sintéticos. El caso principal conserva su demanda y balance; el cambio de predicción afecta a consultas individuales o lotes que antes perdían categorías.

## Pruebas

`.venv\Scripts\python.exe -m unittest discover -s backend/tests -v`: **22 pruebas aprobadas** en seis archivos.

Las regresiones nuevas fallaron antes de corregir el código y ahora comprueban:

- Predicciones iguales en lote completo, por categoría e individuales; endpoint individual para cada tipo y rechazo de categorías no admitidas.
- Métricas ausentes, corruptas, incompletas o no finitas sin cifras de respaldo; simulación disponible con `metricas_ml: null`; archivo válido con R² negativo.
- Kruskal productivo con costo conocido 6, conectividad y ausencia de ciclos; rechazo de redes vacías, desconectadas o con nodos declarados aislados.
- Error de topología presentado por API como HTTP 503 en vez de resultado incompleto.

Frontend antes de la ampliación de casos: 37 pruebas, lint y build con TypeScript aprobados. El cliente ya acepta métricas null. Se incorporaron los efectos pedidos por Ciro: HoloCard en pestaña especial y LatticeLoader para solicitudes reales. Las cuatro pruebas nuevas verifican contador/limpieza, éxito/error, alternativa sin WebGL y navegación sin solicitudes extra; ver [efectos-visuales.md](efectos-visuales.md).

Se comprobó también HTTP local con una API temporal y métricas ausentes, sin tocar archivos reales: simulación 200 con 16 caudales y balance base sin cambios, `metricas_ml: null`; consulta de métricas 200/null; Z16 individual 10128.63 m³/mes y categoría inválida 422. Falta publicar estas correcciones y comprobarlas en Render.

## Resultados reales observados en Render

La revisión previa comprobó OpenAPI y tres POST HTTP 200 con contrato completo. No se atribuye al servicio la corrección local posterior mientras no se publique y verifique.

| Escenario | Demanda m³/día | Abastecido m³/día | Déficit m³/día |
| --- | --- | --- | --- |
| Base | 2167.74 | 1435.18 | 732.56 |
| +10 % | 2192.58 | 1439.69 | 752.89 |
| +30 % | 2242.26 | 1448.71 | 793.55 |

Los porcentajes multiplican la tasa poblacional. Se recibieron 17 nodos, 26 candidatos y 16 caudales en cada escenario. Edge confirmó las 16 etiquetas, cero Sin dato, déficit visible y móvil de 390 px sin desbordamiento. Las capturas de `capturas/` corresponden a esa verificación real, no a mocks.

El flujo máximo optimiza suministro total, no equidad. Puede haber tramos con cero y varias asignaciones máximas válidas; comparar totales y conservación, sin exigir una asignación idéntica a NetworkX.

## Ampliación actual de casos y barrios

Las dos mejoras están implementadas localmente: selección original/progresivo, regla reproducible del segundo CSV y suministro/déficit de cada barrio desde el supersumidero. La página tiene selector, detalle/tabla por barrio y comparación de tres escenarios, sin alterar el original ni añadir dependencias.

**25 pruebas backend y 43 frontend aprobadas**, lint, TypeScript y build. ASGI automatizado de las seis combinaciones y ejemplo conocido de consumo/tránsito; HTTP local 200 para las seis y 422 para caso desconocido. Edge con API local confirmó 16 barrios, comparación, déficit progresivo de 47.09 m³/día en +30 % y móvil de 390 px sin desbordamiento ni excepciones. Reglas, cantidades publicadas y capturas en [casos-capacidad.md](casos-capacidad.md).

La evaluación de ML ya está implementada y reproducida. Sus pruebas específicas y comparación con una referencia simple en el script son mejoras adicionales. La exportación usa explícitamente la configuración ganadora de CV, sin selección automática si cambian los datos. La comprobación adicional de mantener consumo histórico dio MAE 479.20 frente a 130.11 del modelo.

## Entorno y cierre pendiente

Dependencias fijadas, Python 3.12.10 y Node 24.x; no se incorporaron paquetes para estas ampliaciones. La instalación limpia anterior está documentada en [instalacion-reproducible.md](instalacion-reproducible.md); su prueba en otra computadora sigue pendiente.

Falta actualizar/verificar API en Render, comprobar la página contra ella y publicar frontend en Vercel. No se confirmó el estado de la cuenta Vercel ni cambios remotos posteriores. Se repitieron 25/43 pruebas, lint, build y recorrido Edge antes de agrupar los cambios en commits locales; desconexión y reintento conservaron el resultado identificado y recuperaron la conexión. El usuario realiza el push. Conservar diferenciados resultados HTTP locales y observaciones previas del servicio público. Completar el registro de IA adicional con información confirmada del grupo.
