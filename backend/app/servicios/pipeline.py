from backend.app.config import RUTA_ARISTAS, DIAS_MES
from backend.app.data.cargar import cargar_zonas, cargar_planta, cargar_aristas
from backend.app.ml.predictor import predecir_demanda
from backend.app.grafos.mst import calcular_red_menor_costo
from backend.app.grafos.flujo import evaluar_flujo
from backend.app.grafos.diagnostico import obtener_estados_flujo

df_zonas_base = cargar_zonas()
df_planta_base = cargar_planta()
df_candidatas_base = cargar_aristas()

def ejecutar_simulacion(escenario_crecimiento: float):
    # 1. Proyección de demanda mensual y conversión a diaria
    predicciones = predecir_demanda(df_zonas_base, escenario_crecimiento)
    
    demandas_diarias = {}
    for idx, fila in df_zonas_base.iterrows():
        demandas_diarias[fila['nodo_id']] = float(predicciones[idx] / DIAS_MES)
        
    # 2. Cálculo de red de tendidos de menor costo (Kruskal)
    mst, costo_total = calcular_red_menor_costo(RUTA_ARISTAS)
    
    # 3. Flujo máximo (Edmonds-Karp) hacia el super-sumidero
    abastecido, dict_flujos = evaluar_flujo(mst, demandas_diarias)
    
    # 4. Estados de flujo para cada tendido del MST
    estados_flujo = obtener_estados_flujo(mst, dict_flujos)
    
    # 5. Balance y resumen de capacidad
    demanda_total = sum(demandas_diarias.values())
    caudal_abastecido = min(abastecido, demanda_total)
    deficit = max(0.0, demanda_total - caudal_abastecido)
    
    resumen_capacidad = {
        "demanda_total_m3_dia": round(demanda_total, 2),
        "caudal_abastecido_m3_dia": round(caudal_abastecido, 2),
        "deficit_m3_dia": round(deficit, 2)
    }
    
    # 6. Preparación de la lista de todos los nodos (Barrios + PLANTA)
    nodos = []
    # Planta
    fila_planta = df_planta_base.iloc[0]
    nodos.append({
        "id": str(fila_planta["nodo_id"]),
        "latitud": float(fila_planta["latitud"]),
        "longitud": float(fila_planta["longitud"]),
        "tipo_zona": "PLANTA",
        "demanda_diaria_proyectada": 0.0
    })
    # Barrios
    for _, fila in df_zonas_base.iterrows():
        nid = fila["nodo_id"]
        nodos.append({
            "id": str(nid),
            "latitud": float(fila["latitud"]),
            "longitud": float(fila["longitud"]),
            "tipo_zona": str(fila["tipo_zona"]),
            "demanda_diaria_proyectada": round(demandas_diarias[nid], 2)
        })
        
    # 7. Tendidos candidatos
    candidatos = [
        {
            "origen": str(f["origen"]),
            "destino": str(f["destino"]),
            "costo": float(f["costo_unidades"]),
            "capacidad_maxima": float(f["capacidad_m3_dia"])
        }
        for _, f in df_candidatas_base.iterrows()
    ]
    
    return {
        "nodos": nodos,
        "mst": mst,
        "costo_total_mst": costo_total,
        "flujos": estados_flujo,
        "candidatos": candidatos,
        "resumen_capacidad": resumen_capacidad
    }
