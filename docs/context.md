# Contexto del proyecto para agentes de código

> Documento vivo: leer antes de trabajar y actualizar ante cambios importantes y antes de commits/push. Reglas completas en `../AGENTS.md`. Sin fechas exactas ni hashes: el historial se consulta en Git.

## Objetivo y alcance

TP integrador para una cooperativa de agua: datos sintéticos → regresión de consumo a cinco años → demanda diaria por barrio → Kruskal de menor costo → Edmonds–Karp → API → página. Consigna general pp. 1–4 y caso elegido pp. 7–8. El crecimiento cambia demanda y capacidad de abastecimiento, sin exigir que cambie un MST con costos fijos. La matriz está en `revision-consigna.md`.

Ciro trabaja en frontend y Matías en backend/ML/grafos. Ciro asumió y autorizó completar la integración de capacidades progresivas, el suministro/déficit por barrio y su comparación en la web. Se implementó ese alcance con el stack actual; no pedir otra vez aprobación por él. Las ampliaciones visuales ajenas al pedido se consultan antes. Sin autenticación, base de datos ni servicios nuevos.

## Estado del repositorio y publicación

La copia recibió el nuevo entrenamiento/evaluación de ML y el CSV progresivo de Matías; se preservaron. Las ampliaciones se agrupan en commits locales de backend, frontend y documentación, como solicitó el usuario; el push queda a su cargo. No se modificaron modelo ni CSV versionados. No se confirmó si GitHub tiene cambios posteriores a los recibidos; no repetir una consulta remota no autorizada por otro medio.

Render ya alojaba la API y su contrato de planta/candidatos/16 caudales/balance fue verificado. La ampliación de casos y barrios solo está comprobada localmente: actualizar/verificar Render antes de declararla publicada. Frontend preparado para Vercel, publicación sin confirmar. El usuario realiza los push.

## Página / frontend

React + TypeScript estricto + Vite; CSS propio y SVG para la red. Paleta `#44749d`, `#c6d4e1`, `#ffffff`, `#ebe7e0`, `#bdb8ad`. Tendidos/Capacidad, selección de nodo/arista por teclado o mouse, detalle, búsqueda en tabla, leyendas, demanda, costo y caudales.

- Selector Original/Progresivo independiente de Base/+10 %/+30 %. Estos porcentajes multiplican la tasa anual poblacional, no directamente el consumo.
- Cada resultado identifica el caso y escenario realmente mostrados. Se conserva la respuesta anterior identificada durante carga/error; respuestas tardías de otro caso/escenario no reemplazan la actual.
- En Capacidad: suministro/déficit en el detalle y tabla de barrios; «Comparar escenarios» solicita tres simulaciones del mismo caso, sin modificar el escenario principal. Se cancela al cambiar de caso y no muestra tablas parciales si falla una consulta.
- Cliente HTTP con validación de JSON, referencias, candidatos/MST, capacidades y balances por barrio/globales; cancelación y espera de 90 s. Sin datos simulados como respaldo de errores.
- Progresivo exige confirmación de caso/crecimiento para detectar una API antigua que ignore el campo. Original admite respuestas anteriores: los suministros ausentes son «No informado», nunca cero.
- API aporta geometría/candidatos. `casoRed.json` solo completa geometría CSV de respuestas anteriores coincidentes, sin predicciones. Sincronizar con `python frontend/scripts/sincronizar_datos.py` si cambia el caso original.
- Los tendidos seleccionados muestran caudal/utilización; distingue cero, ausencia, cercanía >=90 % y saturación. Gráfico/tabla mantienen desplazamiento interno en móvil.
- No hay distintivo live ni hora de respuesta. LatticeLoader azul acompaña solicitudes reales y reinicia por caso/escenario/intento; su reloj incluye espera de red y servidor, no es porcentaje de avance.
- Pestaña Efectos: HoloCard/Pikachu local, carga diferida, pausa y alternativa sin WebGL. Ambos componentes de React Bits son código local TypeScript/CSS, sin Tailwind ni paquetes nuevos; respetan movimiento reducido. TechText no se aplicó porque anima letras, no grafos. Procedencia en `efectos-visuales.md` y `../frontend/THIRD_PARTY_NOTICES.md`.

Guía de ampliación y resultados: `casos-capacidad.md`. No se entrena ML ni se calculan MST/flujo en el navegador.

## Datos

Generador estándar Python, semilla 42: una planta, 16 barrios, 600 muestras y 26 candidatos. Consumo mensual, capacidades diarias, costos convencionales y horizonte de cinco años con ruido ±5 %. No son mediciones reales. El pipeline divide por 30 para convertir consumo a diario.

Se conserva `aristas_candidatas.csv`. `aristas_progresivas.csv` usa los mismos candidatos/costos/coordenadas, con PLANTA–Z01 de 2195 m³/día y el resto de 2500. Se reproduce con `python backend/app/data/generar_caso_progresivo.py`, sin sobrescribir la entrada. Es una regla sintética fija declarada; otras semillas, modelos o topologías requieren repetir la comprobación. No se recalibran capacidades por petición ni se reentrena al cambiar de caso. Rutas actuales de datos/modelo relativas a la raíz: iniciar Python desde ella.

## Machine learning

Matías cerró la metodología, justificación de features y evaluación de ML en `entrenar.py`:
- **Separación de validación y test:** Selección de modelo mediante validación cruzada 5-Fold dentro del 80 % de entrenamiento (480 muestras) y reserva estricta del 20 % (120 muestras) como conjunto de prueba final no visto.
- **Justificación de features:** Comparación experimental en validación cruzada entre incluir y excluir variables espaciales (`latitud`, `longitud`, `fila`, `columna`). Excluirlas redujo el MAE de CV de 142.65 a 141.80 m³/mes y evitó sobreajuste por ruido aleatorio en coordenadas que no intervienen en el consumo.
- **Comparación de modelos:** En validación cruzada 5-Fold, Regresión Lineal superó a Árbol de Decisión (MAE CV 141.80 frente a 186.66 m³/mes). Se reentrenó en todo el 80 % y se exportó a `backend/models/modelo_consumo.joblib`.
- **Evaluación final en test (20 %):** MAE = 130.11 m³/mes, RMSE = 172.14 m³/mes, R² = 0.9940, MAPE = 3.57 %. Persistidas en `backend/models/metricas.json` y consumidas por la API.
- **Análisis de errores:** Desglose en test por tipo de zona: Residencial MAE=106.83 (3.79 %), Comercial MAE=128.09 (2.62 %), Industrial MAE=326.67 (4.48 %). El mayor error absoluto en industria responde a la escala de consumo (~8600 frente a ~3500 m³/mes), manteniéndose el error relativo uniforme por debajo del 5 %. Muestra de residuos documentada en JSON e informe.
- `features.py`: funciones `preparar_features_entrenamiento` (con exclusión de espaciales) y `preparar_features_inferencia` (asegura coincidencia exacta con `modelo.feature_names_in_`).
- `evaluar.py`: cálculo de métricas globales (MAE, RMSE, MSE, R², MAPE), evaluación por subgrupos y extracción de residuos.
- `ml/metricas.py`: centraliza lectura/validación de `metricas.json`. `metricas_ml` es nullable en el esquema; si el archivo no existe o es inválido produce `null` sin fallar.

Se reprodujo el entrenamiento con exportación del modelo interceptada y métricas en un directorio temporal: el JSON completo coincide con el versionado, incluidas CV, subgrupos y residuos. El cierre principal de metodología está implementado. La configuración exportada sigue elegida explícitamente en el script; coincide con la ganadora de CV, pero no se selecciona automáticamente si cambia la comparación. No se agregaron tests específicos del nuevo entrenamiento, subgrupos o residuos. Una comprobación adicional de referencia simple (mantener consumo histórico) dio MAE 479.20 frente a 130.11 del modelo; esa comparación todavía no forma parte del script ni del JSON entregado.

## Grafos e infraestructura

Union-Find propio con compresión y rango; Kruskal manual y Edmonds–Karp manual con BFS residual. NetworkX representa grafos y compara totales con tolerancia 0.1. No exigir la misma asignación de flujos, que puede no ser única.

Kruskal incorpora nodos declarados y rechaza redes vacías/desconectadas; las rutas informan 503. MST y candidatos se leen del mismo caso. Se conservan pruebas de costo conocido y conservación. Flujo máximo prioriza suministro total, sin restricciones de equidad: un barrio puede recibir cero y el reparto puede variar entre soluciones máximas.

## API y contrato

`POST /api/simular-red` recibe `caso_red` original/progresivo (original por omisión) y `escenario_crecimiento` positivo <=5. Responde caso/crecimiento, 17 nodos, 16 MST, 26 candidatos, 16 flujos, resumen y métricas nullable. Tipos de caso fuera del enum producen 422; nunca se aceptan rutas del cliente.

Cada barrio agrega `caudal_abastecido_m3_dia` y `deficit_m3_dia`, calculados desde su flujo a SUPER_SUMIDERO, no del tránsito por una cañería. PLANTA no es consumidora y usa null. Antes de redondear se verifican finitud, no negatividad, suministro <= demanda y suma igual al flujo máximo. El resumen suma las cantidades publicadas por barrio a dos decimales, evitando diferencias acumuladas; explica variaciones de centésimas frente a totales anteriores.

Las rutas auxiliares de inspección conservan el caso original. Predicción individual estable por categoría y validación 422 de tipos no admitidos. Métricas ausentes/inválidas devuelven null sin constantes. Contrato en `contrato-api.md` y `casos-capacidad.md`. CORS actual admite cualquier origen sin credenciales; revisar origen Vercel definitivo.

## Pruebas y resultados comprobados

- Backend: **25 pruebas aprobadas**, siete archivos. Nuevas pruebas recorren ASGI/FastAPI completo, seis combinaciones, coherencia de casos/candidatos/MST, balances individuales/globales, ejemplo PLANTA–A–B que separa tránsito/consumo, rechazo 422 y CSV reproducible sin cambiar el original.
- Frontend: **43 aprobadas**, seis archivos; lint, TypeScript y build aprobados. Nuevas pruebas de datos incompatibles, API que ignora caso, escenario equivocado, presentación/comparación, cancelación, respuestas tardías y fallo parcial.
- HTTP local: seis simulaciones 200 y caso inválido 422. Progresivo Base demanda/suministro/déficit 2167.62/2167.62/0; +10 % 2192.42/2192.42/0 (entrada ~99.9 %); +30 % 2242.09/2195.00/47.09 m³/día. Original sigue insuficiente en los tres. Tabla completa en `casos-capacidad.md`.
- Edge con API local: 17 nodos, tabla de 16 barrios, comparación de tres filas, transición a déficit, sin excepciones y móvil de 390 px sin desbordamiento. Capturas nuevas `capturas/caso-progresivo-*` son locales; las anteriores documentan el Render previo.
- Antes de agrupar los cambios se repitieron 25/43 pruebas, lint y build, más el recorrido Edge. Una desconexión simulada mostró error conservando los 16 barrios y el caso/escenario anterior; reintentar tras restablecer la red recuperó la respuesta. La guía manual está en `casos-capacidad.md`.
- Build principal ~270 kB JS / 83 kB gzip; vista Efectos diferida ~20 kB / 7 kB gzip y Pikachu ~49 kB.
- Instalación limpia previa a los efectos: dependencias fijadas, entornos nuevos, pip check, 22/33 pruebas de esa etapa y build/lint aprobados. No equivale a prueba en otra computadora o Linux. No reinstalar sobre procesos ajenos ni detener servidores que no pertenecen al QA propio.

## Informe y uso de IA

Informe vivo alineado con lo probado. Errores, detección, solución y pruebas se registran en su sección de IA, sin atribución personal. Codex/Gemini, paletasdecolores.com.ar, exploración en Figma, patrones declarados del proyecto anterior de Ciro y React Bits están diferenciados. No se inspeccionó código previo ni se atribuye copia literal; no agregar funciones ajenas al alcance como reutilizadas. Registrar solo intervenciones adicionales de IA confirmadas por el grupo.

## Hosting y entorno

Vercel frontend + Render FastAPI. Python 3.12.10 en `.python-version`; requirements fija dependencias directas/transitivas, con scikit-learn 1.9.1 compatible con el modelo. Node 24.20.0/npm 11.19.0 conocidos; engines fija Node 24.x, lockfile conserva paquetes. No se agregaron dependencias para estas mejoras.

Render desde raíz: `pip install -r backend/requirements.txt`; `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`. PYTHON_VERSION, si existe, tiene prioridad y debe coincidir. Vercel raíz frontend, preset Vite y configuración en vercel.json (`npm ci`, `npm run build`, dist); `VITE_API_URL=https://infraestructura-red-api.onrender.com`. Cambiar URL exige reiniciar Vite o recompilar.

Si GitHub sigue siendo un repositorio de cuenta personal, Vercel exige que lo importe su propietario: ser colaborador no basta. Una organización requiere miembros con permisos adecuados; no asumir que habilitar la app permite importarlo desde otra cuenta personal.

## Próximo paso

1. El usuario puede repetir la prueba manual de `casos-capacidad.md` y publicar los commits locales; no se hizo push en esta verificación.
2. Actualizar/verificar API en Render y probar el frontend contra ella antes de publicarlo en Vercel; comprobar CORS, HTTPS e inactividad.
3. Repetir instalación en otra computadora, actualizar capturas/resultados de la versión publicada y cerrar informe/defensa.
4. ML principal ya implementado/reproducido; pruebas específicas, referencia simple en el script y automatización de selección son mejoras adicionales, no integración pendiente de casos/barrios.
