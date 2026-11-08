"""Tests unitarios para los módulos auxiliares de datos, features, evaluación y topología."""

from __future__ import annotations

import unittest
import pandas as pd
from backend.app.data.cargar import (
    cargar_zonas, cargar_planta, cargar_aristas,
    cargar_todos_los_nodos, cargar_conexiones
)
from backend.app.ml.features import (
    preparar_features_entrenamiento,
    preparar_features_inferencia,
    calcular_consumo_per_capita
)
from backend.app.ml.evaluar import evaluar_modelo
from backend.app.grafos.construir import (
    preparar_aristas_kruskal,
    construir_lista_adyacencia,
    construir_red_flujo
)
from backend.app.api.routes_modelo import status_modelo, obtener_metricas, predecir_nodo, PrediccionNodoRequest
from backend.app.api.routes_red import obtener_nodos, obtener_conexiones, obtener_red_menor_costo


class CargaDatosTest(unittest.TestCase):
    def test_carga_correcta_archivos_base(self) -> None:
        zonas = cargar_zonas()
        planta = cargar_planta()
        aristas = cargar_aristas()
        
        self.assertEqual(len(zonas), 16)
        self.assertEqual(len(planta), 1)
        self.assertEqual(len(aristas), 26)
        
        nodos = cargar_todos_los_nodos()
        self.assertEqual(len(nodos), 17)
        self.assertEqual(nodos[0]["id"], "PLANTA")
        
        conexiones = cargar_conexiones()
        self.assertEqual(len(conexiones), 26)


class FeaturesYEvaluacionTest(unittest.TestCase):
    def test_preparar_features(self) -> None:
        df_dummy = pd.DataFrame([
            {
                "nodo_id": "Z01",
                "poblacion": 500,
                "tipo_zona": "residencial",
                "consumo_historico_mensual": 2000.0,
                "crecimiento_poblacional_estimado": 0.02,
                "consumo_futuro": 2200.0
            }
        ])
        X, y = preparar_features_entrenamiento(df_dummy)
        self.assertNotIn("nodo_id", X.columns)
        self.assertNotIn("consumo_futuro", X.columns)
        self.assertEqual(len(y), 1)
        
        per_capita = calcular_consumo_per_capita(df_dummy)
        self.assertAlmostEqual(per_capita.iloc[0], 4.0)

    def test_evaluar_modelo(self) -> None:
        y_true = [100.0, 200.0, 300.0]
        y_pred = [102.0, 198.0, 301.0]
        metricas = evaluar_modelo(y_true, y_pred)
        
        self.assertIn("mae", metricas)
        self.assertIn("rmse", metricas)
        self.assertIn("r2", metricas)
        self.assertGreater(metricas["r2"], 0.99)


class ConstruccionGrafosTest(unittest.TestCase):
    def test_preparar_kruskal_y_adyacencia(self) -> None:
        aristas = cargar_aristas()
        lista_kruskal = preparar_aristas_kruskal(aristas)
        
        self.assertEqual(len(lista_kruskal), 26)
        # Debe estar ordenada por costo ascendente
        costos = [a[0] for a in lista_kruskal]
        self.assertEqual(costos, sorted(costos))
        
        adyacencia = construir_lista_adyacencia(aristas)
        self.assertIn("PLANTA", adyacencia)
        # La planta conecta a 2 barrios candidatos
        self.assertEqual(len(adyacencia["PLANTA"]), 2)


class RutasAuxiliaresTest(unittest.TestCase):
    def test_endpoints_red_y_modelo(self) -> None:
        # Rutas de red
        res_nodos = obtener_nodos()
        self.assertEqual(res_nodos["total"], 17)
        
        res_conexiones = obtener_conexiones()
        self.assertEqual(res_conexiones["total"], 26)
        
        res_mst = obtener_red_menor_costo()
        self.assertEqual(res_mst["total_aristas"], 16)
        
        # Rutas de modelo
        res_status = status_modelo()
        self.assertEqual(res_status["status"], "online")
        
        res_metricas = obtener_metricas()
        self.assertIn("r2", res_metricas)
        
        req = PrediccionNodoRequest(
            poblacion=500.0,
            tipo_zona="residencial",
            consumo_historico_mensual=2250.0,
            crecimiento_poblacional_estimado=0.02
        )
        res_pred = predecir_nodo(req)
        self.assertGreater(res_pred["consumo_futuro_mensual_m3"], 0.0)
        self.assertGreater(res_pred["demanda_diaria_estimada_m3"], 0.0)


if __name__ == "__main__":
    unittest.main()

