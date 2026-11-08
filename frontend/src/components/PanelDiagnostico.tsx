import { numero } from '../lib/red';
import type { RedVisual } from '../types/red';
import { Icono } from './Icono';

export function PanelDiagnostico({ red }: { red: RedVisual | null }) {
  const seleccionadas = red?.aristas.filter(a => a.seleccionada).length;
  return <section className="indicadores" aria-label="Resumen del escenario mostrado">
    <article className="indicador">
      <div className="indicador-cabecera"><span>Costo del tendido</span><Icono nombre="red" /></div>
      <p className="indicador-valor">{red ? numero(red.costoTotal, 2) : '—'} <small>u. c.</small></p>
      <p>Suma de las conexiones seleccionadas</p>
    </article>
    <article className="indicador">
      <div className="indicador-cabecera"><span>Demanda proyectada</span><Icono nombre="agua" /></div>
      <p className="indicador-valor" data-testid="demanda-total">{red ? numero(red.demandaTotal) : '—'} <small>m³/día</small></p>
      <p>Consumo futuro de todos los barrios</p>
    </article>
    <article className="indicador">
      <div className="indicador-cabecera"><span>Conexiones del diseño</span><Icono nombre="flujo" /></div>
      <p className="indicador-valor">{seleccionadas ?? '—'} <small>tendidos</small></p>
      <p>{red ? `${red.cantidadBarrios} barrios en este escenario` : 'Red seleccionada por el backend'}</p>
    </article>
    <article className={`indicador ${red && red.tramosCriticos > 0 ? 'indicador-alerta' : ''}`}>
      <div className="indicador-cabecera"><span>Tramos críticos informados</span><Icono nombre="alerta" /></div>
      <p className="indicador-valor">{red ? red.tramosCriticos : '—'} <small>tramos</small></p>
      <p>Con una utilización de al menos 90 %</p>
    </article>
  </section>;
}
