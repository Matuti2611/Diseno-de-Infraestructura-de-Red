import { useState } from 'react';
import type { RedVisual, Seleccion, Vista } from '../types/red';
import { MapaRed } from './MapaRed';
import { DetalleSeleccion } from './DetalleSeleccion';
import { Leyenda } from './Leyenda';

export interface PropsPanelRed { red: RedVisual; seleccion: Seleccion; onSeleccionar: (s: Seleccion) => void }

export function PanelRed({ red, seleccion, onSeleccionar, vista }: PropsPanelRed & { vista: Vista }) {
  const [mostrarCandidatos, setMostrarCandidatos] = useState(vista === 'tendidos');
  const candidatosDisponibles = red.fuenteGeometria !== 'solo-mst';
  return <section className="panel-red" aria-label={vista === 'tendidos' ? 'Diseño de los tendidos' : 'Capacidad de la red'}>
    <div className="panel-cabecera"><div><h2>{vista === 'tendidos' ? 'Tendidos de la red' : 'Flujo y capacidad'}</h2><p>{vista === 'tendidos' ? 'Conexiones posibles y diseño seleccionado por costo.' : 'Inspeccioná los tramos próximos a su capacidad máxima.'}</p></div>
      <label className="control-checkbox"><input type="checkbox" checked={mostrarCandidatos && candidatosDisponibles} disabled={!candidatosDisponibles} onChange={e => setMostrarCandidatos(e.target.checked)} />Mostrar candidatos</label>
    </div>
    <div className="panel-red-cuerpo"><div className="mapa-area"><div className="mapa-etiquetas"><span><i />{red.nodos.length} nodos</span><span>{red.aristas.length} tendidos {candidatosDisponibles ? 'posibles' : 'recibidos'}</span></div><div className="mapa-contenedor" tabIndex={0} role="region" aria-label="Gráfico de la red desplazable"><MapaRed red={red} vista={vista} mostrarCandidatos={mostrarCandidatos && candidatosDisponibles} seleccion={seleccion} onSeleccionar={onSeleccionar} /></div><p className="mapa-ayuda">Desplazá el gráfico hacia los lados para explorar la red. También podés consultar todos los tramos en la tabla.</p></div><DetalleSeleccion red={red} seleccion={seleccion} /></div>
    <div className="panel-red-pie"><Leyenda vista={vista} mostrarCandidatos={mostrarCandidatos && candidatosDisponibles} /><span>Seleccioná un elemento para inspeccionarlo</span></div>
    <p className="nota-geometria">Los escenarios evalúan otra demanda sobre la misma red. Las ubicaciones y los costos de los tendidos permanecen fijos.</p>
    {red.fuenteGeometria === 'solo-mst' && <p className="nota-geometria">Las conexiones candidatas de esta red todavía no están disponibles. Se muestran los tendidos recibidos de la simulación.</p>}
    {red.ubicacionesFaltantes.length > 0 && <p className="nota-geometria">Faltan coordenadas de {red.ubicacionesFaltantes.join(', ')}. Sus conexiones se conservan en la tabla, pero no se pueden ubicar en el gráfico.</p>}
  </section>;
}
