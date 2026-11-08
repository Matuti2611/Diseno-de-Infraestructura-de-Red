"""Evaluación de métricas de rendimiento para los modelos de regresión."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def evaluar_modelo(y_true, y_pred) -> dict[str, float]:
    """
    Calcula las métricas de rendimiento del modelo de regresión:
    MAE, RMSE, MSE y R².
    """
    mae = float(mean_absolute_error(y_true, y_pred))
    mse = float(mean_squared_error(y_true, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_true, y_pred))
    
    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "mse": round(mse, 2),
        "r2": round(r2, 4)
    }


def imprimir_reporte_evaluacion(nombre_modelo: str, y_true, y_pred) -> None:
    """Imprime un resumen formateado por consola."""
    metricas = evaluar_modelo(y_true, y_pred)
    print(f"=== Reporte de Evaluación: {nombre_modelo} ===")
    print(f"MAE:  {metricas['mae']:.2f} m³/mes")
    print(f"RMSE: {metricas['rmse']:.2f} m³/mes")
    print(f"MSE:  {metricas['mse']:.2f}")
    print(f"R²:   {metricas['r2']:.4f}")
    print("==============================================")

