import collections
import networkx as nx

def bfs_manual(capacidad, flujo, s, t, padres):
    visitados = set([s])
    cola = collections.deque([s])
    
    while cola:
        u = cola.popleft()
        for v in capacidad[u]:
            if v not in visitados and capacidad[u][v] - flujo[u][v] > 0:
                padres[v] = u
                if v == t:
                    return True
                cola.append(v)
                visitados.add(v)
    return False

def edmonds_karp_manual(nodos, aristas, s, t):
    capacidad = {n: {} for n in nodos}
    flujo = {n: {} for n in nodos}
    
    for u, v, cap in aristas:
        capacidad[u][v] = cap
        if u not in capacidad[v]:
            capacidad[v][u] = 0
        flujo[u][v] = 0
        flujo[v][u] = 0
        
    flujo_maximo = 0
    padres = {}
    
    while bfs_manual(capacidad, flujo, s, t, padres):
        path_flow = float('inf')
        nodo = t
        while nodo != s:
            u = padres[nodo]
            path_flow = min(path_flow, capacidad[u][nodo] - flujo[u][nodo])
            nodo = u
            
        nodo = t
        while nodo != s:
            u = padres[nodo]
            flujo[u][nodo] += path_flow
            flujo[nodo][u] -= path_flow
            nodo = u
            
        flujo_maximo += path_flow
        
    return flujo_maximo, flujo

def evaluar_flujo(mst, demandas_diarias):
    nodos = list(mst.nodes()) + ['SUPER_SUMIDERO']
    aristas = []
    
    for u, v, datos in mst.edges(data=True):
        cap = datos['capacidad_m3_dia']
        aristas.append((u, v, cap))
        aristas.append((v, u, cap))
        
    for barrio, demanda in demandas_diarias.items():
        if barrio != 'PLANTA':
            aristas.append((barrio, 'SUPER_SUMIDERO', demanda))
            
    flujo_manual, dict_flujos_manual = edmonds_karp_manual(nodos, aristas, 'PLANTA', 'SUPER_SUMIDERO')
    
    G_flujo = nx.DiGraph()
    for u, v, cap in aristas:
        G_flujo.add_edge(u, v, capacity=cap)
    flujo_nx, dict_flujos_nx = nx.maximum_flow(G_flujo, _s='PLANTA', _t='SUPER_SUMIDERO')
    
    print(f"[Validación Flujo] Manual: {flujo_manual:.2f} | NetworkX: {flujo_nx:.2f}")
    assert abs(flujo_manual - flujo_nx) < 0.1, "¡Diferencia en Edmonds-Karp!"
    
    return flujo_manual, dict_flujos_manual