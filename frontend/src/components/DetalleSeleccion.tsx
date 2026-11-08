import { etiquetasEstado, nombreNodo, numero } from '../lib/red';
import type { RedVisual, Seleccion } from '../types/red';
import { Icono } from './Icono';

export function DetalleSeleccion({ red, seleccion }: { red: RedVisual; seleccion: Seleccion }) {
  const nodo = seleccion?.tipo === 'nodo' ? red.nodos.find(n => n.id === seleccion.id) : undefined;
  const arista = seleccion?.tipo === 'arista' ? red.aristas.find(a => a.id === seleccion.id) : undefined;
  return <aside className="detalle" aria-label="Detalle de la selección">
    <span className="etiqueta-superior">EXPLORAR LA RED</span>
    <div className="detalle-icono"><Icono nombre={arista ? 'flujo' : 'agua'} /></div>
    <h3>{nodo ? nombreNodo(nodo.id) : arista ? `${arista.origen} — ${arista.destino}` : 'Cada conexión cuenta'}</h3>
    <p className="detalle-intro">{nodo ? nodo.id === 'PLANTA' ? 'Fuente de abastecimiento del caso de estudio.' : `Zona ${nodo.tipo_zona}.` : arista ? 'Detalle del tendido entre dos puntos de la red.' : 'Seleccioná un barrio o un tendido para conocer sus datos.'}</p>
    {nodo && <dl className="detalle-datos">
      <div><dt>Identificador</dt><dd>{nodo.id}</dd></div>
      {nodo.poblacion !== undefined && <div><dt>Población del caso</dt><dd>{numero(nodo.poblacion, 0)} hab.</dd></div>}
      <div><dt>Demanda proyectada</dt><dd>{nodo.demanda === null ? 'Fuente de agua' : `${numero(nodo.demanda)} m³/día`}</dd></div>
    </dl>}
    {arista && <><span className={`estado-pill estado-${arista.estado}`}>{etiquetasEstado[arista.estado]}</span><dl className="detalle-datos">
      <div><dt>Costo del tendido</dt><dd>{numero(arista.costo, 2)} u. c.</dd></div>
      <div><dt>Capacidad máxima</dt><dd>{numero(arista.capacidad_maxima)} m³/día</dd></div>
      <div><dt>Flujo informado</dt><dd>{arista.flujo === null ? 'No informado' : `${numero(arista.flujo)} m³/día`}</dd></div>
      <div><dt>Utilización</dt><dd>{arista.utilizacion === null ? 'No informada' : `${numero(arista.utilizacion)} %`}</dd></div>
    </dl></>}
    <div className="detalle-pie"><Icono nombre="info" /><p>Las ubicaciones y capacidades pertenecen a un caso de estudio sintético.</p></div>
  </aside>;
}
