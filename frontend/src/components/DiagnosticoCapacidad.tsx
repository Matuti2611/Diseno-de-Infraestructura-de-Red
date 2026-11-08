import { useId } from 'react';
import { numero } from '../lib/red';
import type { RedVisual } from '../types/red';
import { Icono } from './Icono';

export function DiagnosticoCapacidad({ red }: { red: RedVisual }) {
  const id = useId();
  const resumen = red.resumenCapacidad;
  const estado = !resumen ? 'pendiente' : resumen.deficit_m3_dia > 0 ? 'deficit' : 'cubierta';
  const titulo = !resumen ? 'Diagnóstico incompleto' : resumen.demanda_total_m3_dia === 0 ? 'Sin demanda proyectada'
    : estado === 'deficit' ? 'La red no cubre toda la demanda' : 'La red cubre la demanda proyectada';
  const seleccionadas = red.aristas.filter(a => a.seleccionada).length;
  return <section className={`diagnostico-capacidad diagnostico-${estado}`} aria-labelledby={id}>
    <div className="diagnostico-titulo"><Icono nombre={estado === 'deficit' ? 'alerta' : 'info'} /><div>
      <span className="etiqueta-superior">DIAGNÓSTICO DE ABASTECIMIENTO</span><h2 id={id}>{titulo}</h2>
      {!resumen && <p>El abastecimiento total y el déficit todavía no están informados por el servicio. No se puede determinar si la red alcanza con los datos disponibles.</p>}
      {resumen && <p>Balance informado por el backend para el escenario mostrado. {estado === 'deficit' ? 'Hay consumo proyectado que la red no logra abastecer.' : 'El caudal abastecido alcanza para la demanda de este escenario.'}</p>}
    </div></div>
    {resumen && <dl className="balance-agua">
      <div><dt>Demanda total</dt><dd>{numero(resumen.demanda_total_m3_dia, 2)} <small>m³/día</small></dd></div>
      <div><dt>Caudal abastecido</dt><dd>{numero(resumen.caudal_abastecido_m3_dia, 2)} <small>m³/día</small></dd></div>
      <div><dt>Déficit</dt><dd>{numero(resumen.deficit_m3_dia, 2)} <small>m³/día</small></dd></div>
    </dl>}
    <p className="diagnostico-cobertura">Hay caudal informado para {red.flujosInformados} de {seleccionadas} tendidos.
      {red.flujosInformados < seleccionadas ? ' Los demás figuran como «Sin dato»; no se interpretan como flujo cero.' : ' Todos los tendidos seleccionados tienen dato de flujo.'}</p>
  </section>;
}
