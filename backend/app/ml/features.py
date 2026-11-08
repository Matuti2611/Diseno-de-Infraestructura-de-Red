"""Transformación y preparación de features para el modelo de consumo."""

from __future__ import annotations

import pandas as pd


def preparar_features_entrenamiento(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Separa variables predictoras y objetivo, y aplica one-hot encoding
    a las variables categóricas.
    """
    columnas_a_descartar = [c for c in ['nodo_id', 'consumo_futuro'] if c in df.columns]
    X = df.drop(columns=columnas_a_descartar)
    y = df['consumo_futuro'] if 'consumo_futuro' in df.columns else pd.Series(dtype=float)
    
    if 'tipo_zona' in X.columns:
        X = pd.get_dummies(X, columns=['tipo_zona'], drop_first=True)
        
    return X, y


def preparar_features_inferencia(
    df_zonas: pd.DataFrame,
    columnas_esperadas: list[str]
) -> pd.DataFrame:
    """
    Prepara las features para predicción asegurando que las columnas
    coincidan exactamente con las del modelo entrenado.
    """
    columnas_a_descartar = [c for c in ['nodo_id', 'consumo_futuro'] if c in df_zonas.columns]
    X = df_zonas.drop(columns=columnas_a_descartar)
    
    if 'tipo_zona' in X.columns:
        X = pd.get_dummies(X, columns=['tipo_zona'], drop_first=True)
        
    # Reindexar para asegurar orden y presencia de todas las dummies del entrenamiento
    X = X.reindex(columns=columnas_esperadas, fill_value=0)
    return X


def calcular_consumo_per_capita(df: pd.DataFrame) -> pd.Series:
    """Calcula el consumo mensual promedio por habitante si las columnas existen."""
    if 'consumo_historico_mensual' in df.columns and 'poblacion' in df.columns:
        return df['consumo_historico_mensual'] / df['poblacion']
    return pd.Series(0.0, index=df.index)

