import { describe, expect, it } from 'vitest';
import muestra from './fixtures/simulacion.json';
import { validarSimulacion } from '../api/validar';
import { construirRed, estadoTramo } from '../lib/red';

describe('Límite de datos entre la API y la página', () => {
  it.each([
    ['demanda negativa', () => ({ ...muestra, nodos: [{ ...muestra.nodos[0], demanda_diaria_proyectada: -1 }] })],
    ['demanda no finita', () => ({ ...muestra, nodos: [{ ...muestra.nodos[0], demanda_diaria_proyectada: NaN }] })],
    ['nodos duplicados', () => ({ ...muestra, nodos: [...muestra.nodos, muestra.nodos[0]] })],
    ['colección de nodos ausente', () => ({ ...muestra, nodos: undefined })],
    ['conexión a un nodo inexistente', () => ({ ...muestra, tendidos_mst: [{ ...muestra.tendidos_mst[0], destino: 'NO-EXISTE' }] })],
    ['flujo superior a la capacidad', () => ({ ...muestra, flujos: [{ ...muestra.flujos[0], flujo_actual: muestra.flujos[0].capacidad_maxima + 10 }] })],
    ['conexiones duplicadas', () => ({ ...muestra, tendidos_mst: [...muestra.tendidos_mst, muestra.tendidos_mst[0]] })],
  ])('rechaza %s antes de mostrar resultados', (_nombre, crear) => {
    expect(() => validarSimulacion(crear())).toThrow();
  });

  it('acepta R² negativo y no inventa métricas cuando no se reciben', () => {
    expect(validarSimulacion({ ...muestra, metricas_ml: { mae: 20, rmse: 30, r2: -0.5 } }).metricas_ml?.r2).toBe(-0.5);
    expect(validarSimulacion({ ...muestra, metricas_ml: null }).metricas_ml).toBeNull();
  });

  it('completa la geometría con los CSV coincidentes sin fabricar caudales', () => {
    const red = construirRed(validarSimulacion(muestra));
    expect(red.fuenteGeometria).toBe('csv');
    expect(red.nodos.find(n => n.id === 'PLANTA')).toMatchObject({ latitud: -32.95, longitud: -60.65, demanda: null });
    expect(red.aristas).toHaveLength(26);
    expect(red.aristas.filter(a => a.seleccionada)).toHaveLength(16);
    expect(red.aristas.find(a => a.origen === 'PLANTA' && a.destino === 'Z01')).toMatchObject({ flujo: null, utilizacion: null, estado: 'sin-dato' });
  });

  it('no mezcla candidatos locales con una red que cambió en la API', () => {
    const cambiada = structuredClone(muestra);
    cambiada.tendidos_mst[0].costo += 100;
    const red = construirRed(validarSimulacion(cambiada));
    expect(red.fuenteGeometria).toBe('solo-mst');
    expect(red.aristas).toHaveLength(16);
  });

  it('diferencia ausencia de caudal, cero real, cercanía y saturación completa', () => {
    expect(estadoTramo(null, 100)).toBe('sin-dato');
    expect(estadoTramo(0, 100)).toBe('informado');
    expect(estadoTramo(92, 100)).toBe('cercano');
    expect(estadoTramo(100, 100)).toBe('saturado');
    expect(estadoTramo(0, 0)).toBe('sin-capacidad');
  });

  it('avisa si una red diferente no incluye la ubicación de la planta, sin inventarla', () => {
    const cambiada = structuredClone(muestra);
    cambiada.nodos[0].latitud += 0.01;
    const red = construirRed(validarSimulacion(cambiada));
    expect(red.nodos.some(n => n.id === 'PLANTA')).toBe(false);
    expect(red.ubicacionesFaltantes).toEqual(['PLANTA']);
  });
});
