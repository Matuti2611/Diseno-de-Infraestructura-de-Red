from pydantic import BaseModel, Field
from typing import List, Optional

class EscenarioRequest(BaseModel):
    escenario_crecimiento: float = Field(
        default=1.0, 
        gt=0.0,
        le=5.0,
        description="Multiplicador de demanda / tasa de crecimiento (ej. 1.10 para +10%)"
    )

class NodoRed(BaseModel):
    id: str
    latitud: float
    longitud: float
    tipo_zona: str
    demanda_diaria_proyectada: float 

class TendidoMST(BaseModel):
    origen: str
    destino: str
    costo: float
    capacidad_maxima: float

class EstadoFlujo(BaseModel):
    origen: str
    destino: str
    flujo_actual: float
    capacidad_maxima: float
    saturada: bool

class ResumenCapacidad(BaseModel):
    demanda_total_m3_dia: float
    caudal_abastecido_m3_dia: float
    deficit_m3_dia: float

class MetricasML(BaseModel):
    mae: float
    rmse: float
    r2: float

class SimulacionResponse(BaseModel):
    nodos: List[NodoRed]
    tendidos_mst: List[TendidoMST]
    tendidos_candidatos: Optional[List[TendidoMST]] = None
    flujos: List[EstadoFlujo]
    resumen_capacidad: Optional[ResumenCapacidad] = None
    metricas_ml: Optional[MetricasML] = None
