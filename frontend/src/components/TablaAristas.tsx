import { useState } from 'react';
import { etiquetasEstado, numero } from '../lib/red';
import type { RedVisual, Seleccion, Vista } from '../types/red';
import { Icono } from './Icono';

export function TablaAristas({ red, vista, seleccion, onSeleccionar }: { red: RedVisual; vista: Vista; seleccion: Seleccion; onSeleccionar: (s: Seleccion) => void }) {
  const [busqueda, setBusqueda] = useState('');
  const base = red.aristas.filter(a => vista === 'tendidos' || a.seleccionada);
  const visibles = base.filter(a => `${a.origen} ${a.destino}`.toLowerCase().includes(busqueda.trim().toLowerCase()));
  return <section className="panel-tabla" aria-labelledby="titulo-tabla">
    <div className="panel-cabecera"><div><h2 id="titulo-tabla">Detalle de conexiones <span className="contador">{base.length}</span></h2><p>{vista === 'tendidos' ? 'Compará los tendidos posibles y los seleccionados.' : 'Valores informados para los tendidos seleccionados.'}</p></div>
      <label className="buscador"><Icono nombre="buscar" /><span className="sr-only">Buscar conexión por nodo</span><input value={busqueda} onChange={e => setBusqueda(e.target.value)} placeholder="Buscar por nodo…" /></label>
    </div>
    <div className="tabla-scroll" tabIndex={0} role="region" aria-label="Tabla de conexiones desplazable">
      <table><caption className="sr-only">{vista === 'tendidos' ? 'Conexiones candidatas y red elegida' : 'Capacidad y flujos informados'}</caption>
        <thead><tr><th scope="col">Conexión</th><th scope="col">{vista === 'tendidos' ? 'Costo · u. c.' : 'Flujo · m³/día'}</th><th scope="col">Capacidad · m³/día</th>{vista === 'capacidad' && <th scope="col">Utilización</th>}<th scope="col">Estado</th></tr></thead>
        <tbody>{visibles.map(a => <tr key={a.id} className={seleccion?.tipo === 'arista' && seleccion.id === a.id ? 'fila-elegida' : ''}>
          <th scope="row"><button className="boton-tramo" onClick={() => onSeleccionar({ tipo: 'arista', id: a.id })} aria-label={`Ver detalle del tramo ${a.origen} a ${a.destino}`}><span>{a.origen}</span><span className="separador-tramo">—</span><span>{a.destino}</span><Icono nombre="flecha" /></button></th>
          <td>{vista === 'tendidos' ? numero(a.costo, 2) : a.flujo === null ? <span className="sin-dato">No informado</span> : numero(a.flujo)}</td>
          <td>{numero(a.capacidad_maxima)}</td>
          {vista === 'capacidad' && <td>{a.utilizacion === null ? <span className="sin-dato">—</span> : `${numero(a.utilizacion)} %`}</td>}
          <td>{vista === 'tendidos' ? <span className={`estado-pill ${a.seleccionada ? 'estado-seleccionado' : 'estado-candidato'}`}>{a.seleccionada ? 'Seleccionado' : 'Alternativa'}</span> : <span className={`estado-pill estado-${a.estado}`}>{etiquetasEstado[a.estado]}</span>}</td>
        </tr>)}</tbody>
      </table>
    </div>
    {visibles.length === 0 && <div className="tabla-vacia"><p>No hay conexiones que coincidan con «{busqueda}».</p><button className="boton-secundario" onClick={() => setBusqueda('')}>Limpiar búsqueda</button></div>}
    <div className="tabla-pie"><span>{visibles.length} de {base.length} conexiones</span><span>{vista === 'tendidos' ? 'Costos en unidades convencionales' : 'Un flujo no informado no se interpreta como cero'}</span></div>
  </section>;
}
