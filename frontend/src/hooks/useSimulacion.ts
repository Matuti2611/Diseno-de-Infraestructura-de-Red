import { useEffect, useState } from 'react';
import { solicitarSimulacion } from '../api/cliente';
import type { Escenario, SimulacionResponse } from '../types/red';

interface Estado {
  estado: 'cargando' | 'listo' | 'error';
  datos: SimulacionResponse | null;
  escenarioMostrado: Escenario | null;
  error: string | null;
}

export function useSimulacion() {
  const [escenario, setEscenario] = useState<Escenario>(1);
  const [intento, setIntento] = useState(0);
  const [resultado, setResultado] = useState<Estado>({ estado: 'cargando', datos: null, escenarioMostrado: null, error: null });
  useEffect(() => {
    const controlador = new AbortController();
    setResultado(anterior => ({ ...anterior, estado: 'cargando', error: null }));
    solicitarSimulacion(escenario, controlador.signal).then(datos => {
      if (!controlador.signal.aborted) setResultado({ estado: 'listo', datos, escenarioMostrado: escenario, error: null });
    }).catch((error: unknown) => {
      if (!controlador.signal.aborted) setResultado(anterior => ({ ...anterior, estado: 'error', error: error instanceof Error ? error.message : 'No se pudo obtener la simulación.' }));
    });
    return () => controlador.abort();
  }, [escenario, intento]);
  return { ...resultado, escenario, intento, setEscenario, reintentar: () => setIntento(valor => valor + 1) };
}
