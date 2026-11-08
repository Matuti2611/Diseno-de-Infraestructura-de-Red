"""Endpoints para consulta directa de topología de red y tendidos candidatos."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from backend.app.config import RUTA_ARISTAS
from backend.app.data.cargar import cargar_todos_los_nodos, cargar_conexiones
from backend.app.grafos.mst import calcular_red_menor_costo

router = APIRouter(prefix="/red", tags=["Topología de Red"])


@router.get("/nodos")
def obtener_nodos():
    """Devuelve la lista completa de nodos de la red (PLANTA y barrios)."""
    try:
        nodos = cargar_todos_los_nodos()
        return {"total": len(nodos), "nodos": nodos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar nodos: {str(e)}")


@router.get("/conexiones")
def obtener_conexiones():
    """Devuelve las 26 conexiones candidatas base para los tendidos."""
    try:
        conexiones = cargar_conexiones()
        return {"total": len(conexiones), "conexiones": conexiones}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al cargar conexiones: {str(e)}")


@router.get("/mst")
def obtener_red_menor_costo():
    """Devuelve la red de tendidos de menor costo calculada con Kruskal manual."""
    try:
        mst, costo_total = calcular_red_menor_costo(RUTA_ARISTAS)
        aristas = [
            {
                "origen": u,
                "destino": v,
                "costo": d["costo_unidades"],
                "capacidad": d["capacidad_m3_dia"]
            }
            for u, v, d in mst.edges(data=True)
        ]
        return {
            "algoritmo": "Kruskal (Manual con Union-Find)",
            "total_aristas": len(aristas),
            "costo_total": round(costo_total, 2),
            "aristas": aristas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular MST: {str(e)}")

