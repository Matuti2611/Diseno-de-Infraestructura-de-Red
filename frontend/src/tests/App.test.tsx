import { act, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import App from '../App';
import muestra from './fixtures/simulacion.json';

const respuesta = (datos: unknown = muestra) => new Response(JSON.stringify(datos), { status: 200 });
function diferida<T>() {
  let resolve!: (valor: T) => void;
  const promise = new Promise<T>(resolver => { resolve = resolver; });
  return { promise, resolve };
}

describe('Recorridos de la página', () => {
  it('permite explorar los 26 candidatos, buscar una conexión y elegir un barrio por teclado', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respuesta()));
    const usuario = userEvent.setup();
    render(<App />);
    await screen.findByText('Resultado mostrado: Base');
    expect(within(screen.getByRole('table')).getAllByRole('row')).toHaveLength(27);
    await usuario.type(screen.getByRole('textbox', { name: 'Buscar conexión por nodo' }), 'NO-EXISTE');
    expect(screen.getByText(/No hay conexiones que coincidan/)).toBeInTheDocument();
    await usuario.click(screen.getByRole('button', { name: 'Limpiar búsqueda' }));
    expect(within(screen.getByRole('table')).getAllByRole('row')).toHaveLength(27);
    screen.getByRole('button', { name: 'Inspeccionar Barrio 01' }).focus();
    await usuario.keyboard('{Enter}');
    const detalle = screen.getByRole('complementary', { name: 'Detalle de la selección' });
    expect(within(detalle).getByRole('heading', { name: 'Barrio 01' })).toBeInTheDocument();
    expect(within(detalle).getByText('854 hab.')).toBeInTheDocument();
  });

  it('muestra los caudales omitidos como no informados y diferencia un tramo al 95 % del saturado', async () => {
    const datos = structuredClone(muestra);
    datos.flujos[0].flujo_actual = datos.flujos[0].capacidad_maxima * 0.95;
    datos.flujos[0].saturada = true; // La API actual marca también los cercanos como saturados.
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respuesta(datos)));
    const usuario = userEvent.setup();
    render(<App />);
    await screen.findByText('Resultado mostrado: Base');
    await usuario.click(screen.getByRole('button', { name: 'Capacidad' }));
    const filaSinFlujo = screen.getByRole('button', { name: 'Ver detalle del tramo PLANTA a Z01' }).closest('tr')!;
    expect(within(filaSinFlujo).getByText('No informado')).toBeInTheDocument();
    const f = datos.flujos[0];
    const filaCritica = screen.getByRole('button', { name: `Ver detalle del tramo ${f.origen} a ${f.destino}` }).closest('tr')!;
    expect(within(filaCritica).getByText('Cerca del límite')).toBeInTheDocument();
    expect(within(filaCritica).queryByText('Saturado', { exact: true })).not.toBeInTheDocument();
    expect(screen.getByText(/abastecimiento total y el déficit todavía no están informados/)).toBeInTheDocument();
  });

  it('ignora respuestas antiguas aunque terminen después del último escenario solicitado', async () => {
    const anterior = diferida<Response>();
    const reciente = diferida<Response>();
    const fetchMock = vi.fn().mockResolvedValueOnce(respuesta()).mockImplementationOnce(() => anterior.promise).mockImplementationOnce(() => reciente.promise);
    vi.stubGlobal('fetch', fetchMock);
    const usuario = userEvent.setup();
    render(<App />);
    await screen.findByText('Resultado mostrado: Base');
    await usuario.click(screen.getByRole('button', { name: 'Escenario +10 %' }));
    await usuario.click(screen.getByRole('button', { name: 'Escenario +30 %' }));
    const nueva = structuredClone(muestra);
    nueva.nodos[0].demanda_diaria_proyectada = 999;
    await act(async () => { reciente.resolve(respuesta(nueva)); });
    await screen.findByText('Resultado mostrado: +30 %');
    await usuario.click(screen.getByRole('button', { name: 'Inspeccionar Barrio 01' }));
    const vieja = structuredClone(muestra);
    vieja.nodos[0].demanda_diaria_proyectada = 500;
    await act(async () => { anterior.resolve(respuesta(vieja)); });
    const detalle = screen.getByRole('complementary', { name: 'Detalle de la selección' });
    expect(within(detalle).getByText('999 m³/día')).toBeInTheDocument();
    expect(within(detalle).queryByText('500 m³/día')).not.toBeInTheDocument();
    expect(screen.getByText('Resultado mostrado: +30 %')).toBeInTheDocument();
  });

  it('conserva el escenario anterior ante un error y reintenta el escenario seleccionado', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(respuesta()).mockRejectedValueOnce(new TypeError('Network error')).mockResolvedValueOnce(respuesta());
    vi.stubGlobal('fetch', fetchMock);
    const usuario = userEvent.setup();
    render(<App />);
    await screen.findByText('Resultado mostrado: Base');
    await usuario.click(screen.getByRole('button', { name: 'Escenario +30 %' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Se conservan los resultados de Base');
    expect(screen.getByText('Resultado mostrado: Base')).toBeInTheDocument();
    await usuario.click(screen.getByRole('button', { name: /Volver a intentar/ }));
    await screen.findByText('Resultado mostrado: +30 %');
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    const opciones = fetchMock.mock.calls[2][1] as RequestInit;
    expect(JSON.parse(opciones.body as string)).toEqual({ escenario_crecimiento: 1.3 });
  });

  it('presenta un error inicial sin inventar una red y permite recuperarse', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValueOnce(new TypeError('Offline')).mockResolvedValueOnce(respuesta()));
    const usuario = userEvent.setup();
    render(<App />);
    await screen.findByRole('alert');
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'La red todavía no está disponible' })).toBeInTheDocument();
    await usuario.click(screen.getByRole('button', { name: /Volver a intentar/ }));
    await screen.findByRole('table');
  });

  it('presenta una respuesta vacía sin incorporar barrios del CSV por su cuenta', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respuesta({ nodos: [], tendidos_mst: [], flujos: [], metricas_ml: null })));
    render(<App />);
    await waitFor(() => expect(screen.getByRole('heading', { name: 'No hay zonas para mostrar' })).toBeInTheDocument());
    expect(screen.queryByRole('button', { name: 'Inspeccionar Planta de agua' })).not.toBeInTheDocument();
  });
});
