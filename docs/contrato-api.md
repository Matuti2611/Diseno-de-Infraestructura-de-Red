# Contrato de API y capacidad

Contrato actual implementado y probado localmente. La API pública de Render fue comprobada con una versión anterior; no se confirma que ya entregue las ampliaciones de casos y barrios. Reglas y resultados en [casos-capacidad.md](casos-capacidad.md).

## Petición

`POST /api/simular-red`, Content-Type application/json:

```json
{"caso_red": "progresivo", "escenario_crecimiento": 1.3}
```

- `caso_red`: `original` por omisión o `progresivo`. Un valor ajeno al enum produce 422; nunca es una ruta de archivo.
- `escenario_crecimiento`: positivo y <=5; multiplica la **tasa anual de crecimiento poblacional**, no directamente el consumo.
- La respuesta confirma ambos valores. La selección de caso solo cambia capacidades, manteniendo candidatos, geometría, costos y modelo.
- Red candidata vacía/desconectada: 503. Una petición inválida se rechaza mediante validación de FastAPI/Pydantic.

## Respuesta

| Campo | Contenido |
| --- | --- |
| `caso_red`, `escenario_crecimiento` | Identificación de la solicitud calculada |
| `nodos` | PLANTA y barrios con coordenadas, tipo y demanda diaria |
| `tendidos_mst` | Conexiones elegidas con origen, destino, costo y capacidad |
| `tendidos_candidatos` | Alternativas del mismo CSV/caso usado por Kruskal |
| `flujos` | Todos los enlaces del MST, incluidos caudales cero |
| `resumen_capacidad` | Demanda, suministro y déficit generales |
| `metricas_ml` | MAE, RMSE y R² persistidos válidos, o null |

Cada barrio incluye `demanda_diaria_proyectada`, `caudal_abastecido_m3_dia` y `deficit_m3_dia`, en m³/día. Su suministro se obtiene del flujo hacia SUPER_SUMIDERO, no de la cañería de entrada. PLANTA tiene demanda cero y los campos de suministro/déficit son null, porque es fuente.

Antes de redondear se verifican valores finitos, no negatividad, suministro <= demanda y suma de consumos igual al flujo máximo. El resumen suma cantidades publicadas por barrio a dos decimales para mantener su balance. Puede haber diferencias de centésimas respecto al flujo de precisión completa.

Todos los tendidos seleccionados deben estar entre candidatos con iguales costos/capacidades. Los extremos identifican conexiones **no dirigidas**; `flujo_actual` es magnitud neta no negativa y no expresa sentido físico. No sumar todos los caudales de cañerías como suministro: contaría agua en tránsito más de una vez.

`saturada` corresponde al 100 % con tolerancia numérica. La página distingue también cercanía desde 90 %. Máximo flujo optimiza suministro total; no garantiza equidad ni una asignación única por barrio.

## Validación y compatibilidad del cliente

- Verifica identificadores, referencias, duplicados, números finitos, capacidades, candidatos/MST y balances.
- Para el resumen anterior sin desglose, tolera redondeo acumulado con max(0.1 m³/día, demanda × 10⁻⁶).
- Si hay balances por barrio, deben estar completos, suministro <= demanda y cuadrar dentro de 0.011 m³/día; sus sumas deben coincidir con el resumen dentro de esa tolerancia.
- Original admite respuestas anteriores sin metadatos/desglose. Un dato ausente aparece como no informado, no como cero. Sin resumen no se declara cobertura.
- Progresivo exige confirmar caso/crecimiento; una API antigua que ignore el campo genera error en vez de mostrar otro caso.
- Respuestas de otro caso/escenario, errores HTTP o contratos inválidos no reemplazan un resultado válido silenciosamente. La comparación requiere las tres respuestas completas.

## Caso conocido de pruebas

Capacidades PLANTA–A=70 y A–B=35 m³/día:

| Demanda A/B | Suministro A/B | Flujo PLANTA–A / A–B | Déficit total |
| --- | --- | --- | --- |
| 20 / 30 | 20 / 30 | 50 / 30 | 0 |
| 26 / 39 | 26 / 35 | 61 / 35 | 4 |

Valores fijados a mano para verificar algoritmos y presentación, no predicciones del modelo. Los mocks permanecen en tests.

## Otras rutas

`GET /api/red/nodos`, `/conexiones`, `/mst` inspeccionan el caso original. `GET /api/modelo/status`, `/metricas` y `POST /api/modelo/predecir` permiten inspección/predicción individual. Tipos de zona fuera de los tres admitidos producen 422. Métricas ausentes/inválidas dan null, sin constantes de respaldo.

La cobertura actual de pruebas y publicación se mantiene en [verificacion-proyecto.md](verificacion-proyecto.md).
