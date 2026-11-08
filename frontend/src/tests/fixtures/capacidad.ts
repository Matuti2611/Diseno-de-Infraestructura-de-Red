import type { SimulacionResponse } from '../../types/red';

/** Caso resuelto a mano, exclusivo de pruebas; no representa predicciones del modelo real.
 * PLANTA–A: 70; A–B: 35. Demanda 20+30 => suministro 50.
 * Demanda 26+39 => suministro 61 y déficit 4. El escenario solo selecciona el mock HTTP.
 */
export function casoCapacidad(conDeficit = false): SimulacionResponse {
  const tendidos = [
    { origen: 'PLANTA', destino: 'A', costo: 10, capacidad_maxima: 70 },
    { origen: 'A', destino: 'B', costo: 5, capacidad_maxima: 35 },
  ];
  return {
    nodos: [
      { id: 'PLANTA', latitud: -32.95, longitud: -60.65, tipo_zona: 'planta', demanda_diaria_proyectada: 0 },
      { id: 'A', latitud: -32.954, longitud: -60.65, tipo_zona: 'residencial', demanda_diaria_proyectada: conDeficit ? 26 : 20 },
      { id: 'B', latitud: -32.958, longitud: -60.645, tipo_zona: 'residencial', demanda_diaria_proyectada: conDeficit ? 39 : 30 },
    ],
    tendidos_mst: tendidos,
    tendidos_candidatos: structuredClone(tendidos),
    flujos: [
      { origen: 'PLANTA', destino: 'A', flujo_actual: conDeficit ? 61 : 50, capacidad_maxima: 70, saturada: false },
      { origen: 'A', destino: 'B', flujo_actual: conDeficit ? 35 : 30, capacidad_maxima: 35, saturada: conDeficit },
    ],
    metricas_ml: null,
    resumen_capacidad: {
      demanda_total_m3_dia: conDeficit ? 65 : 50,
      caudal_abastecido_m3_dia: conDeficit ? 61 : 50,
      deficit_m3_dia: conDeficit ? 4 : 0,
    },
  };
}
