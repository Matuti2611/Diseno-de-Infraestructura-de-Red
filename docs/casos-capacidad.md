# Casos de capacidad y abastecimiento por barrio

## Alcance y regla del ejemplo

Se conserva el caso original y se integra el CSV progresivo preparado por Matías. Por indicación de Ciro, se completó con Codex la selección por API, el abastecimiento por barrio, su presentación, la comparación de escenarios y las pruebas. No se cambia el modelo, la población, los costos ni la geometría al elegir otro caso.

El caso progresivo copia los enlaces, distancias y costos de `aristas_candidatas.csv`, asignando **2195 m³/día** a PLANTA–Z01 y **2500 m³/día** a los demás. El MST conserva PLANTA–Z01 como entrada; esa cañería se convierte en cuello de botella cuando la demanda supera su capacidad. Es un ejemplo sintético declarado, no un dimensionamiento hidráulico real.

Se reproduce desde la raíz con:

```powershell
python backend/app/data/generar_caso_progresivo.py
```

El generador se niega a sobrescribir el archivo de entrada. Las capacidades quedan fijas: no se reajustan a cada predicción. La transición se verificó con datos y modelo versionados; al cambiar semilla, topología o modelo se debe repetir la comprobación. Alternar capacidades no requiere reentrenar ML.

## Contrato

`POST /api/simular-red` admite:

```json
{"caso_red": "progresivo", "escenario_crecimiento": 1.3}
```

`caso_red` admite `original` o `progresivo`; por omisión es `original`, conservando las peticiones anteriores. Nunca acepta una ruta proporcionada por el cliente. El multiplicador modifica la tasa anual poblacional, no directamente el consumo.

La respuesta identifica `caso_red` y `escenario_crecimiento`. Cada barrio tiene `demanda_diaria_proyectada`, `caudal_abastecido_m3_dia` y `deficit_m3_dia`. El suministro sale del flujo hacia `SUPER_SUMIDERO`; no de la cañería que llega, que puede transportar consumo de otros barrios. Los campos de suministro/déficit son null en PLANTA, porque es fuente y no consumidora.

Antes de redondear se comprueban valores finitos, no negativos, suministro <= demanda y suma de suministros igual al flujo máximo. Se publican cantidades por barrio con dos decimales; el resumen suma esas mismas cantidades para evitar diferencias acumuladas. Esto explica cambios de centésimas frente a balances anteriores que redondeaban solo el total.

MST y candidatos se leen del mismo caso. Las rutas auxiliares `GET /api/red/...` conservan la inspección del caso original; la selección se hace en el POST de simulación.

## Resultados HTTP locales

Cantidades en m³/día; corresponden a la API local actualizada, sin publicar:

| Caso | Crecimiento | Demanda | Suministro | Déficit |
| --- | --- | --- | --- | --- |
| Original | Base | 2167.62 | 1435.89 | 731.73 |
| Original | +10 % | 2192.42 | 1440.39 | 752.03 |
| Original | +30 % | 2242.09 | 1449.40 | 792.69 |
| Progresivo | Base | 2167.62 | 2167.62 | 0 |
| Progresivo | +10 % | 2192.42 | 2192.42 | 0 |
| Progresivo | +30 % | 2242.09 | 2195.00 | 47.09 |

Con +10 %, la entrada del caso progresivo utiliza aproximadamente 99.9 %; con +30 % llega al límite. El flujo máximo optimiza suministro total, sin imponer equidad: el reparto y los barrios afectados pueden variar entre soluciones máximas válidas.

## Página y compatibilidad

El selector de capacidades acompaña al crecimiento; se identifica el caso y escenario realmente mostrados, incluso al conservar una respuesta anterior durante carga/error. En Capacidad aparecen suministro/déficit en el detalle y una tabla de barrios.

«Comparar escenarios» consulta Base/+10 %/+30 % para el mismo caso y presenta demanda, suministro, déficit y cobertura sin cambiar el escenario del gráfico. No extrapola resultados ni suma cañerías. Cambiar de caso cancela la comparación anterior; si falla una consulta, no muestra una tabla parcial.

El frontend exige confirmación de caso y crecimiento para Progresivo: una API antigua podría ignorar esos campos. Original admite respuestas anteriores; si falta abastecimiento por barrio, informa su ausencia y nunca lo trata como cero. Cambiar `VITE_API_URL` requiere reiniciar Vite o reconstruir el despliegue.

## Pruebas y publicación

### Prueba manual desde PowerShell

En una terminal, desde la raíz del repositorio:

```powershell
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

En otra terminal, también desde la raíz:

```powershell
cd frontend
$env:VITE_API_URL='http://127.0.0.1:8000'
npm.cmd run dev
```

Abrir la dirección que indique Vite, normalmente `http://127.0.0.1:5173`. La variable afecta solo esa terminal; no cambia la configuración de Render/Vercel ni archivos de entorno. Si el puerto está ocupado, usar la dirección que indique Vite.

1. Elegir **Progresivo** y abrir **Capacidad**. Base debe cubrir toda la demanda.
2. Elegir **+10 %**: sigue cubriendo y PLANTA–Z01 queda aproximadamente al 99.9 %.
3. Elegir **+30 %**: aparecen suministro 2195 y déficit 47.09 m³/día, con entrada saturada.
4. Pulsar **Comparar escenarios**: comprobar tres filas del mismo caso, déficit 0/0/47.09 y que el escenario del gráfico no cambie.
5. Revisar la tabla de barrios y seleccionar uno: demanda = suministro + déficit; los ceros informados se muestran como cero. No confundir caudal de una cañería con consumo del barrio.
6. Volver a **Original**: conserva su red de capacidades y muestra déficit en los tres escenarios. Cambiar casos/escenarios rápidamente no debe mezclar respuestas.
7. En una pantalla estrecha, las tablas se desplazan dentro de su panel sin desbordar la página.
8. Detener la API con Ctrl+C y actualizar la simulación: debe aparecer error, conservar el resultado anterior identificado y permitir reintentar. Reiniciar la API y reintentar debe recuperarlo. Cerrar Vite con Ctrl+C al terminar.

Los valores corresponden al modelo/CSV versionados. Esta prueba usa la API local; Render debe actualizarse antes de esperar que su URL ofrezca el caso nuevo.

### Verificaciones automatizadas

- **28 pruebas backend aprobadas**: las pruebas de casos cubren ruta ASGI completa, seis combinaciones, capacidad cerca del límite, conservación del original y coherencia MST/candidatos, balances individuales/globales, ejemplo conocido PLANTA–A–B, rechazo 422 de casos no admitidos y reproducción del CSV sin alterar el original.
- **43 pruebas frontend aprobadas**, lint, TypeScript y build. Seis nuevas cubren balances inválidos, API que ignora el caso o devuelve otro crecimiento, presentación/comparación, cancelación, respuestas tardías y fallo parcial sin datos inventados.
- HTTP real local: seis simulaciones 200 y caso desconocido 422. Edge: 17 nodos, 16 barrios, comparación completa, cambio a déficit y móvil de 390 px sin desbordamiento ni excepciones.
- Capturas de integración local: [comparación](capturas/caso-progresivo-comparacion.png) y [controles en móvil](capturas/caso-progresivo-movil.png). No corresponden a una publicación nueva de Render/Vercel.

Verificación actual de cierre: 28/43 pruebas, lint y build aprobados. Edge también simuló una desconexión: mostró error, conservó el caso/escenario anterior con sus 16 barrios y se recuperó al reintentar. La prueba manual anterior queda disponible para el usuario.

El usuario realiza el push; el estado de commits y ajustes pendientes se mantiene en `context.md`. Si se publica, primero actualizar/verificar la API de Render y después el frontend con esa URL. Probar otra computadora es recomendable; estas verificaciones locales no declaran un despliegue público actualizado.
