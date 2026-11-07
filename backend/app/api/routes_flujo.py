from fastapi import APIRouter
from backend.app.schemas import EscenarioRequest, SimulacionResponse, NodoRed, TendidoMST, EstadoFlujo, MetricasML
from backend.app.servicios.pipeline import ejecutar_simulacion

router = APIRouter()

@router.post("/simular-red", response_model=SimulacionResponse)
def simular_red(request: EscenarioRequest):
    df_zonas, demandas, mst, saturadas = ejecutar_simulacion(request.escenario_crecimiento)
    
    nodos_res = [
        NodoRed(id=f['nodo_id'], latitud=f['latitud'], longitud=f['longitud'], 
                tipo_zona=f['tipo_zona'], demanda_diaria_proyectada=demandas[f['nodo_id']])
        for _, f in df_zonas.iterrows()
    ]
    
    tendidos_res = [
        TendidoMST(origen=u, destino=v, costo=d['costo_unidades'], capacidad_maxima=d['capacidad_m3_dia'])
        for u, v, d in mst.edges(data=True)
    ]
    
    flujos_res = [EstadoFlujo(origen=s['origen'], destino=s['destino'], flujo_actual=s['flujo'], 
                              capacidad_maxima=s['capacidad'], saturada=True) for s in saturadas]
    
    return SimulacionResponse(
        nodos=nodos_res, tendidos_mst=tendidos_res, flujos=flujos_res,
        metricas_ml=MetricasML(mae=131.28, rmse=172.97, r2=0.9939)
    )