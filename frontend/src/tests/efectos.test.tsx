import { act, fireEvent, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import App from '../App';
import LatticeLoader from '../components/effects/LatticeLoader';
import HoloCard from '../components/effects/HoloCard';
import muestra from './fixtures/simulacion.json';

function diferida<T>() {
  let resolve!: (valor: T) => void;
  let reject!: (motivo: Error) => void;
  const promise = new Promise<T>((resolver, rechazar) => { resolve = resolver; reject = rechazar; });
  return { promise, resolve, reject };
}
const respuesta = () => new Response(JSON.stringify(muestra), { status: 200 });

describe('Efectos conectados al uso real', () => {
  it('reinicia el contador al cambiar de escenario durante una carga y lo retira ante error o éxito', async () => {
    vi.useFakeTimers();
    const primera = diferida<Response>();
    const segunda = diferida<Response>();
    const fetchMock = vi.fn().mockImplementationOnce(() => primera.promise).mockImplementationOnce(() => segunda.promise).mockResolvedValueOnce(respuesta());
    vi.stubGlobal('fetch', fetchMock);
    render(<App />);
    const estado = screen.getByRole('status');
    expect(estado).toHaveTextContent('Calculando escenario…');
    act(() => { vi.advanceTimersByTime(2200); });
    expect(within(estado).getByText('2.2s')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Escenario +30 %' }));
    expect(screen.getByRole('status')).toHaveTextContent('0.0s');
    await act(async () => { primera.resolve(respuesta()); });
    expect(screen.getByText('Sin resultados disponibles')).toBeInTheDocument();
    expect(screen.getByRole('status')).toBeInTheDocument();

    await act(async () => { segunda.reject(new TypeError('Sin conexión')); });
    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: /Volver a intentar/ })); });
    expect(screen.getByText('Resultado mostrado: +30 %')).toBeInTheDocument();
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
    expect(screen.getByRole('table')).toBeInTheDocument();
  });

  it('no anuncia cada décima de segundo ni deja contadores activos al desmontarse', () => {
    vi.useFakeTimers();
    const { unmount } = render(<LatticeLoader label="Calculando escenario…" />);
    const status = screen.getByRole('status');
    expect(within(status).getByText('Calculando escenario…', { selector: '.lattice-loader__sr' })).toBeInTheDocument();
    act(() => { vi.advanceTimersByTime(1500); });
    expect(within(status).getByText('1.5s')).toHaveAttribute('aria-hidden', 'true');
    expect(status.querySelector('.lattice-loader__sr')).toHaveTextContent(/^Calculando escenario…$/);
    unmount();
    expect(vi.getTimerCount()).toBe(0);
  });

  it('mantiene la imagen accesible si el navegador no ofrece WebGL', () => {
    const contexto = vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(null);
    try {
      render(<HoloCard image="/pikachu.webp" alt="Carta holográfica de Pikachu" />);
      const carta = screen.getByRole('img', { name: 'Carta holográfica de Pikachu' });
      expect(carta.querySelector('img')).toHaveAttribute('src', '/pikachu.webp');
      expect(carta).not.toHaveAttribute('data-ready');
    } finally { contexto.mockRestore(); }
  });

  it('abre la pestaña de Pikachu y vuelve a la red sin pedir otra simulación', async () => {
    const contexto = vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(null);
    try {
      const fetchMock = vi.fn().mockResolvedValue(respuesta());
      vi.stubGlobal('fetch', fetchMock);
      const usuario = userEvent.setup();
      render(<App />);
      await screen.findByText('Resultado mostrado: Base');
      await usuario.click(screen.getByRole('button', { name: 'Efectos' }));
      await screen.findByRole('heading', { name: 'Tarjeta holográfica' });
      expect(screen.getByRole('img', { name: 'Carta holográfica de Pikachu' })).toBeInTheDocument();
      expect(screen.queryByRole('table')).not.toBeInTheDocument();
      await usuario.click(screen.getByRole('button', { name: 'Pausar movimiento' }));
      expect(screen.getByRole('button', { name: 'Activar movimiento' })).toHaveAttribute('aria-pressed', 'true');
      await usuario.click(screen.getByRole('button', { name: 'Capacidad' }));
      expect(screen.getByRole('table')).toBeInTheDocument();
      expect(screen.getByText('Resultado mostrado: Base')).toBeInTheDocument();
      expect(fetchMock).toHaveBeenCalledTimes(1);
    } finally { contexto.mockRestore(); }
  });
});
