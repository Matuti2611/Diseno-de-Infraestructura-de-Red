# Página de la cooperativa de agua

Panel en React + TypeScript estricto + Vite. Usa la API real de Render para mostrar proyecciones, tendidos y capacidad; no calcula predicciones, MST ni flujo en el navegador.

## Ejecutar

Requiere Node 22.12 o posterior; verificado con Node 24.20.0 y npm 11.19.0. Desde la raíz:

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev
```

Abrir `http://127.0.0.1:5173`. En PowerShell se usa `npm.cmd` para evitar cambiar la política de ejecución de scripts. En otros entornos puede usarse `npm`.

La API predeterminada es `https://infraestructura-red-api.onrender.com`. Para cambiarla, copiar `.env.example` a `.env.local`, modificar `VITE_API_URL` y reiniciar Vite. La dirección no lleva `/api` al final. Para un backend local iniciado desde la raíz del repositorio, usar `http://127.0.0.1:8000`.

El servicio de Render puede tardar en responder después de inactividad. La interfaz avisa durante la carga y permite reintentar; el cliente espera hasta 90 segundos. Un fallo nunca se sustituye por resultados de ejemplo.

## Qué permite hacer

- Alternar Tendidos y Capacidad, seleccionar barrios o conexiones y buscar en la tabla.
- Solicitar escenarios base, +10 % y +30 %. Estos valores multiplican la **tasa de crecimiento poblacional** usada por el predictor; no aumentan directamente la demanda en ese porcentaje.
- Ver demanda proyectada, costo del MST y utilización de los tramos informados por la API.
- Consultar las métricas enviadas por el backend y las limitaciones del caso sintético.

La API actual devuelve 16 barrios y 16 tendidos, pero solo dos registros de flujo en el escenario base. Los otros 14 se identifican como **Sin dato**; no se interpretan como flujo cero. Se distingue utilización desde 90 % de saturación al 100 % mediante el cociente flujo/capacidad. Caudal abastecido y déficit total siguen pendientes de la API.

## Archivos y fuentes

- `src/api/`: cliente HTTP, cancelación y validación del contrato JSON.
- `src/hooks/useSimulacion.ts`: carga, reintento y protección ante respuestas fuera de orden; conserva el escenario del último resultado durante una nueva solicitud.
- `src/data/`: geometría y conexiones candidatas del caso versionado.
- `src/lib/red.ts`: adaptación de resultados para presentación, sin algoritmos de predicción, MST o flujo.
- `src/components/` y `src/views/`: gráfico SVG, detalles, escenarios, indicadores y tabla; las dos vistas comparten los datos.
- `src/styles/global.css`: paleta elegida, estados, foco y diseño adaptable. En móvil el gráfico y la tabla tienen desplazamiento horizontal interno para mantener legibles sus etiquetas.
- `src/tests/`: pruebas de contrato, red e interacción; los JSON de prueba no participan en la aplicación publicada.

Como la API todavía omite la planta y las conexiones candidatas, `src/data/casoRed.json` incluye sus coordenadas, costos y capacidades desde los CSV versionados del backend. **No incluye predicciones ni resultados simulados.** Solo se usa cuando los barrios y tendidos recibidos coinciden con el caso local; si no coinciden, se muestra únicamente la red recibida y se avisa si faltan coordenadas. Cuando el servidor entregue `tendidos_candidatos`, se priorizarán esos datos.

Si Matías cambia los CSV, actualizar esta copia desde la raíz y revisar el diff:

```powershell
python frontend/scripts/sincronizar_datos.py
```

El JSON se versiona para que Vercel pueda compilar solo `frontend/`, sin Python. Coordinar la actualización de los CSV, el backend publicado y este archivo.

## Verificación

Dentro de `frontend/`:

```powershell
npm.cmd test
npm.cmd run lint
npm.cmd run typecheck
npm.cmd run build
```

El 08/11/2026 pasaron 22 pruebas, lint y build (que incluye TypeScript). Las pruebas detectan datos inválidos, flujos imposibles, respuestas HTTP fallidas, espera agotada, confusión entre cero y dato ausente, escenarios desordenados, reintento y pérdida del resultado anterior. Se verificaron también búsqueda y selección por teclado. Son pruebas del frontend; no demuestran la corrección matemática del backend.

Se probó en Edge con Render real: 17 nodos, 26 conexiones candidatas, 16 tendidos seleccionados, demanda base 2167.74 m³/día y escenario +30 % con 2242.3 m³/día mostrados. A 390 px no hay desbordamiento horizontal de la página; el gráfico mantiene su desplazamiento interno. Capturas en [docs/capturas](../docs/capturas/).

`package-lock.json` fija la instalación. Los overrides de `minimatch` están limitados a herramientas de lint para resolver el aviso GHSA-g3hv-75wg-m249 de la versión transitiva anterior; se comprobó el árbol instalado y el lint con la versión 11.0.5. La instalación final informó cero vulnerabilidades conocidas. Los artefactos de QA y perfiles temporales quedan ignorados en `.preview/` y excluidos del watcher de Vite.

## Vercel

Preparado para raíz `frontend`, preset Vite, build `npm run build` y salida `dist`. Usar Node 24.x y `VITE_API_URL=https://infraestructura-red-api.onrender.com`; la variable es pública y se incorpora al compilar. Tras cambiarla hay que reconstruir. Aún no se publicó el frontend: falta importar el repositorio, coordinar CORS con el origen definitivo y verificar la página por HTTPS. Ver [despliegue](../docs/despliegue.md).
