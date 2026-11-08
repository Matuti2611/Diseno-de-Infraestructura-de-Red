"""Módulo de I/O para carga y lectura de datos estructurados de la red y ML."""

from __future__ import annotations

import os
from typing import Any
import pandas as pd
from backend.app.config import (
    RUTA_ZONAS,
    RUTA_PLANTA,
    RUTA_ARISTAS,
    RUTA_HISTORIAL
)


def _verificar_archivo(ruta: str) -> None:
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo de datos en: {ruta}")


def cargar_zonas(ruta: str = RUTA_ZONAS) -> pd.DataFrame:
    """Carga el dataset de características base de los barrios."""
    _verificar_archivo(ruta)
    return pd.read_csv(ruta)


def cargar_planta(ruta: str = RUTA_PLANTA) -> pd.DataFrame:
    """Carga los datos y coordenadas de la planta potabilizadora."""
    _verificar_archivo(ruta)
    return pd.read_csv(ruta)


def cargar_aristas(ruta: str = RUTA_ARISTAS) -> pd.DataFrame:
    """Carga los enlaces candidatos entre nodos de la red."""
    _verificar_archivo(ruta)
    return pd.read_csv(ruta)


def cargar_historial(ruta: str = RUTA_HISTORIAL) -> pd.DataFrame:
    """Carga el historial de consumo para entrenamiento del modelo de ML."""
    _verificar_archivo(ruta)
    return pd.read_csv(ruta)


def cargar_todos_los_nodos(
    ruta_zonas: str = RUTA_ZONAS,
    ruta_planta: str = RUTA_PLANTA
) -> list[dict[str, Any]]:
    """
    Retorna la lista unificada de todos los nodos (PLANTA + 16 barrios)
    como diccionarios compatibles con los esquemas de la API.
    """
    df_planta = cargar_planta(ruta_planta)
    df_zonas = cargar_zonas(ruta_zonas)
    
    nodos: list[dict[str, Any]] = []
    
    # Planta
    fila_planta = df_planta.iloc[0]
    nodos.append({
        "id": str(fila_planta["nodo_id"]),
        "latitud": float(fila_planta["latitud"]),
        "longitud": float(fila_planta["longitud"]),
        "tipo_zona": "PLANTA",
        "demanda_diaria_proyectada": 0.0
    })
    
    # Barrios
    for _, fila in df_zonas.iterrows():
        nodos.append({
            "id": str(fila["nodo_id"]),
            "latitud": float(fila["latitud"]),
            "longitud": float(fila["longitud"]),
            "tipo_zona": str(fila["tipo_zona"]),
            "demanda_diaria_proyectada": 0.0
        })
        
    return nodos


def cargar_conexiones(ruta: str = RUTA_ARISTAS) -> list[dict[str, Any]]:
    """Carga los tendidos candidatos base formateados para la API."""
    df_aristas = cargar_aristas(ruta)
    return [
        {
            "origen": str(f["origen"]),
            "destino": str(f["destino"]),
            "costo": float(f["costo_unidades"]),
            "capacidad_maxima": float(f["capacidad_m3_dia"])
        }
        for _, f in df_aristas.iterrows()
    ]

