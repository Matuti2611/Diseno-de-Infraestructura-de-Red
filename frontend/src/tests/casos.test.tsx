import { act, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import App from '../App';
import { solicitarSimulacion } from '../api/cliente';
import { validarSimulacion } from '../api/validar';
import { ComparacionEscenarios } from '../components/ComparacionEscenarios';
import type { CasoRed, Escenario } from '../types/red';
import { casoCapacidad } from './fixtures/capacidad';

/** Datos resueltos a mano para probar presentación, no predicciones del modelo. */
function caso(casoRed: CasoRed = 'progresivo', escenario: Escenario = 1) {
  const datos = casoCapacidad(escenario === 1.3);
  datos.caso_red = casoRed;
  datos.escenario_crecimiento = escenario;
  datos.nodos = datos.nodos.map(n => {
    if (n.id === 'PLANTA') return n;
    const suministro = n.id === 'A' ? n.demanda_diaria_proyectada : escenario === 1.3 ? 35 : 30;
    return { ...n, caudal_abastecido_m3_dia: suministro, deficit_m3_dia: n.demanda_diaria_proyectada - suministro };
  });
  return datos;
}
const respuesta = (datos: unknown) => new Response(JSON.stringify(datos), { status: 200 });
function diferida<T>() {
  let resolve!: (valor: T) => void;
  const promise = new Promise<T>(resolver => { resolve = resolver; });
  return { promise, resolve };
}

describe('Casos y abastecimiento por barrio', () => {
  it('rechaza suministro excesivo, balance parcial y totales que contradicen los barrios', () => {
    const excesivo = caso();
    excesivo.nodos[1].caudal_abastecido_m3_dia = 50; // Tránsito PLANTA–A, no consumo local de A=20.
    expect(() => validarSimulacion(excesivo)).toThrow('barrio');
    const parcial = caso();
    delete parcial.nodos[1].deficit_m3_dia;
    expect(() => validarSimulacion(parcial)).toThrow();
    const total = caso();
    total.nodos[1].caudal_abastecido_m3_dia = 19;
    total.nodos[1].deficit_m3_dia = 1;
    expect(() => validarSimulacion(total)).toThrow('total');
    expect(validarSimulacion(caso()).nodos[1].caudal_abastecido_m3_dia).toBe(20);
  });

  it('no acepta como progresivo un servidor que ignora el caso, ni otro crecimiento', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(respuesta(casoCapacidad())).mockResolvedValueOnce(respuesta(caso('progresivo', 1.3)));
    vi.stubGlobal('fetch', fetchMock);
    await expect(solicitarSimulacion(1, undefined, 'progresivo')).rejects.toThrow('no confirmó el caso');
    expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({ escenario_crecimiento: 1, caso_red: 'progresivo' });
    await expect(solicitarSimulacion(1, undefined, 'progresivo')).rejects.toThrow('otro escenario');
  });

  it('muestra el consumo del barrio y compara tres balances reales recibidos sin cambiar el escenario principal', async () => {
    const fetchMock = vi.fn().mockImplementation((_url: string, opciones: RequestInit) => {
      const entrada = JSON.parse(opciones.body as string);
      return Promise.resolve(respuesta(caso(entrada.caso_red ?? 'original', entrada.escenario_crecimiento)));
    });
    vi.stubGlobal('fetch', fetchMock);
    const usuario = userEvent.setup();
    render(<App />);
    await screen.findByText('Caso mostrado: Original');
    await usuario.selectOptions(screen.getByRole('combobox', { name: 'Caso de capacidades' }), 'progresivo');
    await screen.findByText('Caso mostrado: Progresivo');
    await usuario.click(screen.getByRole('button', { name: 'Capacidad' }));
    const tabla = screen.getByRole('table', { name: 'Abastecimiento por barrio' });
    expect(within(tabla).getAllByRole('row')).toHaveLength(3);
    await usuario.click(within(tabla).getByRole('button', { name: 'Ver abastecimiento de A' }));
    const detalle = screen.getByRole('complementary', { name: 'Detalle de la selección' });
    expect(within(detalle).getByText('Suministro al barrio').nextElementSibling).toHaveTextContent('20 m³/día');
    await usuario.click(screen.getByRole('button', { name: 'Comparar escenarios' }));
    const comparacion = await screen.findByRole('table', { name: 'Comparación de escenarios' });
    const ultima = within(comparacion).getAllByRole('row')[3];
    expect(ultima).toHaveTextContent('+30 %');
    expect(within(ultima).getAllByRole('cell').map(n => n.textContent)).toEqual(['65', '61', '4', '93,8 % · Con déficit']);
    expect(screen.getByText('Resultado mostrado: Base')).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(5);
    for (const llamada of fetchMock.mock.calls.slice(2)) expect(JSON.parse(llamada[1].body).caso_red).toBe('progresivo');
  });

  it('ignora una respuesta de otro caso que termina después de volver al original', async () => {
    const tardia = diferida<Response>();
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(respuesta(caso('original'))).mockImplementationOnce(() => tardia.promise).mockResolvedValueOnce(respuesta(caso('original'))));
    const usuario = userEvent.setup();
    render(<App />);
    await screen.findByText('Caso mostrado: Original');
    await usuario.selectOptions(screen.getByRole('combobox'), 'progresivo');
    await usuario.selectOptions(screen.getByRole('combobox'), 'original');
    await act(async () => { tardia.resolve(respuesta(caso('progresivo', 1.3))); });
    expect(screen.getByText('Caso mostrado: Original')).toBeInTheDocument();
    expect(screen.queryByText('Caso mostrado: Progresivo')).not.toBeInTheDocument();
    expect(screen.getByText('Resultado mostrado: Base')).toBeInTheDocument();
  });

  it('cancela la comparación al cambiar de caso y no mezcla respuestas tardías', async () => {
    const pendientes = [diferida<Response>(), diferida<Response>(), diferida<Response>()];
    const fetchMock = vi.fn().mockImplementationOnce(() => pendientes[0].promise).mockImplementationOnce(() => pendientes[1].promise).mockImplementationOnce(() => pendientes[2].promise).mockImplementation((_url: string, opciones: RequestInit) => {
      const entrada = JSON.parse(opciones.body as string);
      return Promise.resolve(respuesta(caso('progresivo', entrada.escenario_crecimiento)));
    });
    vi.stubGlobal('fetch', fetchMock);
    const usuario = userEvent.setup();
    const { rerender } = render(<ComparacionEscenarios key="original" caso="original" />);
    await usuario.click(screen.getByRole('button', { name: 'Comparar escenarios' }));
    rerender(<ComparacionEscenarios key="progresivo" caso="progresivo" />);
    expect((fetchMock.mock.calls[0][1].signal as AbortSignal).aborted).toBe(true);
    await act(async () => { pendientes.forEach((p, i) => p.resolve(respuesta(caso('original', ([1, 1.1, 1.3] as const)[i])))); });
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
    await usuario.click(screen.getByRole('button', { name: 'Comparar escenarios' }));
    await screen.findByRole('table', { name: 'Comparación de escenarios' });
    expect(screen.getByRole('heading', { name: 'Comparar escenarios · Progresivo' })).toBeInTheDocument();
  });

  it('no presenta una comparación parcial ante un escenario fallido y permite reintentar', async () => {
    const fetchMock = vi.fn().mockImplementation((_url: string, opciones: RequestInit) => {
      const entrada = JSON.parse(opciones.body as string);
      return Promise.resolve(entrada.escenario_crecimiento === 1.1 ? new Response('', { status: 503 }) : respuesta(caso('progresivo', entrada.escenario_crecimiento)));
    });
    vi.stubGlobal('fetch', fetchMock);
    const usuario = userEvent.setup();
    render(<ComparacionEscenarios caso="progresivo" />);
    await usuario.click(screen.getByRole('button', { name: 'Comparar escenarios' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('No se completó la comparación');
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Reintentar comparación' })).toBeEnabled();
  });
});
