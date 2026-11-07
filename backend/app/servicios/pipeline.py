import pandas as pd
from backend.app.config import RUTA_ZONAS, RUTA_ARISTAS, DIAS_MES
from backend.app.ml.predictor import predecir_demanda
from backend.app.grafos.mst import calcular_red_menor_costo
from backend.app.grafos.flujo import evaluar_flujo
from backend.app.grafos.diagnostico import obtener_aristas_saturadas

df_zonas_base = pd.read_csv(RUTA_ZONAS)

def ejecutar_simulacion(escenario_crecimiento: float):
    predicciones = predecir_demanda(df_zonas_base, escenario_crecimiento)
    
    demandas_diarias = {}
    for idx, fila in df_zonas_base.iterrows():
        demandas_diarias[fila['nodo_id']] = predicciones[idx] / DIAS_MES
        
    mst, costo_total = calcular_red_menor_costo(RUTA_ARISTAS)
    
    abastecido, dict_flujos = evaluar_flujo(mst, demandas_diarias)
    saturadas = obtener_aristas_saturadas(mst, dict_flujos)
    
    return df_zonas_base, demandas_diarias, mst, saturadas