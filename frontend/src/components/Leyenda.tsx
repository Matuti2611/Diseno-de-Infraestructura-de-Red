import type { Vista } from '../types/red';

export function Leyenda({ vista, mostrarCandidatos }: { vista: Vista; mostrarCandidatos: boolean }) {
  return <ul className="leyenda" aria-label="Leyenda de la red">
    <li><span className="muestra-linea seleccionada" />Red seleccionada</li>
    {mostrarCandidatos && <li><span className="muestra-linea candidata" />Tendido posible</li>}
    {vista === 'capacidad' && <><li><span className="muestra-linea cercana" />Cerca del límite</li><li><span className="muestra-linea saturada" />Saturado</li><li><span className="muestra-linea desconocida" />Flujo no informado</li></>}
    <li><span className="muestra-nodo" />Barrio</li>
    <li><span className="muestra-planta" />Planta</li>
  </ul>;
}
