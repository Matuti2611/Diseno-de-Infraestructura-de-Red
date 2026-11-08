import caso from '../data/casoRed.json';
import { idArista } from '../api/validar';
import type { AristaVisual, EstadoTramo, NodoVisual, RedVisual, SimulacionResponse } from '../types/red';

export const numero = (valor: number, decimales = 1) => new Intl.NumberFormat('es-AR', { maximumFractionDigits: decimales }).format(valor);
export const nombreNodo = (id: string) => id === 'PLANTA' ? 'Planta de agua' : /^Z\d+$/.test(id) ? `Barrio ${id.slice(1)}` : id;
export const nombreEscenario = (escenario: number) => escenario === 1 ? 'Base' : `+${Math.round((escenario - 1) * 100)} %`;
export const etiquetasEstado: Record<EstadoTramo, string> = {
  candidato: 'No seleccionado', 'sin-dato': 'Sin dato de flujo', informado: 'Flujo informado',
  cercano: 'Cerca del límite', saturado: 'Saturado', 'sin-capacidad': 'Sin capacidad',
};

export function estadoTramo(flujo: number | null, capacidad: number, seleccionada = true): EstadoTramo {
  if (!seleccionada) return 'candidato';
  if (capacidad === 0) return 'sin-capacidad';
  if (flujo === null) return 'sin-dato';
  if (flujo / capacidad >= 1 - 1e-6) return 'saturado';
  return flujo / capacidad >= 0.9 ? 'cercano' : 'informado';
}

/** La geometría CSV solo se agrega si coincide con los nodos y tendidos de la API. */
export function construirRed(respuesta: SimulacionResponse): RedVisual {
  const barrios = respuesta.nodos.filter(n => n.id !== 'PLANTA');
  const mismaGeometria = barrios.length === caso.zonas.length && barrios.every(n => caso.zonas.some(z =>
    z.id === n.id && Math.abs(z.latitud - n.latitud) < 1e-6 && Math.abs(z.longitud - n.longitud) < 1e-6,
  ));
  const mismoCaso = mismaGeometria && respuesta.tendidos_mst.every(a => caso.aristas.some(c =>
    idArista(a.origen, a.destino) === idArista(c.origen, c.destino)
    && Math.abs(a.costo - c.costo) < 0.02 && Math.abs(a.capacidad_maxima - c.capacidad_maxima) < 1e-6,
  ));
  const nodos: NodoVisual[] = respuesta.nodos.map(n => ({
    ...n, demanda: n.id === 'PLANTA' ? null : n.demanda_diaria_proyectada,
    poblacion: mismaGeometria ? caso.zonas.find(z => z.id === n.id)?.poblacion : undefined,
  }));
  if (mismaGeometria && !nodos.some(n => n.id === 'PLANTA')) {
    nodos.unshift({ ...caso.planta, tipo_zona: 'planta', demanda: null });
  }
  const fuenteGeometria = respuesta.tendidos_candidatos ? 'api' : mismoCaso ? 'csv' : 'solo-mst';
  const candidatos = respuesta.tendidos_candidatos ?? (mismoCaso ? caso.aristas : respuesta.tendidos_mst);
  const aristas: AristaVisual[] = candidatos.map(a => {
    const id = idArista(a.origen, a.destino);
    const seleccionada = respuesta.tendidos_mst.some(m => idArista(m.origen, m.destino) === id);
    const flujo = respuesta.flujos.find(f => idArista(f.origen, f.destino) === id)?.flujo_actual ?? null;
    return {
      ...a, id, seleccionada, flujo,
      utilizacion: flujo !== null && a.capacidad_maxima > 0 ? flujo / a.capacidad_maxima * 100 : null,
      estado: estadoTramo(flujo, a.capacidad_maxima, seleccionada),
    };
  });
  return {
    nodos, aristas, fuenteGeometria, cantidadBarrios: barrios.length,
    costoTotal: respuesta.tendidos_mst.reduce((s, a) => s + a.costo, 0),
    demandaTotal: barrios.reduce((s, n) => s + n.demanda_diaria_proyectada, 0),
    tramosCriticos: aristas.filter(a => a.seleccionada && ['cercano', 'saturado', 'sin-capacidad'].includes(a.estado)).length,
    flujosInformados: respuesta.flujos.length,
    ubicacionesFaltantes: [...new Set(respuesta.tendidos_mst.flatMap(a => [a.origen, a.destino]))].filter(id => !nodos.some(n => n.id === id)),
    resumenCapacidad: respuesta.resumen_capacidad ?? null,
  };
}
