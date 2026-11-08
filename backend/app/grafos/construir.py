"""Construcción y formateo de estructuras de datos para algoritmos de grafos."""

from __future__ import annotations

from typing import Any
import pandas as pd


def preparar_aristas_kruskal(df_aristas: pd.DataFrame) -> list[tuple[float, str, str, float]]:
    """
    Convierte el DataFrame de aristas en una lista de tuplas (costo, origen, destino, capacidad)
    ordenada de forma ascendente por costo para el algoritmo de Kruskal.
    """
    aristas = []
    for _, fila in df_aristas.iterrows():
        aristas.append((
            float(fila["costo_unidades"]),
            str(fila["origen"]),
            str(fila["destino"]),
            float(fila["capacidad_m3_dia"])
        ))
    aristas.sort(key=lambda x: x[0])
    return aristas


def construir_red_flujo(
    mst_edges: list[tuple[str, str, dict[str, Any]]],
    demandas_diarias: dict[str, float],
    planta_id: str = "PLANTA",
    super_sumidero_id: str = "SUPER_SUMIDERO"
) -> tuple[list[str], list[tuple[str, str, float]]]:
    """
    Construye la red dirigida residual para Edmonds-Karp:
    - Arcos bidireccionales por cada cañería del MST.
    - Arcos dirigidos desde cada barrio hacia el super-sumidero con capacidad igual a su demanda.
    """
    nodos_set = set()
    for u, v, _ in mst_edges:
        nodos_set.add(u)
        nodos_set.add(v)
    nodos_set.add(super_sumidero_id)
    nodos = list(nodos_set)
    
    aristas_flujo: list[tuple[str, str, float]] = []
    
    # Cañerías del MST
    for u, v, datos in mst_edges:
        cap = float(datos["capacidad_m3_dia"])
        aristas_flujo.append((u, v, cap))
        aristas_flujo.append((v, u, cap))
        
    # Demandas hacia el super-sumidero
    for barrio, demanda in demandas_diarias.items():
        if barrio != planta_id and demanda > 0:
            aristas_flujo.append((barrio, super_sumidero_id, float(demanda)))
            
    return nodos, aristas_flujo


def construir_lista_adyacencia(df_aristas: pd.DataFrame) -> dict[str, list[dict[str, Any]]]:
    """
    Construye una representación de lista de adyacencia no dirigida del grafo completo.
    """
    grafo: dict[str, list[dict[str, Any]]] = {}
    for _, fila in df_aristas.iterrows():
        u = str(fila["origen"])
        v = str(fila["destino"])
        costo = float(fila["costo_unidades"])
        cap = float(fila["capacidad_m3_dia"])
        
        if u not in grafo:
            grafo[u] = []
        if v not in grafo:
            grafo[v] = []
            
        grafo[u].append({"destino": v, "costo": costo, "capacidad": cap})
        grafo[v].append({"destino": u, "costo": costo, "capacidad": cap})
        
    return grafo

