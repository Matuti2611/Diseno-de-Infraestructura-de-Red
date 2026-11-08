interface Props { nombre: 'agua' | 'red' | 'flujo' | 'flecha' | 'actualizar' | 'alerta' | 'buscar' | 'info' | 'externo' | 'brillo'; className?: string }

const trazos: Record<Props['nombre'], string> = {
  brillo: 'm12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5L12 3Z',
  agua: 'M12 3C9 8 5 11 5 15a7 7 0 0 0 14 0c0-4-4-7-7-12ZM9 15a3 3 0 0 0 3 3',
  red: 'M8 5h8M5 8v8m3 3h8m3-11v8M8 8l8 8M8 16l8-8M3 3h5v5H3Zm13 0h5v5h-5ZM3 16h5v5H3Zm13 0h5v5h-5Z',
  flujo: 'M3 7h15m-4-4 4 4-4 4M21 17H6m4-4-4 4 4 4',
  flecha: 'M5 12h14m-6-6 6 6-6 6',
  actualizar: 'M20 7v5h-5M4 17v-5h5M6 7a7 7 0 0 1 12-1l2 3M4 15l2 3a7 7 0 0 0 12-1',
  alerta: 'm12 3 10 18H2L12 3Zm0 6v5m0 3v1',
  buscar: 'M15 15l6 6M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0Z',
  info: 'M12 10v7m0-11v1M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0Z',
  externo: 'M14 3h7v7m0-7L10 14M10 3H3v18h18v-7',
};

export function Icono({ nombre, className = '' }: Props) {
  return <svg className={`icono ${className}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={trazos[nombre]} /></svg>;
}
