import { describe, expect, it, vi } from 'vitest';
import { API_URL, solicitarSimulacion, TIEMPO_ESPERA_MS } from '../api/cliente';
import muestra from './fixtures/simulacion.json';

describe('Comunicación con el backend', () => {
  it('envía el multiplicador elegido como JSON al endpoint acordado', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(muestra), { status: 200 }));
    vi.stubGlobal('fetch', fetchMock);
    await solicitarSimulacion(1.3);
    expect(fetchMock).toHaveBeenCalledWith(`${API_URL}/api/simular-red`, expect.objectContaining({
      method: 'POST', body: '{"escenario_crecimiento":1.3}', headers: { 'Content-Type': 'application/json' },
    }));
  });

  it('informa un HTTP 500 en vez de sustituirlo por resultados de ejemplo', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('Internal Server Error', { status: 500 })));
    await expect(solicitarSimulacion(1)).rejects.toThrow('500');
  });

  it('rechaza un JSON incompatible aunque el servidor responda 200', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ nodos: 'incorrecto' }), { status: 200 })));
    await expect(solicitarSimulacion(1)).rejects.toThrow('incompletos o incompatibles');
  });

  it('termina la espera de un servicio que no responde y explica cómo reintentar', async () => {
    vi.useFakeTimers();
    vi.stubGlobal('fetch', vi.fn((_url: string, opciones: RequestInit) => new Promise((_resolve, reject) => {
      opciones.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
    })));
    const pendiente = expect(solicitarSimulacion(1)).rejects.toThrow('tardó demasiado');
    await vi.advanceTimersByTimeAsync(TIEMPO_ESPERA_MS);
    await pendiente;
  });
});
