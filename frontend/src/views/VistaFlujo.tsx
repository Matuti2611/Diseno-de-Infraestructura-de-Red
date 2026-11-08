import { PanelRed, type PropsPanelRed } from '../components/PanelRed';
import { Icono } from '../components/Icono';

export function VistaFlujo(props: PropsPanelRed) {
  const seleccionadas = props.red.aristas.filter(a => a.seleccionada).length;
  return <>
    <div className="aviso-capacidad"><Icono nombre="info" /><div><strong>Lectura de capacidad</strong><p>Hay caudal informado para {props.red.flujosInformados} de {seleccionadas} tendidos. Los demás figuran como «Sin dato». El abastecimiento total y el déficit todavía no están informados por el servicio.</p></div></div>
    <PanelRed {...props} vista="capacidad" />
  </>;
}
