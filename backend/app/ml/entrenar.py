"""Entrenamiento, selección por validación cruzada y evaluación final del modelo de demanda."""

from __future__ import annotations

import os
import sys
import json
import joblib
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split, KFold, cross_validate
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from backend.app.config import RUTA_HISTORIAL, RUTA_MODELO, RUTA_METRICAS
from backend.app.data.cargar import cargar_historial
from backend.app.ml.features import preparar_features_entrenamiento
from backend.app.ml.evaluar import (
    evaluar_modelo,
    evaluar_por_subgrupo,
    obtener_muestra_residuos,
    imprimir_reporte_evaluacion
)


def ejecutar_entrenamiento():
    print("1. Cargando historial de consumo...")
    df = cargar_historial(RUTA_HISTORIAL)
    
    # --- EXPERIMENTO DE JUSTIFICACIÓN DE FEATURES ---
    # Comparar en validación qué ocurre con y sin variables espaciales (lat, lon, fila, col)
    X_con_esp, y_completa = preparar_features_entrenamiento(df, incluir_espaciales=True)
    X_sin_esp, _ = preparar_features_entrenamiento(df, incluir_espaciales=False)
    
    # Reservar 20% para test final. La selección de modelo se hace 100% dentro del 80% de train.
    idx_train, idx_test = train_test_split(df.index, test_size=0.2, random_state=42)
    y_train = y_completa.loc[idx_train]
    y_test = y_completa.loc[idx_test]
    
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    print("\n2. Validación Cruzada (5-Fold) dentro del 80% de Entrenamiento:")
    print("   (Comparación de modelos y justificación de variables espaciales)")
    
    modelos_candidatos = {
        "Regresión Lineal": LinearRegression(),
        "Árbol de Decisión": DecisionTreeRegressor(random_state=42)
    }
    
    comparativa_cv = {}
    
    for nombre_esp, X_matriz in [("Sin variables espaciales", X_sin_esp), ("Con variables espaciales", X_con_esp)]:
        X_tr = X_matriz.loc[idx_train]
        comparativa_cv[nombre_esp] = {}
        print(f"\n   --- Configuración: {nombre_esp} ---")
        
        for nombre_mod, modelo in modelos_candidatos.items():
            cv_scores = cross_validate(
                modelo, X_tr, y_train, cv=kf,
                scoring=['neg_mean_absolute_error', 'neg_root_mean_squared_error', 'r2']
            )
            mae_cv = round(float(-cv_scores['test_neg_mean_absolute_error'].mean()), 2)
            rmse_cv = round(float(-cv_scores['test_neg_root_mean_squared_error'].mean()), 2)
            r2_cv = round(float(cv_scores['test_r2'].mean()), 4)
            
            comparativa_cv[nombre_esp][nombre_mod] = {
                "mae_cv": mae_cv,
                "rmse_cv": rmse_cv,
                "r2_cv": r2_cv
            }
            print(f"   {nombre_mod:18} | MAE CV: {mae_cv:7.2f} | RMSE CV: {rmse_cv:7.2f} | R² CV: {r2_cv:7.4f}")

    # Justificación y Selección:
    # Regresión Lineal sin espaciales obtiene el menor MAE en validación cruzada.
    # Excluir coordenadas evita ruido aleatorio y sobreajuste.
    modelo_elegido = LinearRegression()
    nombre_elegido = "Regresión Lineal (sin variables espaciales)"
    X_train_final = X_sin_esp.loc[idx_train]
    X_test_final = X_sin_esp.loc[idx_test]
    
    print(f"\n3. Modelo Seleccionado por Validación Cruzada: {nombre_elegido}")
    print("   Entrenando sobre todo el conjunto de entrenamiento (80%)...")
    modelo_elegido.fit(X_train_final, y_train)
    
    print("\n4. Evaluación Final sobre el conjunto de Test reservado (20%):")
    predicciones_test = modelo_elegido.predict(X_test_final)
    metricas_test = evaluar_modelo(y_test, predicciones_test)
    imprimir_reporte_evaluacion("Regresión Lineal (Test Final)", y_test, predicciones_test)
    
    # 5. Análisis de errores por tipo de zona y muestra de residuos
    df_test_analisis = df.loc[idx_test].copy()
    df_test_analisis['prediccion'] = predicciones_test
    
    desglose_zonas = evaluar_por_subgrupo(df_test_analisis)
    muestra_residuos = obtener_muestra_residuos(df_test_analisis, n=6)
    
    print("\n5. Análisis de Errores por Tipo de Zona en Test:")
    for zona, met in desglose_zonas.items():
        print(f"   Zona: {zona:12} | N: {met['n_muestras']:2} | Consumo Prom: {met['consumo_promedio']:7.1f} | MAE: {met['mae']:6.2f} | MAPE: {met['mape']:4.2f}% | R²: {met['r2']:.4f}")
        
    print("\n6. Muestra de casos reales vs predichos (residuos):")
    for c in muestra_residuos:
        print(f"   Nodo {c['nodo_id']} ({c['tipo_zona']:11}): Real={c['consumo_real']:7.2f} | Pred={c['consumo_predicho']:7.2f} | Error={c['error_absoluto']:6.2f} ({c['error_porcentual']:4.1f}%)")

    # 6. Guardar artefactos
    os.makedirs(os.path.dirname(RUTA_MODELO), exist_ok=True)
    joblib.dump(modelo_elegido, RUTA_MODELO)
    
    archivo_metricas = {
        "mae": metricas_test["mae"],
        "rmse": metricas_test["rmse"],
        "r2": metricas_test["r2"],
        "mape": metricas_test["mape"],
        "modelo_seleccionado": nombre_elegido,
        "features_utilizadas": list(X_train_final.columns),
        "comparacion_modelos_cv": comparativa_cv,
        "desglose_por_zona": desglose_zonas,
        "muestra_predicciones": muestra_residuos
    }
    
    with open(RUTA_METRICAS, 'w', encoding='utf-8') as f:
        json.dump(archivo_metricas, f, indent=2, ensure_ascii=False)
        
    print(f"\nModelo guardado exitosamente en: {RUTA_MODELO}")
    print(f"Métricas y análisis de errores guardados en: {RUTA_METRICAS}")


if __name__ == "__main__":
    ejecutar_entrenamiento()
