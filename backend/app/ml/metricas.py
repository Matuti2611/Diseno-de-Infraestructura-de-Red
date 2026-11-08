"""Lectura de evaluación persistida sin sustituir datos ausentes por cifras fijas."""

import json
from math import isfinite
from pathlib import Path


def leer_metricas(ruta: str) -> dict[str, float] | None:
    try:
        datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if not isinstance(datos, dict):
        return None
    campos = ("mae", "rmse", "r2")
    valores = {campo: datos.get(campo) for campo in campos}
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not isfinite(v) for v in valores.values()):
        return None
    if valores["mae"] < 0 or valores["rmse"] < 0 or valores["r2"] > 1:
        return None
    return {campo: float(valor) for campo, valor in valores.items()}
