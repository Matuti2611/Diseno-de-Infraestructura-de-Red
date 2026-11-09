import { useEffect, useRef, useState } from 'react';
import { solicitarSimulacion } from '../api/cliente';
import { nombreCaso, nombreEscenario, numero } from '../lib/red';
import type { CasoRed, Escenario, ResumenCapacidad } from '../types/red';
import LatticeLoader from './effects/LatticeLoader';

type Fila = { escenario: Escenario; resumen: ResumenCapacidad };

/** Solo presenta balances calculados por la API; no extrapola escenarios en el navegador. */
export function ComparacionEscenarios({ caso }: { caso: CasoRed }) {
  const [filas, setFilas] = useState<Fila[]>([]);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const peticion = useRef<AbortController | null>(null);
  useEffect(() => () => { peticion.current?.abort(); peticion.current = null; }, []);

  async function comparar() {
    peticion.current?.abort();
    const controlador = new AbortController();
    peticion.current = controlador;
    setCargando(true);
    setError(null);
    setFilas([]);
    try {
      const resultados = await Promise.all(([1, 1.1, 1.3] as const).map(async escenario => {
        const datos = await solicitarSimulacion(escenario, controlador.signal, caso);
        if (!datos.resumen_capacidad) throw new Error('La API no informó el balance de todos los escenarios.');
        return { escenario, resumen: datos.resumen_capacidad };
      }));
      if (!controlador.signal.aborted) setFilas(resultados);
    } catch (causa) {
      if (!controlador.signal.aborted) {
        setError(causa instanceof Error ? causa.message : 'No se pudo completar la comparación.');
        controlador.abort();
      }
    } finally {
      if (peticion.current === controlador) setCargando(false);
    }
  }

  return <section className="panel-comparacion" aria-labelledby="titulo-comparacion">
    <div className="panel-cabecera"><div><h2 id="titulo-comparacion">Comparar escenarios · {nombreCaso(caso)}</h2><p>Tres consultas al mismo caso para observar el efecto del crecimiento.</p></div><button className="boton-secundario" type="button" disabled={cargando} onClick={comparar}>{filas.length ? 'Actualizar comparación' : error ? 'Reintentar comparación' : 'Comparar escenarios'}</button></div>
    {cargando && <div className="comparacion-espera"><LatticeLoader label="Comparando escenarios…" color="#44749d" fontSize={12} /></div>}
    {error && <p className="comparacion-error" role="alert">{error} No se completó la comparación.</p>}
    {filas.length > 0 && <div className="tabla-scroll"><table aria-label="Comparación de escenarios"><thead><tr><th scope="col">Crecimiento</th><th scope="col">Demanda · m³/día</th><th scope="col">Suministro · m³/día</th><th scope="col">Déficit · m³/día</th><th scope="col">Cobertura</th></tr></thead><tbody>{filas.map(({ escenario, resumen }) => <tr key={escenario}>
      <th scope="row">{nombreEscenario(escenario)}</th><td>{numero(resumen.demanda_total_m3_dia, 2)}</td><td>{numero(resumen.caudal_abastecido_m3_dia, 2)}</td><td>{numero(resumen.deficit_m3_dia, 2)}</td><td>{numero(resumen.demanda_total_m3_dia > 0 ? resumen.caudal_abastecido_m3_dia / resumen.demanda_total_m3_dia * 100 : 100, 1)} % · {resumen.deficit_m3_dia > 0 ? 'Con déficit' : 'Cubierta'}</td>
    </tr>)}</tbody></table></div>}
  </section>;
}
