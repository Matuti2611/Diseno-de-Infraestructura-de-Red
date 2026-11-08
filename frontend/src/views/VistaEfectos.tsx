import { useState } from 'react';
import HoloCard from '../components/effects/HoloCard';
import pikachu from '../assets/pikachu.webp';
import './VistaEfectos.css';

export default function VistaEfectos() {
  const [movimiento, setMovimiento] = useState(true);
  return <section className="vista-efectos" aria-labelledby="titulo-efectos">
    <div className="efectos-introduccion">
      <span className="etiqueta-superior">EXPLORACIÓN VISUAL</span>
      <h2 id="titulo-efectos">Tarjeta holográfica</h2>
      <p>Mové el cursor sobre Pikachu para descubrir los reflejos.</p>
    </div>
    <figure className="efectos-escena">
      <HoloCard image={pikachu} alt="Carta holográfica de Pikachu" preset="bursts"
        foilColor="#e2e6ec" intensity={0.85} scale={1} edgeSparkle={0.8}
        frame={4} glare={0.5} tiltMax={movimiento ? 14 : 0}
        hoverScale={movimiento ? 1.04 : 1} radius={14} width={320}
        idle={movimiento} shadow />
      <figcaption>Pikachu <span aria-hidden="true">·</span> Holo Card</figcaption>
      <button type="button" className="boton-secundario" aria-pressed={!movimiento} onClick={() => setMovimiento(valor => !valor)}>{movimiento ? 'Pausar movimiento' : 'Activar movimiento'}</button>
    </figure>
    <p className="efectos-nota">Una prueba visual independiente de los resultados de la red.</p>
  </section>;
}
