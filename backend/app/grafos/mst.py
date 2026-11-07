import networkx as nx
import pandas as pd

def calcular_red_menor_costo(ruta_aristas_csv):
    """
    Lee las aristas candidatas y calcula el MST usando Kruskal.
    Retorna el grafo resultante y el costo total.
    """
    df_aristas = pd.read_csv(ruta_aristas_csv)
    
    G_base = nx.from_pandas_edgelist(
        df_aristas, 
        source='origen', 
        target='destino', 
        edge_attr=['costo_unidades', 'capacidad_m3_dia']
    )
    
    mst = nx.minimum_spanning_tree(G_base, weight='costo_unidades')
    
    costo_total = sum(datos['costo_unidades'] for u, v, datos in mst.edges(data=True))
    
    return mst, costo_total

if __name__ == "__main__":
    ruta = 'backend/data/raw/aristas_candidatas.csv' 
    
    try:
        red_optima, costo = calcular_red_menor_costo(ruta)
        print("--- Resultado de Kruskal ---")
        print(f"Cantidad de conexiones seleccionadas: {red_optima.number_of_edges()}")
        print(f"Costo total de la obra: {costo:.2f}")
    except FileNotFoundError:
        print(f"No se encontró el archivo en {ruta}.")