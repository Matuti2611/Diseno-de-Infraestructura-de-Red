export type Escenario = 1 | 1.1 | 1.3;
export type CasoRed = 'original' | 'progresivo';
export type Vista = 'tendidos' | 'capacidad';

export interface NodoRed {
  id: string;
  latitud: number;
  longitud: number;
  tipo_zona: string;
  demanda_diaria_proyectada: number;
  caudal_abastecido_m3_dia?: number | null;
  deficit_m3_dia?: number | null;
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

/** Extensión propuesta: totales calculados por el backend, nunca por suma de cañerías. */
export interface ResumenCapacidad {
  demanda_total_m3_dia: number;
  caudal_abastecido_m3_dia: number;
  deficit_m3_dia: number;
}

export interface SimulacionResponse {
  caso_red?: CasoRed;
  escenario_crecimiento?: number;
  nodos: NodoRed[];
  tendidos_mst: TendidoMST[];
  flujos: EstadoFlujo[];
  metricas_ml: MetricasML | null;
  tendidos_candidatos?: TendidoMST[];
  resumen_capacidad?: ResumenCapacidad | null;
}

export type EstadoTramo = 'candidato' | 'sin-dato' | 'informado' | 'cercano' | 'saturado' | 'sin-capacidad';

export interface NodoVisual {
  id: string;
  latitud: number;
  longitud: number;
  tipo_zona: string;
  demanda: number | null;
  suministro?: number | null;
  deficit?: number | null;
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
  resumenCapacidad: ResumenCapacidad | null;
}

export type Seleccion = { tipo: 'nodo' | 'arista'; id: string } | null;
