import { nombreNodo, numero } from '../lib/red';
import type { RedVisual, Seleccion } from '../types/red';

export function TablaBarrios({ red, onSeleccionar }: { red: RedVisual; onSeleccionar: (valor: Seleccion) => void }) {
  const barrios = red.nodos.filter(n => n.id !== 'PLANTA');
  return <section className="panel-tabla" aria-labelledby="titulo-barrios"><div className="panel-cabecera"><div><h2 id="titulo-barrios">Abastecimiento por barrio</h2><p>Consumo efectivo de cada zona; el agua que continúa hacia otros barrios no se cuenta como consumo local.</p></div></div>
    {barrios.every(n => n.suministro == null) ? <p className="barrios-aviso">El servicio todavía no informa el abastecimiento por barrio. No se interpreta como cero.</p> : <>
      <div className="tabla-scroll"><table aria-label="Abastecimiento por barrio"><thead><tr><th scope="col">Barrio</th><th scope="col">Demanda · m³/día</th><th scope="col">Suministro · m³/día</th><th scope="col">Déficit · m³/día</th><th scope="col">Diagnóstico</th></tr></thead><tbody>{barrios.map(n => <tr key={n.id}><th scope="row"><button type="button" className="boton-barrio" aria-label={`Ver abastecimiento de ${nombreNodo(n.id)}`} onClick={() => onSeleccionar({ tipo: 'nodo', id: n.id })}>{nombreNodo(n.id)}</button></th><td>{numero(n.demanda!, 2)}</td><td>{n.suministro == null ? 'No informado' : numero(n.suministro, 2)}</td><td>{n.deficit == null ? 'No informado' : numero(n.deficit, 2)}</td><td>{n.deficit == null ? 'Sin dato' : n.deficit > 0 ? 'Con déficit' : 'Cubierto'}</td></tr>)}</tbody></table></div>
      <p className="barrios-aviso">El flujo máximo prioriza el suministro total. El reparto por barrio puede variar entre soluciones máximas y no garantiza equidad.</p>
    </>}
  </section>;
}
