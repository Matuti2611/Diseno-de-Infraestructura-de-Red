"""Evaluación de métricas de rendimiento y análisis de errores para modelos de regresión."""

from __future__ import annotations

from typing import Any
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def evaluar_modelo(y_true, y_pred) -> dict[str, float]:
    """
    Calcula las métricas globales de rendimiento del modelo de regresión:
    MAE, RMSE, MSE, R² y MAPE.
    """
    y_t = np.array(y_true, dtype=float)
    y_p = np.array(y_pred, dtype=float)
    
    mae = float(mean_absolute_error(y_t, y_p))
    mse = float(mean_squared_error(y_t, y_p))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_t, y_p))
    mape = float(np.mean(np.abs((y_t - y_p) / np.maximum(y_t, 1e-5))) * 100.0)
    
    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "mse": round(mse, 2),
        "r2": round(r2, 4),
        "mape": round(mape, 2)
    }


def evaluar_por_subgrupo(
    df_eval: pd.DataFrame,
    col_real: str = "consumo_futuro",
    col_pred: str = "prediccion",
    col_grupo: str = "tipo_zona"
) -> dict[str, dict[str, Any]]:
    """
    Desglosa el rendimiento del modelo por subgrupos (ej. residencial, comercial, industrial)
    para analizar dónde se concentran los mayores errores absolutos y relativos.
    """
    resultados: dict[str, dict[str, Any]] = {}
    for grupo, datos in df_eval.groupby(col_grupo):
        y_real = datos[col_real]
        y_est = datos[col_pred]
        metricas_g = evaluar_modelo(y_real, y_est)
        resultados[str(grupo)] = {
            "n_muestras": int(len(datos)),
            "consumo_promedio": round(float(y_real.mean()), 2),
            **metricas_g
        }
    return resultados


def obtener_muestra_residuos(
    df_eval: pd.DataFrame,
    n: int = 5,
    col_real: str = "consumo_futuro",
    col_pred: str = "prediccion"
) -> list[dict[str, Any]]:
    """Extrae los primeros n casos como ejemplos ilustrativos, no como muestra estadística."""
    muestra = df_eval.head(n)
    filas = []
    for _, fila in muestra.iterrows():
        real = float(fila[col_real])
        pred = float(fila[col_pred])
        error_abs = abs(real - pred)
        error_pct = (error_abs / max(real, 1e-5)) * 100.0
        filas.append({
            "nodo_id": str(fila.get("nodo_id", "")),
            "tipo_zona": str(fila.get("tipo_zona", "")),
            "consumo_real": round(real, 2),
            "consumo_predicho": round(pred, 2),
            "residuo": round(real - pred, 2),
            "error_absoluto": round(error_abs, 2),
            "error_porcentual": round(error_pct, 2)
        })
    return filas


def imprimir_reporte_evaluacion(nombre_modelo: str, y_true, y_pred) -> None:
    """Imprime un resumen formateado por consola."""
    m = evaluar_modelo(y_true, y_pred)
    print(f"=== Reporte de Evaluación: {nombre_modelo} ===")
    print(f"MAE:  {m['mae']:.2f} m³/mes")
    print(f"RMSE: {m['rmse']:.2f} m³/mes")
    print(f"MSE:  {m['mse']:.2f}")
    print(f"R²:   {m['r2']:.4f}")
    print(f"MAPE: {m['mape']:.2f} %")
    print("==============================================")
