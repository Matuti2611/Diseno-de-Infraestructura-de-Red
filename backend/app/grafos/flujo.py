import networkx as nx

def evaluar_flujo(mst, demandas_diarias):
    """
    Recibe el MST y las demandas predichas para diagnosticar la red usando Edmonds-Karp.
    """
    G_flujo = nx.DiGraph()
    
    for u, v, datos in mst.edges(data=True):
        capacidad = datos['capacidad_m3_dia']
        G_flujo.add_edge(u, v, capacity=capacidad)
        G_flujo.add_edge(v, u, capacity=capacidad)
        
    demanda_total = 0
    for barrio, demanda in demandas_diarias.items():
        if barrio != 'PLANTA':
            G_flujo.add_edge(barrio, 'SUPER_SUMIDERO', capacity=demanda)
            demanda_total += demanda
            
    flujo_abastecido, dict_flujos = nx.maximum_flow(G_flujo, _s='PLANTA', _t='SUPER_SUMIDERO')
    
    saturadas = []
    for u, v, datos in mst.edges(data=True):
        capacidad_max = datos['capacidad_m3_dia']
        flujo_neto = abs(dict_flujos[u][v] - dict_flujos[v][u])
        porcentaje_uso = (flujo_neto / capacidad_max) * 100
        
        if porcentaje_uso >= 90.0:
            saturadas.append({
                "origen": u, 
                "destino": v, 
                "flujo": flujo_neto, 
                "capacidad": capacidad_max, 
                "uso_pct": porcentaje_uso
            })
            
    return flujo_abastecido, demanda_total, saturadas

if __name__ == "__main__":
    from mst import calcular_red_menor_costo
    import pandas as pd
    
    ruta_aristas = 'backend/data/raw/aristas_candidatas.csv'
    ruta_zonas = 'backend/data/raw/zonas.csv'
    
    red_optima, _ = calcular_red_menor_costo(ruta_aristas)
    
    df_zonas = pd.read_csv(ruta_zonas)
    demandas_mock = {}
    for _, fila in df_zonas.iterrows():
        demanda_diaria = (fila['consumo_historico_mensual'] / 30) * 1.20 
        demandas_mock[fila['nodo_id']] = demanda_diaria
        
    abastecido, requerido, saturadas = evaluar_flujo(red_optima, demandas_mock)
    
    print("--- Diagnóstico de Capacidad (Simulación +20%) ---")
    print(f"Agua requerida: {requerido:.2f} m3/día")
    print(f"Agua abastecida: {abastecido:.2f} m3/día")
    
    if abastecido < requerido:
        print("¡ALERTA! La red no da abasto para toda la zona.")
    else:
        print("La red cubre la demanda perfectamente.")
        
    print(f"\nAristas en estado crítico (>= 90% de uso): {len(saturadas)}")
    for s in saturadas:
        print(f" - {s['origen']} <-> {s['destino']}: {s['uso_pct']:.1f}% ({s['flujo']:.1f} / {s['capacidad']} m3/día)")