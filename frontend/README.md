# Página de la cooperativa de agua

Panel en React + TypeScript estricto + Vite. Usa la API real de Render para mostrar proyecciones, tendidos y capacidad; no calcula predicciones, MST ni flujo en el navegador.

## Ejecutar

Requiere Node 24.x; verificado con Node 24.20.0 y npm 11.19.0. `.nvmrc` registra la versión local y `package.json` fija la versión mayor para Vercel. Desde la raíz:

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
- Abrir «Efectos» para ver la carta holográfica de Pikachu, independiente de los resultados. Durante las solicitudes aparece LatticeLoader con tiempo de espera; desaparece al terminar y no mide el avance del algoritmo.

La API actual devuelve planta y 16 barrios, 26 candidatos y 16 tendidos con sus 16 registros de flujo. Cada tendido seleccionado tiene etiqueta de caudal/utilización; un cero informado se muestra como cero. **Sin dato** queda reservado para respuestas incompletas, sin asumir cero. Las etiquetas verticales se ubican al costado para preservar los nombres. Se distingue cercanía desde 90 % de saturación al 100 % mediante flujo/capacidad.

El panel usa el `resumen_capacidad` real de Render para mostrar demanda, suministro, déficit y cobertura. En base se verificaron 2167.74/1435.18/732.56 m³/día: la red no cubre toda la demanda. Se valida consistencia con nodos y balance. Si una respuesta omite el resumen se mantiene **Diagnóstico incompleto**; no se deduce suministro sumando cañerías. Ver [contrato y caso de prueba](../docs/contrato-api.md).

## Archivos y fuentes

- `src/api/`: cliente HTTP, cancelación y validación del contrato JSON.
- `src/hooks/useSimulacion.ts`: carga, reintento y protección ante respuestas fuera de orden; conserva el escenario del último resultado durante una nueva solicitud.
- `src/data/`: geometría y conexiones candidatas del caso versionado.
- `src/lib/red.ts`: adaptación de resultados para presentación, sin algoritmos de predicción, MST o flujo.
- `src/components/` y `src/views/`: gráfico SVG, detalles, escenarios, indicadores y tabla; las dos vistas comparten los datos.
- `src/styles/global.css`: paleta elegida, estados, foco y diseño adaptable. En móvil el gráfico y la tabla tienen desplazamiento horizontal interno para mantener legibles sus etiquetas.
- `src/tests/`: pruebas de contrato, red e interacción; los JSON de prueba no participan en la aplicación publicada.

La API actual aporta planta y candidatos, que se priorizan al dibujar. `src/data/casoRed.json` conserva geometría/costos/capacidades CSV como compatibilidad con la respuesta anterior, solo tras comprobar coincidencia del caso. **No contiene predicciones ni resultados simulados** y no sustituye una API fallida. Si cambia la red sin geometría completa se descarta el complemento y se avisa si faltan coordenadas.

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

Pasaron 37 pruebas, lint y build (que incluye TypeScript). Las pruebas detectan datos inválidos, flujos imposibles, respuestas HTTP fallidas, espera agotada, confusión entre cero y dato ausente, escenarios desordenados, reintento y pérdida del resultado anterior. También verifican búsqueda/teclado, caudales de tramos no críticos y cambio de cobertura a déficit con respuestas controladas. Se rechazan resúmenes que contradicen la demanda o el balance y candidatos con costos/capacidades distintos del MST. Las nuevas pruebas de efectos cubren reinicio/limpieza del contador, retiro ante error/éxito, imagen sin WebGL y navegación sin nuevas simulaciones. Son pruebas del frontend; no demuestran la corrección matemática del backend.

Se repitió la prueba en Edge con Render real tras los cambios de Matías: 17 nodos, 26 candidatos, 16 etiquetas con caudal (cero Sin dato), déficit base 732.56 m³/día y demanda +30 % mostrada como 2242.3 m³/día. A 390 px no hay desbordamiento horizontal de la página; el gráfico mantiene desplazamiento interno. Se renovaron las [capturas](../docs/capturas/). No se cambió código frontend para consumir el contrato completo.

Antes de incorporar los efectos, en una copia separada sin reutilizar `node_modules`, pasaron `npm.cmd ci --offline --no-audit --no-fund`, las 33 pruebas de esa etapa, lint y build con TypeScript. Los efectos no agregan paquetes. Se usó la caché disponible; una computadora nueva necesita acceso al registro para `npm ci`. Los permisos adecuados resolvieron el bloqueo de la comprobación anterior. Falta el ensayo en otra máquina; seguir la [guía de instalación reproducible](../docs/instalacion-reproducible.md).

`package-lock.json` fija la instalación. Los overrides de `minimatch` están limitados a herramientas de lint para resolver el aviso GHSA-g3hv-75wg-m249 de la versión transitiva anterior; se comprobó el árbol instalado y el lint con la versión 11.0.5. La instalación final informó cero vulnerabilidades conocidas. Los artefactos de QA y perfiles temporales quedan ignorados en `.preview/` y excluidos del watcher de Vite.

## Vercel

`vercel.json` configura Vite, instalación con `npm ci`, build `npm run build` y salida `dist`. Al importar el repositorio, seleccionar raíz `frontend`, Node 24.x y `VITE_API_URL=https://infraestructura-red-api.onrender.com`; la variable es pública y se incorpora al compilar. Tras cambiarla hay que reconstruir. Aún no se publicó el frontend: falta subir los cambios, importar el repositorio, coordinar CORS con el origen definitivo y verificar la página por HTTPS. Ver [despliegue](../docs/despliegue.md).

## Efectos y procedencia

HoloCard se carga al abrir su pestaña, conserva la imagen sin WebGL y permite pausar el giro. LatticeLoader acompaña únicamente solicitudes reales y reinicia su reloj por escenario/intento. Ambos respetan movimiento reducido. Edge confirmó textura y reflejos, tarjeta sin desbordamiento a 390 px y vuelta a los 17 nodos/16 caudales reales de Render.

Código TypeScript/CSS adaptado de React Bits, sin Tailwind ni dependencias nuevas. TechText se dejó sin aplicar porque transforma texto, no nodos/aristas. Ver [decisiones y archivos](../docs/efectos-visuales.md) y [procedencia/licencia](THIRD_PARTY_NOTICES.md). Otras mejoras visuales se consultan con el usuario.
