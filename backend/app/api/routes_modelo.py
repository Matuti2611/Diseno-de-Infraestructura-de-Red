"""Endpoints para inspección, métricas y predicciones aisladas del modelo de ML."""

from __future__ import annotations

import os
from typing import Literal
import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.app.config import RUTA_MODELO, RUTA_METRICAS, DIAS_MES
from backend.app.ml.features import preparar_features_inferencia
from backend.app.ml.metricas import leer_metricas

router = APIRouter(prefix="/modelo", tags=["Machine Learning"])


class PrediccionNodoRequest(BaseModel):
    poblacion: float = Field(..., gt=0, description="Población proyectada")
    tipo_zona: Literal["residencial", "comercial", "industrial"] = Field(..., description="Tipo de zona: residencial, comercial o industrial")
    consumo_historico_mensual: float = Field(..., gt=0, description="Consumo mensual base en m³")
    crecimiento_poblacional_estimado: float = Field(default=0.02, description="Tasa anual estimada (ej. 0.02 para 2%)")
    latitud: float = Field(default=-32.95, description="Coordenada de latitud")
    longitud: float = Field(default=-60.65, description="Coordenada de longitud")
    fila: int = Field(default=0, description="Fila en la cuadrícula")
    columna: int = Field(default=0, description="Columna en la cuadrícula")


@router.get("/status")
def status_modelo():
    """Verifica si el archivo del modelo entrenado existe y es legible."""
    if os.path.exists(RUTA_MODELO):
        try:
            modelo = joblib.load(RUTA_MODELO)
            nombre_clase = modelo.__class__.__name__
            features = list(getattr(modelo, "feature_names_in_", []))
            return {
                "status": "online",
                "modelo": nombre_clase,
                "features_esperadas": features,
                "archivo": RUTA_MODELO
            }
        except Exception as e:
            return {"status": "error", "detalle": str(e)}
    return {"status": "offline", "message": "Archivo de modelo no encontrado."}


@router.get("/metricas")
def obtener_metricas():
    """Devuelve las métricas de evaluación del modelo sobre el conjunto de test."""
    return leer_metricas(RUTA_METRICAS)


@router.post("/predecir")
def predecir_nodo(datos: PrediccionNodoRequest):
    """
    Realiza una predicción aislada de demanda para una zona individual,
    transformando las features conforme al modelo entrenado.
    """
    if not os.path.exists(RUTA_MODELO):
        raise HTTPException(status_code=503, detail="Modelo no disponible en disco")
        
    try:
        modelo = joblib.load(RUTA_MODELO)
        columnas_esperadas = list(getattr(modelo, "feature_names_in_", []))
        
        df_fila = pd.DataFrame([{
            "poblacion": datos.poblacion,
            "tipo_zona": datos.tipo_zona,
            "consumo_historico_mensual": datos.consumo_historico_mensual,
            "crecimiento_poblacional_estimado": datos.crecimiento_poblacional_estimado,
            "latitud": datos.latitud,
            "longitud": datos.longitud,
            "fila": datos.fila,
            "columna": datos.columna
        }])
        
        X = preparar_features_inferencia(df_fila, columnas_esperadas)
        prediccion_mensual = float(modelo.predict(X)[0])
        demanda_diaria = prediccion_mensual / DIAS_MES
        
        return {
            "consumo_futuro_mensual_m3": round(prediccion_mensual, 2),
            "demanda_diaria_estimada_m3": round(demanda_diaria, 2),
            "unidad_mensual": "m³/mes",
            "unidad_diaria": "m³/día"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la predicción: {str(e)}")

