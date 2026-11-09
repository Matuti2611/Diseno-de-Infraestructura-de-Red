# Verificación final del proyecto

## Alcance revisado

Consigna general y TP de red de agua contrastados con implementación/documentación. Las correcciones finales y su documentación se agrupan en commits locales por indicación del usuario; el push queda a su cargo. No se consultaron cambios remotos no autorizados ni se publicaron servicios. No se cambió dataset, modelo exportado ni dependencias, y no se automatizó la elección de modelos ni se añadió un importador de datos.

Se corrigieron descripciones/documentación obsoletas, una etiqueta del esquema de población y la supresión global de warnings en inferencia. No se detectó una discrepancia matemática en los casos comprobados.

## Cobertura comprobada

| Área | Evidencia |
| --- | --- |
| Datos | Generación reproducible, estructura del caso y conectividad |
| ML | Inferencia individual/lotes/categorías; métricas válidas o null, rechazo de categorías desconocidas |
| Evaluación | MAE/RMSE/MSE/R²/MAPE conocidos; desglose por zona; signo/valor de residuos y no modificación de entradas |
| MST | Union-Find, costo conocido 6 sobre función productiva, árbol real y rechazo de topología vacía/desconectada/aislada |
| Flujo | Caso PLANTA–A–B, capacidades/conservación y máximo 2 que requiere cancelar un flujo residual previo |
| API | Recorrido ASGI completo de seis casos/escenarios, 422 de caso inválido, 503 de topología no disponible y coherencia de candidatos/MST |
| Barrios | Suministro no negativo <= demanda, déficit correcto y sumas iguales al resumen |
| Frontend | Contrato, HTTP/timeout, cero/ausencia, búsquedas/teclado, respuestas tardías, cancelación, casos, comparación y reintento |
| Efectos | Reinicio/limpieza del contador, retiro en error/éxito e imagen accesible sin WebGL |

**28 pruebas backend** en ocho archivos y **43 frontend** en seis archivos. Lint, TypeScript y build frontend aprobados. El conteo describe esta suite: no equivale a cobertura exhaustiva ni a garantía de ausencia de errores.

Los tres tests añadidos en el cierre son casos conocidos, no otro dataset de entrenamiento. No se reentrenó ni se ampliaron funcionalidades por esa revisión.

## Comprobaciones de integración

Seis peticiones HTTP locales respondieron 200 y caso desconocido 422. Edge con API local comprobó 17 nodos, 16 barrios, comparación de tres filas, transición a déficit y pantalla de 390 px sin desbordamiento. Al simular desconexión conservó el resultado identificado y se recuperó al reintentar.

En Progresivo, Base y +10 % están cubiertos; +30 % da suministro ~2195 y déficit ~47.09 m³/día. Original conserva insuficiencia. Resultados, regla, capturas y pasos manuales en [casos-capacidad.md](casos-capacidad.md).

Las métricas JSON del entrenamiento actual se reprodujeron en la revisión previa sin sobrescribir modelo/artefactos: test MAE 130.11, RMSE 172.14, R² 0.9940 y MAPE 3.57 %. La selección fija coincide con la configuración de menor MAE medio de CV; no es un selector automático para cualquier dataset.

## Documentación

README e instalación describen el arranque real. Contrato, plan, informe y matriz se actualizaron para describir lo implementado. Se retiraron cifras antiguas que se presentaban junto a resultados actuales y afirmaciones no justificadas de análisis automático, representatividad de residuos o EDA en un notebook vacío. Los errores y su corrección quedan en la sección de IA del informe, sin atribución personal.

## Límites y cierre

La revisión no prueba cualquier CSV, topología, volumen de datos o dispositivo posible. Los tests usan casos conocidos e invariantes del alcance entregado. No se reejecutó entrenamiento sobre otro dataset, porque no es requisito del enunciado.

La instalación limpia previa y las instrucciones están disponibles; no se comprobó otra computadora ni Linux en esta revisión. El enunciado pide instrucciones reproducibles y demo funcionando, no un proveedor de hosting ni un dataset adicional.

Falta confirmar que el repositorio remoto tenga los cambios finales y preparar la demo/defensa. Si se entrega una URL, comprobar que API y frontend públicos estén actualizados. No se declara un despliegue actual por haber pasado localmente.
