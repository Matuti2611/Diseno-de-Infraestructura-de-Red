"""Construye enlaces candidatos para un caso sintético de distribución de agua."""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt
from random import Random


def distancia_metros(a: dict, b: dict) -> float:
    """Distancia aproximada entre dos coordenadas para estimar longitud de tendido."""
    lat1, lon1 = radians(float(a["latitud"])), radians(float(a["longitud"]))
    lat2, lon2 = radians(float(b["latitud"])), radians(float(b["longitud"]))
    delta_lat, delta_lon = lat2 - lat1, lon2 - lon1
    h = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    return 2 * 6_371_000 * asin(sqrt(h))


def generar_aristas(zonas: list[dict], planta: dict, rng: Random) -> list[dict]:
    """Une vecinos de una cuadrícula 4x4 y conecta la planta a dos barrios."""
    if len(zonas) != 16:
        raise ValueError("Este escenario necesita exactamente 16 zonas")

    por_posicion = {(int(z["fila"]), int(z["columna"])): z for z in zonas}
    if len(por_posicion) != 16:
        raise ValueError("Las posiciones de las zonas deben ser únicas")

    pares = set()
    for fila in range(4):
        for columna in range(4):
            actual = por_posicion[(fila, columna)]["nodo_id"]
            for siguiente in ((fila + 1, columna), (fila, columna + 1)):
                if siguiente in por_posicion:
                    pares.add(tuple(sorted((actual, por_posicion[siguiente]["nodo_id"]))))

    # Dos alternativas de entrada desde la planta. El MST elegirá según el costo.
    for posicion in ((0, 0), (0, 1)):
        pares.add(tuple(sorted((planta["nodo_id"], por_posicion[posicion]["nodo_id"]))))

    nodos = {z["nodo_id"]: z for z in zonas}
    nodos[planta["nodo_id"]] = planta
    aristas = []
    for origen, destino in sorted(pares):
        distancia = distancia_metros(nodos[origen], nodos[destino])
        dificultad = rng.uniform(0.9, 1.25)
        aristas.append(
            {
                "origen": origen,
                "destino": destino,
                "distancia_m": round(distancia, 1),
                "costo_unidades": round(distancia * 10 * dificultad, 2),
                "capacidad_m3_dia": (
                    2500 if planta["nodo_id"] in (origen, destino) else rng.choice((750, 1200, 2000, 3000))
                ),
            }
        )
    return aristas
