import { useId, type KeyboardEvent } from 'react';
import { nombreNodo, numero } from '../lib/red';
import type { RedVisual, Seleccion, Vista } from '../types/red';

interface Props { red: RedVisual; vista: Vista; mostrarCandidatos: boolean; seleccion: Seleccion; onSeleccionar: (seleccion: Seleccion) => void }

export function MapaRed({ red, vista, mostrarCandidatos, seleccion, onSeleccionar }: Props) {
  const id = useId();
  const latitudes = red.nodos.map(n => n.latitud);
  const longitudes = red.nodos.map(n => n.longitud);
  const minLat = Math.min(...latitudes), maxLat = Math.max(...latitudes);
  const minLon = Math.min(...longitudes), maxLon = Math.max(...longitudes);
  const puntos = new Map(red.nodos.map(n => [n.id, {
    x: 95 + (n.longitud - minLon) / (maxLon - minLon || 1) * 755,
    y: 65 + (maxLat - n.latitud) / (maxLat - minLat || 1) * 355,
  }]));
  const activar = (event: KeyboardEvent<SVGGElement>, siguiente: Seleccion) => {
    if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); onSeleccionar(siguiente); }
  };
  return <svg className="mapa-svg" viewBox="0 0 960 500" aria-labelledby={`${id}-titulo ${id}-descripcion`}>
    <title id={`${id}-titulo`}>Esquema de la red de agua</title>
    <desc id={`${id}-descripcion`}>Ubicación esquemática de la planta y los barrios. Seleccioná un nodo o una conexión para inspeccionarlo. Los mismos tendidos se pueden consultar en la tabla.</desc>
    <defs><pattern id={`${id}-grilla`} width="30" height="30" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#c6d4e1" opacity="0.65" /></pattern></defs>
    <rect width="960" height="500" fill={`url(#${id}-grilla)`} />
    {red.aristas.filter(a => mostrarCandidatos || a.seleccionada).map(a => {
      const origen = puntos.get(a.origen), destino = puntos.get(a.destino);
      if (!origen || !destino) return null;
      const elegida = seleccion?.tipo === 'arista' && seleccion.id === a.id;
      const estado = vista === 'capacidad' ? a.estado : a.seleccionada ? 'informado' : 'candidato';
      const siguiente: Seleccion = { tipo: 'arista', id: a.id };
      const critica = vista === 'capacidad' && ['cercano', 'saturado', 'sin-capacidad'].includes(a.estado);
      return <g key={a.id} className="tramo-interactivo" role="button" tabIndex={0} aria-label={`Inspeccionar conexión ${a.origen} a ${a.destino}`} aria-pressed={elegida} onClick={() => onSeleccionar(siguiente)} onKeyDown={e => activar(e, siguiente)}>
        {elegida && <line x1={origen.x} y1={origen.y} x2={destino.x} y2={destino.y} className="tramo-halo" />}
        <line x1={origen.x} y1={origen.y} x2={destino.x} y2={destino.y} className={`tramo tramo-${estado}`} />
        <line x1={origen.x} y1={origen.y} x2={destino.x} y2={destino.y} className="tramo-hit" />
        {critica && <g className="etiqueta-flujo" transform={`translate(${(origen.x + destino.x) / 2},${(origen.y + destino.y) / 2})`}><rect x="-25" y="-12" width="50" height="24" rx="7" /><text textAnchor="middle" dominantBaseline="central">{a.utilizacion !== null ? `${numero(a.utilizacion, 0)} %` : '0 m³'}</text></g>}
      </g>;
    })}
    {red.nodos.map(n => {
      const punto = puntos.get(n.id)!;
      const esPlanta = n.id === 'PLANTA';
      const elegida = seleccion?.tipo === 'nodo' && seleccion.id === n.id;
      const siguiente: Seleccion = { tipo: 'nodo', id: n.id };
      return <g key={n.id} role="button" tabIndex={0} className={`nodo ${esPlanta ? 'nodo-planta' : ''} ${elegida ? 'nodo-elegido' : ''}`} transform={`translate(${punto.x},${punto.y})`} aria-label={`Inspeccionar ${nombreNodo(n.id)}`} aria-pressed={elegida} onClick={() => onSeleccionar(siguiente)} onKeyDown={e => activar(e, siguiente)}>
        <circle className="nodo-foco" r="28" />
        <circle className="nodo-area" r="26" fill="transparent" />
        {esPlanta ? <><rect className="nodo-forma" x="-20" y="-20" width="40" height="40" rx="12" /><path className="gota" d="M0-12c-3 5-9 10-9 15a9 9 0 0 0 18 0c0-5-6-10-9-15Z" /></> : <><circle className="nodo-forma" r="15" /><circle className="nodo-centro" r="4" /></>}
        <text className="nodo-etiqueta" textAnchor="middle" y={esPlanta ? 39 : 34}>{esPlanta ? 'PLANTA' : n.id}</text>
      </g>;
    })}
    <text x="28" y="476" className="mapa-nota">ESQUEMA DEL CASO SINTÉTICO · SIN ESCALA DE OBRA</text>
  </svg>;
}
