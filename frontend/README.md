# Página de la cooperativa de agua

React + TypeScript estricto + Vite, con CSS propio y SVG. Presenta resultados de la API; no entrena ni calcula MST/flujo en el navegador.

## Arranque y configuración

Node 24.x, probado con 24.20.0/npm 11.19.0. Desde la raíz, después de levantar el backend local según [README](../README.md):

```powershell
cd frontend
npm.cmd ci
$env:VITE_API_URL='http://127.0.0.1:8000'
npm.cmd run dev
```

Abrir la URL indicada por Vite, normalmente `http://127.0.0.1:5173`. En PowerShell usar npm.cmd evita cambiar la política de scripts. También se puede configurar VITE_API_URL en un archivo .env.local ignorado; no sobrescribir uno existente sin revisar su contenido.

Sin configuración explícita el cliente usa `https://infraestructura-red-api.onrender.com`, cuya versión actual no se verificó en esta revisión. La URL no lleva /api al final. Cambiarla requiere reiniciar Vite o recompilar el despliegue. No contiene secretos: queda incorporada al JavaScript.

## Recorrido

- Tendidos: candidatos, MST, costo, selección de barrio/arista y tabla con búsqueda.
- Capacidad: caudales/utilización, resumen de demanda/suministro/déficit, detalle y tabla de barrios.
- Original/Progresivo cambian capacidades, conservando costos, geometría y modelo.
- Base/+10 %/+30 % multiplican la tasa anual poblacional. El MST puede mantenerse; el diagnóstico cambia.
- Comparar escenarios consulta tres balances completos del mismo caso sin cambiar el escenario principal del gráfico.
- Efectos muestra Pikachu/HoloCard como exploración independiente de los resultados. El loader aparece durante solicitudes reales.

En Progresivo, Base/+10 % quedan cubiertos y +30 % produce déficit ~47.09 m³/día con los archivos entregados. El flujo máximo no garantiza equidad: no interpretar el reparto como una política de asignación justa.

## Manejo de datos y errores

El cliente valida números finitos, identificadores, referencias, candidatos/MST, capacidades y balances por barrio/globales. Un cero informado se muestra como cero; los datos ausentes no se inventan. Sin resumen no se declara cobertura suficiente.

Progresivo exige confirmación de caso y crecimiento. Si una API antigua ignora el caso, se muestra un error sin etiquetar Original como Progresivo. Ante error/carga se conserva el resultado anterior identificado; las respuestas tardías se descartan. La comparación se cancela al cambiar de caso y no muestra una tabla parcial si falla una consulta.

Se espera hasta 90 segundos para contemplar inicio del servicio. No hay modo demo de producción ni fallback silencioso a fixtures. La API aporta geometría/candidatos; casoRed.json solo completa geometría de respuestas anteriores coincidentes. Si cambia el CSV original, sincronizar desde raíz con `python frontend/scripts/sincronizar_datos.py` y revisar el diff.

## Organización y pruebas

- `src/api/`: comunicación HTTP y validación del contrato.
- `src/hooks/useSimulacion.ts`: solicitud actual, cancelación, caso/escenario e intento.
- `src/lib/red.ts`: adaptación y formatos de presentación.
- `src/components/`, `src/views/`: controles, SVG, detalles, tablas y comparación.
- `src/components/effects/`: HoloCard y LatticeLoader adaptados de React Bits.
- `src/tests/`: contrato, red, interacción, errores y efectos; fixtures exclusivos de pruebas.

Dentro de frontend:

```powershell
npm.cmd test
npm.cmd run lint
npm.cmd run typecheck
npm.cmd run build
```

43 pruebas frontend aprobadas, lint y build con TypeScript. Cubren búsquedas/teclado, errores de red/timeout, cero frente a ausencia, validación de balances, concurrencia/cancelación, cambios de caso, comparación, reintento y alternativa sin WebGL. No sustituyen los tests matemáticos de Python. Estado completo: [verificacion-proyecto.md](../docs/verificacion-proyecto.md).

Se comprobó Edge con API local: 17 nodos, 16 barrios, comparación y recuperación tras desconexión; móvil de 390 px sin desbordamiento de página. Tabla y grafo usan desplazamiento interno cuando lo necesitan.

El lockfile fija los paquetes; overrides de minimatch limitados a herramientas lint conservan el ajuste de seguridad comprobado. No se incorporaron paquetes para las ampliaciones de capacidad.

## Vercel y procedencia

vercel.json configura Vite, npm ci, npm run build y salida dist. Importar con raíz frontend, Node 24.x y VITE_API_URL de la API pública actualizada. Ver [despliegue](../docs/despliegue.md); no se confirma publicación del frontend.

React Bits fue elegido por Ciro, no es una herramienta de generación IA. Código/imagen y licencia en [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), decisiones en [efectos-visuales.md](../docs/efectos-visuales.md). Los efectos respetan movimiento reducido y la tarjeta conserva una imagen sin WebGL. TechText no se incorporó. Otras mejoras visuales se consultan antes de implementarlas.
