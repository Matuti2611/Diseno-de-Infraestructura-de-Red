export type Escenario = 1 | 1.1 | 1.3;
export type Vista = 'tendidos' | 'capacidad';

export interface NodoRed {
  id: string;
  latitud: number;
  longitud: number;
  tipo_zona: string;
  demanda_diaria_proyectada: number;
}

export interface TendidoMST {
  origen: string;
  destino: string;
  costo: number;
  capacidad_maxima: number;
}

export interface EstadoFlujo {
  origen: string;
  destino: string;
  flujo_actual: number;
  capacidad_maxima: number;
  saturada: boolean;
}

export interface MetricasML {
  mae: number;
  rmse: number;
  r2: number;
}

export interface SimulacionResponse {
  nodos: NodoRed[];
  tendidos_mst: TendidoMST[];
  flujos: EstadoFlujo[];
  metricas_ml: MetricasML | null;
  tendidos_candidatos?: TendidoMST[];
}

export type EstadoTramo = 'candidato' | 'sin-dato' | 'informado' | 'cercano' | 'saturado' | 'sin-capacidad';

export interface NodoVisual {
  id: string;
  latitud: number;
  longitud: number;
  tipo_zona: string;
  demanda: number | null;
  poblacion?: number;
}

export interface AristaVisual extends TendidoMST {
  id: string;
  seleccionada: boolean;
  flujo: number | null;
  utilizacion: number | null;
  estado: EstadoTramo;
  distancia_m?: number;
}

export interface RedVisual {
  nodos: NodoVisual[];
  aristas: AristaVisual[];
  fuenteGeometria: 'api' | 'csv' | 'solo-mst';
  costoTotal: number;
  demandaTotal: number;
  cantidadBarrios: number;
  tramosCriticos: number;
  flujosInformados: number;
  ubicacionesFaltantes: string[];
}

export type Seleccion = { tipo: 'nodo' | 'arista'; id: string } | null;
