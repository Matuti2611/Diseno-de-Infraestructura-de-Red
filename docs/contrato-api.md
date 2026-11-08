# Integración de capacidad: contrato preparado para Matías

Estado: propuesta de extensión compatible con la respuesta actual, preparada y probada en frontend. **El backend no fue modificado y Render todavía no devuelve el resumen.** Coordinar estos nombres antes de implementarlos o adaptar el cliente si se acuerda otra estructura.

## Lo que ya consume la página

`POST /api/simular-red`, cuerpo `{"escenario_crecimiento": 1.0}`. Los presets son 1.0, 1.1 y 1.3. Actualmente multiplican la **tasa anual de crecimiento poblacional**; no multiplican directamente la demanda. Mantener esquema, textos y predictor alineados.

La respuesta conserva `nodos`, `tendidos_mst`, `flujos` y `metricas_ml`. Predicciones, MST, flujo máximo y balance se calculan en Python. El navegador valida y presenta; no reconstruye el abastecimiento sumando caudales de cañerías, porque eso contaría el mismo agua más de una vez.

## Campos que faltan del backend

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

## Validación conjunta pendiente

1. Matías implementa la extensión y verifica resultados conocidos, conservación de flujo, capacidades y demandas simultáneas; cierra los algoritmos exigidos por la consigna.
2. Contrastar OpenAPI/JSON publicado con este documento y ejecutar los escenarios reales de extremo a extremo.
3. Comprobar un caso cubierto y otro con déficit, cambios de escenarios, tiempos de Render y CORS con el origen definitivo.
4. Renovar capturas reales y registrar resultados reproducidos en el informe. Los casos de prueba no se presentan como mediciones ni predicciones reales.
