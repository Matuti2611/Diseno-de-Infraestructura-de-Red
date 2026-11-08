import { PanelRed, type PropsPanelRed } from '../components/PanelRed';
import { DiagnosticoCapacidad } from '../components/DiagnosticoCapacidad';

export function VistaFlujo(props: PropsPanelRed) {
  return <>
    <DiagnosticoCapacidad red={props.red} />
    <PanelRed {...props} vista="capacidad" />
  </>;
}
