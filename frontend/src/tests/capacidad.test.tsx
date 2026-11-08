import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import App from '../App';
import { casoCapacidad } from './fixtures/capacidad';

const respuesta = (datos: unknown) => new Response(JSON.stringify(datos), { status: 200 });

describe('Lectura de caudales y abastecimiento', () => {
  it('muestra el caudal de todos los tramos, incluso los no críticos, y permite inspeccionarlos por teclado', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respuesta(casoCapacidad())));
    const usuario = userEvent.setup();
    render(<App />);
    await screen.findByText('Resultado mostrado: Base');
    await usuario.click(screen.getByRole('button', { name: 'Capacidad' }));
    const plantaA = screen.getByRole('button', { name: /^Inspeccionar conexión PLANTA a A/ });
    const ab = screen.getByRole('button', { name: /^Inspeccionar conexión A a B/ });
    expect(within(plantaA).getByText('50 m³/día')).toBeInTheDocument();
    expect(within(ab).getByText('30 m³/día')).toBeInTheDocument();
    ab.focus();
    await usuario.keyboard('{Enter}');
    const detalle = screen.getByRole('complementary', { name: 'Detalle de la selección' });
    expect(within(detalle).getByText('30 m³/día')).toBeInTheDocument();
    expect(within(detalle).getByText('35 m³/día')).toBeInTheDocument();
  });

  it('distingue flujo cero de dato ausente en las etiquetas y no deduce cobertura', async () => {
    const datos = casoCapacidad();
    delete datos.resumen_capacidad;
    datos.flujos = [{ ...datos.flujos[0], flujo_actual: 0 }];
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respuesta(datos)));
    const usuario = userEvent.setup();
    render(<App />);
    await screen.findByText('Resultado mostrado: Base');
    await usuario.click(screen.getByRole('button', { name: 'Capacidad' }));
    expect(within(screen.getByRole('button', { name: /^Inspeccionar conexión PLANTA a A/ })).getByText('0 m³/día')).toBeInTheDocument();
    expect(within(screen.getByRole('button', { name: /^Inspeccionar conexión A a B/ })).getByText('Sin dato')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Diagnóstico incompleto' })).toBeInTheDocument();
    expect(screen.queryByText('Caudal abastecido')).not.toBeInTheDocument();
  });

  it('presenta cobertura y déficit según cada respuesta del backend al cambiar de escenario', async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(respuesta(casoCapacidad())).mockResolvedValueOnce(respuesta(casoCapacidad(true)));
    vi.stubGlobal('fetch', fetchMock);
    const usuario = userEvent.setup();
    render(<App />);
    await screen.findByText('Resultado mostrado: Base');
    await usuario.click(screen.getByRole('button', { name: 'Capacidad' }));
    let balance = screen.getByRole('region', { name: 'La red cubre la demanda proyectada' });
    expect(within(balance).getAllByRole('definition').map(n => n.textContent)).toEqual(['50 m³/día', '50 m³/día', '0 m³/día']);
    await usuario.click(screen.getByRole('button', { name: 'Escenario +30 %' }));
    await screen.findByText('Resultado mostrado: +30 %');
    balance = screen.getByRole('region', { name: 'La red no cubre toda la demanda' });
    expect(within(balance).getAllByRole('definition').map(n => n.textContent)).toEqual(['65 m³/día', '61 m³/día', '4 m³/día']);
    const ab = screen.getByRole('button', { name: /^Inspeccionar conexión A a B/ });
    expect(within(ab).getByText('35 m³/día')).toBeInTheDocument();
    expect(within(ab).getByText('100 % de capacidad')).toBeInTheDocument();
    expect(JSON.parse(fetchMock.mock.calls[1][1].body)).toEqual({ escenario_crecimiento: 1.3 });
  });

  it('no declara abastecimiento suficiente solo porque se conocen todos los flujos', async () => {
    const datos = casoCapacidad();
    delete datos.resumen_capacidad;
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respuesta(datos)));
    const usuario = userEvent.setup();
    render(<App />);
    await screen.findByText('Resultado mostrado: Base');
    await usuario.click(screen.getByRole('button', { name: 'Capacidad' }));
    expect(screen.getByRole('heading', { name: 'Diagnóstico incompleto' })).toBeInTheDocument();
    expect(screen.getByText(/Todos los tendidos seleccionados tienen dato de flujo/)).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'La red cubre la demanda proyectada' })).not.toBeInTheDocument();
  });
});
