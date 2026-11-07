from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import joblib
import warnings

# Suprimir warnings de sklearn para consola limpia
warnings.filterwarnings("ignore")

from backend.app.schemas import EscenarioRequest, SimulacionResponse, NodoRed, TendidoMST, EstadoFlujo, MetricasML
from backend.app.grafos.mst import calcular_red_menor_costo
from backend.app.grafos.flujo import evaluar_flujo

app = FastAPI(title="API Red de Agua")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

modelo = joblib.load('backend/models/modelo_consumo.joblib')
df_zonas_base = pd.read_csv('backend/data/raw/zonas.csv')
ruta_aristas = 'backend/data/raw/aristas_candidatas.csv'

@app.post("/api/simular-red", response_model=SimulacionResponse)
def simular_red(request: EscenarioRequest):
    df_zonas = df_zonas_base.copy()
    
    df_zonas['crecimiento_poblacional_estimado'] *= request.escenario_crecimiento
    
    X = df_zonas.drop(columns=['nodo_id'])
    X = pd.get_dummies(X, columns=['tipo_zona'], drop_first=True)
    X = X.reindex(columns=modelo.feature_names_in_, fill_value=0)
    
    predicciones = modelo.predict(X)
    
    nodos_response = []
    demandas_diarias = {}
    
    for idx, fila in df_zonas.iterrows():
        demanda_diaria = predicciones[idx] / 30.0
        nodos_response.append(
            NodoRed(
                id=fila['nodo_id'],
                latitud=fila['latitud'],
                longitud=fila['longitud'],
                tipo_zona=df_zonas_base.loc[idx, 'tipo_zona'],
                demanda_diaria_proyectada=demanda_diaria
            )
        )
        demandas_diarias[fila['nodo_id']] = demanda_diaria
        
    red_optima, _ = calcular_red_menor_costo(ruta_aristas)
    
    tendidos_response = []
    for u, v, datos in red_optima.edges(data=True):
        tendidos_response.append(
            TendidoMST(
                origen=u, 
                destino=v, 
                costo=datos['costo_unidades'], 
                capacidad_maxima=datos['capacidad_m3_dia']
            )
        )
        
    _, _, saturadas = evaluar_flujo(red_optima, demandas_diarias)
    
    flujos_response = [
        EstadoFlujo(
            origen=s['origen'], 
            destino=s['destino'], 
            flujo_actual=s['flujo'], 
            capacidad_maxima=s['capacidad'], 
            saturada=True
        )
        for s in saturadas
    ]
    
    return SimulacionResponse(
        nodos=nodos_response,
        tendidos_mst=tendidos_response,
        flujos=flujos_response,
        metricas_ml=MetricasML(mae=131.28, rmse=172.97, r2=0.9939)
    )