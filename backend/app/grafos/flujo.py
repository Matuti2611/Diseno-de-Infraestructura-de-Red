import networkx as nx

def evaluar_flujo(mst, demandas_diarias):
    """
    Arma el grafo dirigido y calcula el flujo máximo usando Edmonds-Karp.
    """
    G_flujo = nx.DiGraph()
    
    for u, v, datos in mst.edges(data=True):
        capacidad = datos['capacidad_m3_dia']
        G_flujo.add_edge(u, v, capacity=capacidad)
        G_flujo.add_edge(v, u, capacity=capacidad)
        
    for barrio, demanda in demandas_diarias.items():
        if barrio != 'PLANTA':
            G_flujo.add_edge(barrio, 'SUPER_SUMIDERO', capacity=demanda)
            
    flujo_abastecido, dict_flujos = nx.maximum_flow(G_flujo, _s='PLANTA', _t='SUPER_SUMIDERO')
    
    return flujo_abastecido, dict_flujos