from pydantic import BaseModel, Field
from typing import List

class EscenarioRequest(BaseModel):
    # Selector de escenario de crecimiento (por ejemplo, +10%, +30%)[span_0](start_span)[span_0](end_span)
    escenario_crecimiento: float = Field(
        default=1.0, 
        description="Multiplicador de demanda (ej. 1.10 para +10%)"
    )

class NodoRed(BaseModel):
    id: str
    latitud: float
    longitud: float
    tipo_zona: str
    demanda_diaria_proyectada: float 

class TendidoMST(BaseModel):
    # Aristas de la red de menor costo calculada con Kruskal o Prim[span_1](start_span)[span_1](end_span)
    origen: str
    destino: str
    costo: float
    capacidad_maxima: float

class EstadoFlujo(BaseModel):
    # Flujo sobre cada arista, identificando las saturadas[span_2](start_span)[span_2](end_span)[span_3](start_span)[span_3](end_span)
    origen: str
    destino: str
    flujo_actual: float
    capacidad_maxima: float
    saturada: bool

class MetricasML(BaseModel):
    # Métricas obligatorias del modelo de regresión[span_4](start_span)[span_4](end_span)
    mae: float
    rmse: float
    r2: float

class SimulacionResponse(BaseModel):
    nodos: List[NodoRed]
    tendidos_mst: List[TendidoMST]
    flujos: List[EstadoFlujo]
    metricas_ml: MetricasML
  
