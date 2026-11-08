import { lazy, Suspense, useMemo, useState } from 'react';
import { API_URL } from './api/cliente';
import { Icono } from './components/Icono';
import { PanelDiagnostico } from './components/PanelDiagnostico';
import { SelectorEscenario } from './components/SelectorEscenario';
import { TablaAristas } from './components/TablaAristas';
import LatticeLoader from './components/effects/LatticeLoader';
import { useSimulacion } from './hooks/useSimulacion';
import { construirRed, nombreEscenario, numero } from './lib/red';
import type { Seleccion, Vista } from './types/red';
import { VistaTendidos } from './views/VistaTendidos';
import { VistaFlujo } from './views/VistaFlujo';

const VistaEfectos = lazy(() => import('./views/VistaEfectos'));
type Seccion = Vista | 'efectos';

export default function App() {
  const [vista, setVista] = useState<Seccion>('tendidos');
  const [seleccion, setSeleccion] = useState<Seleccion>({ tipo: 'nodo', id: 'PLANTA' });
  const simulacion = useSimulacion();
  const red = useMemo(() => simulacion.datos ? construirRed(simulacion.datos) : null, [simulacion.datos]);
  const cargando = simulacion.estado === 'cargando';
  const resultadoAnterior = simulacion.escenarioMostrado !== null && simulacion.escenarioMostrado !== simulacion.escenario;
  const irVista = (nueva: Seccion) => { setVista(nueva); setSeleccion({ tipo: 'nodo', id: 'PLANTA' }); };
  return <div className="aplicacion">
    <a href="#contenido" className="saltar-contenido">Ir al contenido</a>
    <aside className="barra-lateral" aria-label="Navegación del proyecto">
      <a className="marca" href="#contenido"><span className="marca-simbolo"><Icono nombre="agua" /></span><span><strong>Red de Agua</strong><small>Planificación de infraestructura</small></span></a>
      <p className="nav-etiqueta">ESPACIO DE TRABAJO</p>
      <nav><button type="button" className={vista === 'tendidos' ? 'nav-activo' : ''} aria-current={vista === 'tendidos' ? 'page' : undefined} onClick={() => irVista('tendidos')}><Icono nombre="red" />Diseño de red<span>01</span></button><button type="button" className={vista === 'capacidad' ? 'nav-activo' : ''} aria-current={vista === 'capacidad' ? 'page' : undefined} onClick={() => irVista('capacidad')}><Icono nombre="flujo" />Capacidad y flujo<span>02</span></button><button type="button" className={vista === 'efectos' ? 'nav-activo' : ''} aria-current={vista === 'efectos' ? 'page' : undefined} onClick={() => irVista('efectos')}><Icono nombre="brillo" />Efectos visuales<span>03</span></button></nav>
      <div className="caso-lateral"><span className="etiqueta-superior">CASO DE ESTUDIO</span><div className="caso-dibujo" aria-hidden="true"><i /><i /><i /><i /><i /><i /></div><strong>Una red para crecer</strong><p>Una planta, 16 barrios y una decisión de infraestructura.</p><span className="etiqueta-caso">Datos sintéticos</span></div>
      <div className="lateral-pie"><Icono nombre="info" /><p>Trabajo integrador<br /><strong>Lógica y Teoría de Grafos</strong></p></div>
    </aside>
    <div className="area-principal">
      <header className="cabecera"><span className="ruta-cabecera">Infraestructura <span>/</span> <strong>Red de distribución</strong></span></header>
      <main id="contenido" className="contenido">
        <div className="presentacion"><div><span className="etiqueta-superior">DISEÑO DE INFRAESTRUCTURA</span><h1>El agua conecta.<br className="salto-movil" /> La planificación también.</h1><p>Explorá la red de menor costo y evaluá cómo responde<br className="salto-desktop" /> a la demanda futura de cada barrio.</p></div><span className="horizonte"><Icono nombre="agua" /><span>Horizonte de análisis<strong>5 años</strong></span></span></div>
        <div className="navegacion-vistas" role="group" aria-label="Vista de la red"><button type="button" aria-pressed={vista === 'tendidos'} onClick={() => irVista('tendidos')}><Icono nombre="red" />Tendidos</button><button type="button" aria-pressed={vista === 'capacidad'} onClick={() => irVista('capacidad')}><Icono nombre="flujo" />Capacidad</button><button type="button" aria-pressed={vista === 'efectos'} onClick={() => irVista('efectos')}><Icono nombre="brillo" />Efectos</button><span>De la proyección al diseño</span></div>
        {vista === 'efectos' ? <Suspense fallback={<p role="status">Cargando tarjeta…</p>}><VistaEfectos /></Suspense> : <>
        <section className="barra-escenarios" aria-label="Configuración de la simulación"><div><SelectorEscenario valor={simulacion.escenario} onChange={simulacion.setEscenario} /><p>Base conserva la tasa de cada barrio. +30 % multiplica esa tasa por 1,3; no aumenta directamente el consumo un 30 %.</p></div><button type="button" className="boton-secundario" disabled={cargando} onClick={simulacion.reintentar}><Icono nombre="actualizar" />Actualizar simulación</button></section>
        <div className="estado-resultados"><span className="resultado-etiqueta" aria-live="polite">{simulacion.escenarioMostrado !== null ? `Resultado mostrado: ${nombreEscenario(simulacion.escenarioMostrado)}` : 'Sin resultados disponibles'}</span>{cargando && <LatticeLoader key={`${simulacion.escenario}-${simulacion.intento}`} label="Calculando escenario…" pattern="orbit" grid={3} shape="round" color="#44749d" fontSize={12} showTimer />}</div>
        {simulacion.error && <div className="mensaje-error" role="alert"><Icono nombre="alerta" /><div><strong>No pudimos obtener la simulación.</strong><p>{simulacion.error}{simulacion.datos ? ` Se conservan los resultados de ${nombreEscenario(simulacion.escenarioMostrado!)}.` : ''}</p><button className="enlace-boton" onClick={simulacion.reintentar}>Volver a intentar <span aria-hidden="true">→</span></button></div></div>}
        {resultadoAnterior && !simulacion.error && <p className="aviso-anterior">Se muestran los resultados anteriores mientras se consulta el escenario {nombreEscenario(simulacion.escenario)}.</p>}
        <PanelDiagnostico red={red} />
        {red && red.nodos.length > 0 ? <>
          {vista === 'tendidos' ? <VistaTendidos red={red} seleccion={seleccion} onSeleccionar={setSeleccion} /> : <VistaFlujo red={red} seleccion={seleccion} onSeleccionar={setSeleccion} />}
          <TablaAristas key={vista} red={red} vista={vista} seleccion={seleccion} onSeleccionar={setSeleccion} />
        </> : <section className="estado-vacio" aria-label="Estado de la red"><Icono nombre={cargando ? 'red' : 'info'} /><h2>{cargando ? 'Preparando la red' : simulacion.error ? 'La red todavía no está disponible' : 'No hay zonas para mostrar'}</h2><p>{cargando ? 'Estamos consultando el modelo y el diseño de la red. La primera respuesta puede demorar.' : 'Los resultados aparecerán aquí cuando la simulación devuelva una red válida.'}</p></section>}
        <details className="metodologia"><summary><span><Icono nombre="info" />Sobre los datos y el modelo</span><span className="simbolo-mas" aria-hidden="true">+</span></summary><div className="metodologia-cuerpo"><div><h3>Un caso para explorar decisiones</h3><p>Las poblaciones, consumos, costos y capacidades son sintéticos. Las predicciones y el diseño seleccionado se consultan en la API; la página no entrena modelos ni calcula la red óptima.</p><p>{red?.fuenteGeometria === 'csv' ? 'Las ubicaciones de la planta y los tendidos candidatos se completan con los CSV versionados del proyecto, luego de comprobar su coincidencia con la simulación.' : red?.fuenteGeometria === 'solo-mst' ? 'La respuesta usa una red distinta del caso versionado: se muestran solo los tendidos recibidos.' : 'La geometría y las simulaciones se presentan con su origen identificado.'}</p></div><div><h3>Evaluación del consumo</h3>{simulacion.datos?.metricas_ml ? <><dl className="metricas-modelo"><div><dt>MAE · m³/mes</dt><dd>{numero(simulacion.datos.metricas_ml.mae, 2)}</dd></div><div><dt>RMSE · m³/mes</dt><dd>{numero(simulacion.datos.metricas_ml.rmse, 2)}</dd></div><div><dt>R²</dt><dd>{numero(simulacion.datos.metricas_ml.r2, 4)}</dd></div></dl><p>Métricas informadas por la API sobre el conjunto sintético.</p></> : <p>Las métricas aparecerán cuando estén disponibles en la respuesta del servicio.</p>}<a className="enlace-api" href={`${API_URL}/docs`} target="_blank" rel="noreferrer">Consultar documentación de la API <Icono nombre="externo" /></a></div></div></details>
        </>}
        <footer className="pie-pagina"><span><Icono nombre="agua" />Diseño de infraestructura de red de agua</span><span>Modelo predictivo + teoría de grafos</span></footer>
      </main>
    </div>
  </div>;
}
