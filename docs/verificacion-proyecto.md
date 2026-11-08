# Verificación técnica del proyecto

Estado: integración completa verificada con Render y correcciones adicionales comprobadas localmente. Correcciones, entorno, efectos y documentación se agrupan en commits locales; el usuario realiza el push. Falta verificar las correcciones en Render y publicar el frontend.

## Estado comprobado

- Kruskal manual con Union-Find; Edmonds–Karp manual con BFS y flujo residual. NetworkX sirve de representación y referencia de totales con tolerancia 0.1.
- API con planta, 26 candidatos, 16 tendidos, sus 16 caudales y resumen de abastecimiento.
- Frontend consume el contrato real, presenta caudales/balance y conserva estados explícitos para datos ausentes.
- Métricas de ambos modelos reproducidas en memoria sin sobrescribir artefactos: lineal MAE 131.28/RMSE 172.97/R² 0.9939; árbol MAE 197.95/RMSE 308.79/R² 0.9807.

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

Frontend: 37 pruebas, lint y build con TypeScript aprobados. El cliente ya acepta métricas null. Se incorporaron los efectos pedidos por Ciro: HoloCard en pestaña especial y LatticeLoader para solicitudes reales. Las cuatro pruebas nuevas verifican contador/limpieza, éxito/error, alternativa sin WebGL y navegación sin solicitudes extra; ver [efectos-visuales.md](efectos-visuales.md).

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

## Entorno y cierre pendiente

Instalación nueva del backend comprobada con Python 3.12.10; scikit-learn 1.9.1 coincide con el artefacto. También se probaron pandas 3.1.1, NumPy 2.5.4, SciPy 1.18.1, NetworkX 3.7, Joblib 1.6.0, FastAPI 0.162.2, Uvicorn 0.54.0 y Pydantic 2.14.3.

Requirements ya fija dependencias directas y transitivas; `.python-version` indica Python 3.12.10. Node queda en 24.x y `.nvmrc` registra 24.20.0; el lockfile conserva las versiones de paquetes. Antes de incorporar los efectos, una copia separada sin entornos previos pasó instalación, `pip check`, 22 tests backend, las 33 pruebas frontend de esa etapa, lint y build con TypeScript. npm aprovechó la caché local. Los efectos no agregan paquetes. La [guía de instalación](instalacion-reproducible.md) permite repetir el ensayo en otra computadora, que sigue pendiente.

Falta separar selección/evaluación final del modelo y justificar features espaciales; completar pruebas HTTP automatizadas, publicar correcciones y verificar Render, y comprobar el proyecto desde otra máquina. `frontend/vercel.json` ya prepara la publicación; todavía no se importó ni publicó el frontend. Los efectos pedidos ya se probaron en Edge con textura/reflejos, movimiento reducido y móvil sin desbordamiento; volver a Capacidad conservó los 17 nodos/16 caudales reales. Consultar otros cambios visuales con Ciro. El registro adicional de herramientas/prompts se completa con información del grupo, sin inventar intervenciones.
