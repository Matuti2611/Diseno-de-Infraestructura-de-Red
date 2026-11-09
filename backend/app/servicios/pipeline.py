from math import isfinite
from backend.app.config import RUTA_ARISTAS, RUTA_ARISTAS_PROGRESIVAS, DIAS_MES
from backend.app.data.cargar import cargar_zonas, cargar_planta, cargar_aristas
from backend.app.ml.predictor import predecir_demanda
from backend.app.grafos.mst import calcular_red_menor_costo
from backend.app.grafos.flujo import evaluar_flujo
from backend.app.grafos.diagnostico import obtener_estados_flujo

df_zonas_base = cargar_zonas()
df_planta_base = cargar_planta()

def ejecutar_simulacion(escenario_crecimiento: float, caso_red: str = 'original'):
    rutas = {'original': RUTA_ARISTAS, 'progresivo': RUTA_ARISTAS_PROGRESIVAS}
    if caso_red not in rutas:
        raise ValueError('El caso de red no está disponible.')
    ruta_aristas = rutas[caso_red]
    candidatas = cargar_aristas(ruta_aristas)
    # 1. Proyección de demanda mensual y conversión a diaria
    predicciones = predecir_demanda(df_zonas_base, escenario_crecimiento)
    
    demandas_diarias = {}
    for idx, fila in df_zonas_base.iterrows():
        demandas_diarias[fila['nodo_id']] = float(predicciones[idx] / DIAS_MES)
        
    # 2. Cálculo de red de tendidos de menor costo (Kruskal)
    nodos_esperados = set(df_zonas_base['nodo_id']) | set(df_planta_base['nodo_id'])
    mst, costo_total = calcular_red_menor_costo(ruta_aristas, nodos_esperados=nodos_esperados)
    
    # 3. Flujo máximo (Edmonds-Karp) hacia el super-sumidero
    abastecido, dict_flujos = evaluar_flujo(mst, demandas_diarias)
    
    # 4. Estados de flujo para cada tendido del MST
    estados_flujo = obtener_estados_flujo(mst, dict_flujos)
    
    # El consumo efectivo es el flujo al supersumidero, no el tránsito por una cañería.
    suministros = {n: float(dict_flujos.get(n, {}).get('SUPER_SUMIDERO', 0.0)) for n in demandas_diarias}
    for nodo, demanda in demandas_diarias.items():
        suministro = suministros[nodo]
        if not isfinite(demanda) or not isfinite(suministro) or demanda < 0 or suministro < -1e-6 or suministro > demanda + 1e-6:
            raise ValueError('El abastecimiento por barrio no respeta la demanda.')
    if not isfinite(abastecido) or abs(sum(suministros.values()) - abastecido) > 1e-6:
        raise ValueError('El abastecimiento por barrio no coincide con el flujo total.')
    
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
        demanda = round(demandas_diarias[nid], 2)
        suministro = min(demanda, round(max(0.0, suministros[nid]), 2))
        nodos.append({
            "id": str(nid),
            "latitud": float(fila["latitud"]),
            "longitud": float(fila["longitud"]),
            "tipo_zona": str(fila["tipo_zona"]),
            "demanda_diaria_proyectada": demanda,
            "caudal_abastecido_m3_dia": suministro,
            "deficit_m3_dia": round(demanda - suministro, 2)
        })

    # Sumar las cantidades publicadas evita divergencias acumuladas de redondeo.
    barrios = nodos[1:]
    dem_red = round(sum(n['demanda_diaria_proyectada'] for n in barrios), 2)
    aba_red = round(sum(n['caudal_abastecido_m3_dia'] for n in barrios), 2)
    resumen_capacidad = {
        'demanda_total_m3_dia': dem_red,
        'caudal_abastecido_m3_dia': aba_red,
        'deficit_m3_dia': round(dem_red - aba_red, 2),
    }
        
    # 7. Tendidos candidatos
    candidatos = [
        {
            "origen": str(f["origen"]),
            "destino": str(f["destino"]),
            "costo": float(f["costo_unidades"]),
            "capacidad_maxima": float(f["capacidad_m3_dia"])
        }
        for _, f in candidatas.iterrows()
    ]
    
    return {
        'caso_red': caso_red,
        'escenario_crecimiento': escenario_crecimiento,
        "nodos": nodos,
        "mst": mst,
        "costo_total_mst": costo_total,
        "flujos": estados_flujo,
        "candidatos": candidatos,
        "resumen_capacidad": resumen_capacidad
    }
