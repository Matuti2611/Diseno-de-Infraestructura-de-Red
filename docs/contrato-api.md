# Contrato de API e integración de capacidad

Estado: **implementado en backend y frontend y comprobado en Render**. La respuesta pública ya incluye planta, candidatos, 16 flujos y resumen. Se conserva compatibilidad del cliente con respuestas que omitan los campos opcionales. Los cierres pendientes están en `verificacion-proyecto.md`.

Corrección local posterior: `metricas_ml` es objeto válido o `null` si su archivo está ausente/inválido; `GET /api/modelo/metricas` también devuelve null en ese caso. No hay cifras constantes de respaldo. La página ya admite esa ausencia. La API informa HTTP 503 si la red candidata no conecta todos los nodos y el endpoint individual rechaza tipos de zona no admitidos con 422. Se comprobó HTTP local; falta publicar estas correcciones. Error, detección y resolución se documentan en la sección de IA de `Informe.md`.

## Lo que ya consume la página

`POST /api/simular-red`, cuerpo `{"escenario_crecimiento": 1.0}`. Los presets son 1.0, 1.1 y 1.3. Actualmente multiplican la **tasa anual de crecimiento poblacional**; no multiplican directamente la demanda. Mantener esquema, textos y predictor alineados.

La respuesta conserva `nodos`, `tendidos_mst`, `flujos` y `metricas_ml`. Predicciones, MST, flujo máximo y balance se calculan en Python. El navegador valida y presenta; no reconstruye el abastecimiento sumando caudales de cañerías, porque eso contaría el mismo agua más de una vez.

## Campos implementados y reglas del intercambio

1. Incluir `PLANTA` en `nodos`, con sus coordenadas y demanda cero; los barrios mantienen su demanda proyectada en m³/día.
2. Incorporar `tendidos_candidatos`, una lista con `origen`, `destino`, `costo`, `capacidad_maxima`, igual estructura básica que los seleccionados. Todos los elementos del MST deben estar entre los candidatos con los mismos costos y capacidades. Se prioriza esta lista sobre la geometría CSV local.
3. Enviar `flujos` para **todos** los tendidos del MST, incluido el flujo cero. `flujo_actual` es una magnitud no negativa y no supera `capacidad_maxima`; los extremos identifican el tendido no dirigido, sin inferir sentido físico. No filtrar los registros por utilización. La página distingue cercanía desde 90 % y saturación al 100 % mediante el cociente; alinear también `saturada`.
4. Agregar el resumen calculado por el pipeline:

```json
{
  "resumen_capacidad": {
    "demanda_total_m3_dia": 65,
    "caudal_abastecido_m3_dia": 61,
    "deficit_m3_dia": 4
  }
}
```

Los números son un **caso de prueba resuelto a mano**, no una respuesta del modelo publicado. El resumen se agrega al objeto de simulación existente, no reemplaza sus listas.

- `demanda_total_m3_dia`: suma de las demandas de barrios, excluyendo planta.
- `caudal_abastecido_m3_dia`: valor total de flujo máximo retornado por el cálculo hacia el supersumidero.
- `deficit_m3_dia`: demanda total menos caudal abastecido.
- Todos son finitos y no negativos; suministro no supera demanda. No enviar ceros para representar valores desconocidos.
- El resumen debe pertenecer al mismo escenario que nodos y flujos. No reutilizar un total base con demandas recalculadas.

Para compatibilidad, omitir `resumen_capacidad` o usar `null` deja el diagnóstico como incompleto. Si se entrega el objeto, los tres campos son obligatorios. El cliente valida suma de demandas y balance con tolerancia `max(0.1 m³/día, suma de demandas × 10⁻⁶)`, para redondeo acumulado; no corrige balances inválidos silenciosamente. Evitar redondear antes de los cálculos y mantener precisión en JSON.

El resumen basta para presentar cobertura global. No identifica por sí solo qué barrio tiene déficit; eso requeriría un dato adicional calculado por el backend, todavía fuera de esta extensión.

## Qué ya está preparado en frontend

- Cada tendido seleccionado tiene etiqueta de caudal y utilización en el gráfico, o **Sin dato** si no se recibió flujo. El cero real se muestra como `0 m³/día`.
- El panel de capacidad presenta demanda, suministro y déficit cuando existe un resumen válido. Sin él no declara que alcanza el agua, aunque tenga todos los flujos o ningún tramo crítico.
- Se muestran resultados del escenario efectivamente recibido; errores de red o de contrato conservan el resultado previo con su identificación.
- Se validan candidatos/MST, flujos/capacidades y balance antes de mostrar resultados. La extensión está cubierta por pruebas con mocks; no hay modo demo ni respuestas simuladas en producción.

## Caso para coordinar pruebas de ambos lados

Red: PLANTA–A con capacidad 70 y A–B con capacidad 35 m³/día.

| Caso de prueba | Demanda A | Demanda B | Demanda total | Flujo PLANTA–A | Flujo A–B | Abastecido | Déficit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Cubierto | 20 | 30 | 50 | 50 | 30 | 50 | 0 |
| Insuficiente | 26 | 39 | 65 | 61 | 35 | 61 | 4 |

Las demandas se fijan manualmente para validar grafos/presentación. No se supone que el predictor real produzca exactamente esas cifras al aumentar la tasa poblacional un 30 %. Los fixtures están solo en `frontend/src/tests/fixtures/capacidad.ts` y no prueban el entrenamiento ni los algoritmos de Python.

## Validación conjunta y cierre

1. Implementación manual y contrato completo presentes; pasaron 22 pruebas backend. Se corrigieron los casos registrados en la sección de IA, incluyendo null de métricas y desconexión. Los casos de la tabla verifican cobertura/déficit con datos controlados.
2. Se verificaron OpenAPI y escenarios 1.0/1.1/1.3 por HTTP en Render y la página en Edge: todos los caudales disponibles y déficit visible. Ver resultados en `verificacion-proyecto.md`.
3. Falta comprobar CORS con el origen definitivo de Vercel, arranque después de inactividad e instalación/demo en otra máquina.
4. Capturas reales renovadas con el contrato completo. Los casos de prueba no se presentan como mediciones ni predicciones reales.
