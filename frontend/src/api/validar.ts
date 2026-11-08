import type { EstadoFlujo, NodoRed, SimulacionResponse, TendidoMST } from '../types/red';

function objeto(valor: unknown): Record<string, unknown> {
  if (!valor || typeof valor !== 'object' || Array.isArray(valor)) throw new Error('Se esperaba un objeto.');
  return valor as Record<string, unknown>;
}

function texto(valor: unknown): string {
  if (typeof valor !== 'string' || !valor.trim()) throw new Error('Identificador o texto ausente.');
  return valor;
}

function numero(valor: unknown, minimo = 0): number {
  if (typeof valor !== 'number' || !Number.isFinite(valor) || valor < minimo) throw new Error('Valor numérico inválido.');
  return valor;
}

function lista<T>(valor: unknown, transformar: (fila: unknown) => T): T[] {
  if (!Array.isArray(valor)) throw new Error('Falta una colección de la simulación.');
  return valor.map(transformar);
}

function nodo(valor: unknown): NodoRed {
  const v = objeto(valor);
  const latitud = numero(v.latitud, -90);
  const longitud = numero(v.longitud, -180);
  if (latitud > 90 || longitud > 180) throw new Error('Coordenadas fuera de rango.');
  return {
    id: texto(v.id), latitud, longitud, tipo_zona: texto(v.tipo_zona),
    demanda_diaria_proyectada: numero(v.demanda_diaria_proyectada),
  };
}

function tendido(valor: unknown): TendidoMST {
  const v = objeto(valor);
  return { origen: texto(v.origen), destino: texto(v.destino), costo: numero(v.costo), capacidad_maxima: numero(v.capacidad_maxima) };
}

function flujo(valor: unknown): EstadoFlujo {
  const v = objeto(valor);
  if (typeof v.saturada !== 'boolean') throw new Error('Estado de flujo inválido.');
  const capacidad = numero(v.capacidad_maxima);
  const caudal = numero(v.flujo_actual);
  if (caudal > capacidad + Math.max(1, capacidad) * 1e-6) throw new Error('El flujo supera su capacidad.');
  return { origen: texto(v.origen), destino: texto(v.destino), flujo_actual: caudal, capacidad_maxima: capacidad, saturada: v.saturada };
}

export function idArista(origen: string, destino: string): string {
  return JSON.stringify([origen, destino].sort());
}

function aristasUnicas(aristas: { origen: string; destino: string }[]): void {
  const ids = aristas.map(a => idArista(a.origen, a.destino));
  if (new Set(ids).size !== ids.length || aristas.some(a => a.origen === a.destino)) throw new Error('Conexiones duplicadas o inválidas.');
}

/** Valida lo necesario para dibujar y presentar resultados sin valores inventados. */
export function validarSimulacion(valor: unknown): SimulacionResponse {
  const v = objeto(valor);
  const nodos = lista(v.nodos, nodo);
  if (new Set(nodos.map(n => n.id)).size !== nodos.length) throw new Error('Nodos duplicados.');
  const mst = lista(v.tendidos_mst, tendido);
  const flujos = lista(v.flujos, flujo);
  aristasUnicas(mst);
  aristasUnicas(flujos);
  const ids = new Set([...nodos.map(n => n.id), 'PLANTA']);
  for (const a of mst) {
    if (!ids.has(a.origen) || !ids.has(a.destino)) throw new Error('Una conexión referencia un nodo inexistente.');
  }
  for (const f of flujos) {
    const a = mst.find(a => idArista(a.origen, a.destino) === idArista(f.origen, f.destino));
    if (!a || Math.abs(a.capacidad_maxima - f.capacidad_maxima) > 1e-6) throw new Error('El flujo no coincide con los tendidos recibidos.');
  }
  const respuesta: SimulacionResponse = { nodos, tendidos_mst: mst, flujos, metricas_ml: null };
  if (v.metricas_ml != null) {
    const m = objeto(v.metricas_ml);
    const r2 = numero(m.r2, -Infinity);
    if (r2 > 1) throw new Error('Métrica R² inválida.');
    respuesta.metricas_ml = { mae: numero(m.mae), rmse: numero(m.rmse), r2 };
  }
  if (v.tendidos_candidatos !== undefined) {
    const candidatos = lista(v.tendidos_candidatos, tendido);
    aristasUnicas(candidatos);
    for (const a of candidatos) {
      if (!ids.has(a.origen) || !ids.has(a.destino)) throw new Error('Un tendido candidato referencia un nodo inexistente.');
    }
    for (const a of mst) {
      if (!candidatos.some(c => idArista(c.origen, c.destino) === idArista(a.origen, a.destino))) throw new Error('Falta un tendido seleccionado entre los candidatos.');
    }
    respuesta.tendidos_candidatos = candidatos;
  }
  return respuesta;
}
