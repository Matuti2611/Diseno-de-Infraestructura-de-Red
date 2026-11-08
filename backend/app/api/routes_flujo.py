from fastapi import APIRouter, HTTPException
from backend.app.config import RUTA_METRICAS
from backend.app.ml.metricas import leer_metricas
from backend.app.schemas import (
    EscenarioRequest, SimulacionResponse, NodoRed,
    TendidoMST, EstadoFlujo, ResumenCapacidad, MetricasML
)
from backend.app.servicios.pipeline import ejecutar_simulacion

router = APIRouter()

def cargar_metricas() -> MetricasML | None:
    datos = leer_metricas(RUTA_METRICAS)
    return MetricasML(**datos) if datos is not None else None

@router.post("/simular-red", response_model=SimulacionResponse)
def simular_red(request: EscenarioRequest):
    if request.escenario_crecimiento <= 0:
        raise HTTPException(status_code=400, detail="El escenario de crecimiento debe ser mayor a 0")
        
    try:
        resultado = ejecutar_simulacion(request.escenario_crecimiento)
    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    
    nodos_res = [
        NodoRed(
            id=n["id"],
            latitud=n["latitud"],
            longitud=n["longitud"],
            tipo_zona=n["tipo_zona"],
            demanda_diaria_proyectada=n["demanda_diaria_proyectada"]
        )
        for n in resultado["nodos"]
    ]
    
    tendidos_res = [
        TendidoMST(
            origen=u,
            destino=v,
            costo=d["costo_unidades"],
            capacidad_maxima=d["capacidad_m3_dia"]
        )
        for u, v, d in resultado["mst"].edges(data=True)
    ]
    
    candidatos_res = [
        TendidoMST(
            origen=c["origen"],
            destino=c["destino"],
            costo=c["costo"],
            capacidad_maxima=c["capacidad_maxima"]
        )
        for c in resultado["candidatos"]
    ]
    
    flujos_res = [
        EstadoFlujo(
            origen=f["origen"],
            destino=f["destino"],
            flujo_actual=f["flujo_actual"],
            capacidad_maxima=f["capacidad_maxima"],
            saturada=f["saturada"]
        )
        for f in resultado["flujos"]
    ]
    
    rc = resultado["resumen_capacidad"]
    resumen_res = ResumenCapacidad(
        demanda_total_m3_dia=rc["demanda_total_m3_dia"],
        caudal_abastecido_m3_dia=rc["caudal_abastecido_m3_dia"],
        deficit_m3_dia=rc["deficit_m3_dia"]
    )
    
    return SimulacionResponse(
        nodos=nodos_res,
        tendidos_mst=tendidos_res,
        tendidos_candidatos=candidatos_res,
        flujos=flujos_res,
        resumen_capacidad=resumen_res,
        metricas_ml=cargar_metricas()
    )
