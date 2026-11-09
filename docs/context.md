# Contexto del proyecto para agentes de código

> Documento vivo: leer y actualizar antes de trabajar y de cada commit/push. Reglas en `../AGENTS.md`. Sin fechas exactas ni hashes; el historial se consulta en Git.

## Objetivo y responsabilidades

TP de una cooperativa de agua: datos sintéticos, regresión de consumo a cinco años, demanda por barrio, Kruskal y Edmonds–Karp manuales, API FastAPI y página React/TypeScript/Vite. Ciro trabaja en frontend y Matías en backend/ML/grafos. Ciro asumió completar las mejoras de casos y abastecimiento por barrio con su presentación/comparación.

El usuario autorizó probar y agrupar los cambios en commits locales. El backend y sus pruebas ya están registrados. Este grupo incorpora el frontend y sus pruebas; el cierre documental está preparado para el siguiente. El push lo hace el usuario. No se publicaron ampliaciones en Render/Vercel ni se consultaron cambios remotos posteriores.

## Datos

Una planta, 16 barrios, 600 muestras sintéticas y 26 candidatos, con semilla 42. Se preservan los CSV y modelo versionados. El original conserva sus capacidades; Progresivo mantiene candidatos/costos y asigna 2195 m³/día a PLANTA–Z01 y 2500 al resto. Se reproduce con `python backend/app/data/generar_caso_progresivo.py`, sin sobrescribir la entrada. La transición está calibrada para datos/modelo actuales y debe verificarse de nuevo si cambian.

## Machine learning

La versión recibida ya implementa CV de cinco pliegues dentro del 80 % de entrenamiento, comparación con/sin features espaciales y evaluación final con análisis por tipo de zona/residuos. El modelo lineal sin espaciales tiene MAE 130.11, RMSE 172.14 y R² 0.9940 en test. Se reprodujo el JSON completo en la revisión previa sin sobrescribir artefactos. Esta ampliación de capacidades no entrena ni cambia el modelo.

## Grafos

Kruskal y Edmonds–Karp son manuales; NetworkX representa grafos y compara totales. Se conserva el control de topología desconectada. El MST no necesita cambiar al variar crecimiento/capacidades porque sus pesos son costos fijos. Máximo flujo prioriza suministro total, sin garantizar equidad ni reparto único.

## API

POST /api/simular-red admite `caso_red` original/progresivo (original por omisión) y crecimiento positivo <=5. Responde identificación del caso/crecimiento, planta/barrios, MST, candidatos del mismo caso, todos los flujos, resumen y métricas nullable. Casos fuera del enum producen 422, nunca se aceptan rutas del cliente.

Cada barrio tiene demanda, `caudal_abastecido_m3_dia` desde su enlace al SUPER_SUMIDERO y `deficit_m3_dia`. No usar el caudal de una cañería como consumo local. La planta es fuente, no consumidora. Se comprueban finitud, no negatividad, suministro <= demanda y suma igual al flujo total antes de redondear; el resumen suma los importes publicados por barrio. Las rutas auxiliares de inspección conservan el caso original.

## Pruebas

25 pruebas backend aprobadas, incluyendo ASGI/FastAPI de seis combinaciones, candidatos/MST coherentes, balances individuales/globales, caso conocido PLANTA–A–B que distingue tránsito/consumo y CSV reproducible. La API local también respondió las seis simulaciones y rechazó caso desconocido con 422.

Progresivo cubre Base y +10 % (entrada ~99.9 %); +30 % tiene demanda 2242.09, suministro 2195 y déficit 47.09 m³/día. Original conserva déficit en los tres. No se modificaron modelo, CSV ni dependencias.

## Página y próximo paso

La página incorpora selector Original/Progresivo, detalle/tabla de demanda-suministro-déficit por barrio y comparación Base/+10 %/+30 % del mismo caso, sin cambiar el escenario principal del gráfico. El cliente valida balances, metadatos y coherencia de los casos. Una API antigua que ignore Progresivo produce aviso, no resultados de otro caso. Se cancela la comparación al cambiar de caso y no se muestran tablas parciales si falla una consulta.

43 pruebas frontend, lint y build con TypeScript aprobados. Edge con API local verificó 17 nodos, 16 barrios, comparación completa, transición a déficit, móvil de 390 px sin desbordamiento y cero excepciones. La desconexión simulada conservó los datos identificados; reintentar tras restablecer la red recuperó la simulación. Otras mejoras visuales requieren consulta al usuario.

El próximo grupo registra documentación, informe, capturas y la guía manual; el usuario hará push. Actualizar/verificar primero API en Render y luego frontend en Vercel. Repetir instalación en otra computadora. Python se inicia desde la raíz por sus rutas relativas; no reinstalar dependencias ni detener procesos ajenos a QA.
