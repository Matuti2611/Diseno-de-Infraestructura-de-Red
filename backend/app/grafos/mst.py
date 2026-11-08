import networkx as nx
import pandas as pd
from backend.app.grafos.union_find import UnionFind

def calcular_red_menor_costo(ruta_aristas_csv, nodos_esperados=None):
    df_aristas = pd.read_csv(ruta_aristas_csv)
    
    nodos = set(df_aristas['origen']).union(set(df_aristas['destino']))
    if nodos_esperados is not None:
        nodos.update(nodos_esperados)
    if not nodos:
        raise ValueError("No hay nodos para construir la red.")
    uf = UnionFind(nodos)
    
    aristas_ordenadas = df_aristas.sort_values('costo_unidades')
    
    # Vamos a guardar el resultado en un objeto de NetworkX SOLO para mantener 
    # la compatibilidad con el resto del pipeline, pero la lógica fue manual.
    mst_manual = nx.Graph()
    mst_manual.add_nodes_from(nodos)
    costo_manual = 0
    
    for _, fila in aristas_ordenadas.iterrows():
        u, v = fila['origen'], fila['destino']
        costo, cap = fila['costo_unidades'], fila['capacidad_m3_dia']
        
        if uf.union(u, v):
            mst_manual.add_edge(u, v, costo_unidades=costo, capacidad_m3_dia=cap)
            costo_manual += costo
            
    if len({uf.find(nodo) for nodo in nodos}) != 1:
        raise ValueError("La red candidata no permite conectar todos los nodos.")

    G_base = nx.from_pandas_edgelist(df_aristas, source='origen', target='destino', edge_attr=['costo_unidades', 'capacidad_m3_dia'])
    mst_nx = nx.minimum_spanning_tree(G_base, weight='costo_unidades')
    costo_nx = sum(datos['costo_unidades'] for _, _, datos in mst_nx.edges(data=True))
    
    print(f"[Validación Kruskal] Manual: {costo_manual:.2f} | NetworkX: {costo_nx:.2f}")
    assert abs(costo_manual - costo_nx) < 0.1, "¡Diferencia en Kruskal!"
    
    return mst_manual, costo_manual
