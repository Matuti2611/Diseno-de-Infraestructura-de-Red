import type { CasoRed, Escenario, SimulacionResponse } from '../types/red';
import { validarSimulacion } from './validar';

export const API_URL = (import.meta.env.VITE_API_URL || 'https://infraestructura-red-api.onrender.com').replace(/\/+$/, '');
export const TIEMPO_ESPERA_MS = 90_000;

export async function solicitarSimulacion(escenario: Escenario, signal?: AbortSignal, caso: CasoRed = 'original'): Promise<SimulacionResponse> {
  const controlador = new AbortController();
  let agotado = false;
  const cancelar = () => controlador.abort();
  if (signal?.aborted) controlador.abort();
  signal?.addEventListener('abort', cancelar, { once: true });
  const temporizador = setTimeout(() => { agotado = true; controlador.abort(); }, TIEMPO_ESPERA_MS);
  try {
    const respuesta = await fetch(`${API_URL}/api/simular-red`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ escenario_crecimiento: escenario, ...(caso !== 'original' ? { caso_red: caso } : {}) }), signal: controlador.signal,
    });
    if (!respuesta.ok) throw new Error(`La API respondió con un error (${respuesta.status}). Podés volver a intentarlo.`);
    let json: unknown;
    try { json = await respuesta.json(); }
    catch (causa) { throw new Error('La API devolvió una respuesta que no se puede leer.', { cause: causa }); }
    let datos: SimulacionResponse;
    try { datos = validarSimulacion(json); }
    catch (causa) { throw new Error('La simulación recibida tiene datos incompletos o incompatibles. No se pueden mostrar de forma segura.', { cause: causa }); }
    if ((caso === 'progresivo' && (datos.caso_red !== caso || datos.escenario_crecimiento === undefined)) || (datos.caso_red !== undefined && datos.caso_red !== caso)) {
      throw new Error('La API no confirmó el caso elegido. Puede requerir actualizar el backend; no se mostrarán resultados de otro caso.');
    }
    if (datos.escenario_crecimiento !== undefined && Math.abs(datos.escenario_crecimiento - escenario) > 1e-9) throw new Error('La API respondió con otro escenario de crecimiento.');
    return datos;
  } catch (error) {
    if (agotado) throw new Error('La API tardó demasiado en responder. El servicio puede estar iniciándose; intentá nuevamente.', { cause: error });
    if (signal?.aborted) throw error;
    if (error instanceof TypeError) throw new Error('No se pudo conectar con la API. Revisá la conexión o intentá nuevamente en unos segundos.', { cause: error });
    throw error;
  } finally {
    clearTimeout(temporizador);
    signal?.removeEventListener('abort', cancelar);
  }
}
