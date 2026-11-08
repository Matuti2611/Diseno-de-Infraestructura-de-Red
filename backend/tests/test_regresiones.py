"""Regresiones detectadas al revisar código y pruebas desarrollados con asistencia de IA."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from fastapi import HTTPException
from pydantic import ValidationError

from backend.app.api import routes_flujo, routes_modelo
from backend.app.data.cargar import cargar_zonas
from backend.app.ml.predictor import predecir_demanda
from backend.app.schemas import EscenarioRequest


class InferenciaEstableTest(unittest.TestCase):
    def test_prediccion_individual_y_lotes_por_tipo_coinciden_con_lote_completo(self):
        zonas = cargar_zonas()
        esperado = predecir_demanda(zonas, 1.0)
        for tipo in ("comercial", "industrial", "residencial"):
            indices = np.flatnonzero(zonas["tipo_zona"].to_numpy() == tipo)
            with self.subTest(tipo=tipo):
                lote_tipo = predecir_demanda(zonas.iloc[indices], 1.0)
                np.testing.assert_allclose(lote_tipo, esperado[indices], rtol=0, atol=1e-7)
                for indice in indices:
                    individual = predecir_demanda(zonas.iloc[[indice]], 1.0)[0]
                    self.assertAlmostEqual(individual, esperado[indice], places=7)

    def test_endpoint_individual_conserva_prediccion_de_cada_categoria(self):
        zonas = cargar_zonas()
        esperado = predecir_demanda(zonas, 1.0)
        for tipo in ("comercial", "industrial", "residencial"):
            indice = next(i for i, t in enumerate(zonas["tipo_zona"]) if t == tipo)
            with self.subTest(tipo=tipo):
                datos = zonas.iloc[indice].drop(labels=["nodo_id"]).to_dict()
                respuesta = routes_modelo.predecir_nodo(routes_modelo.PrediccionNodoRequest(**datos))
                self.assertAlmostEqual(respuesta["consumo_futuro_mensual_m3"], esperado[indice], delta=0.0051)

    def test_endpoint_rechaza_categoria_que_no_aprendio_el_modelo(self):
        with self.assertRaises(ValidationError):
            routes_modelo.PrediccionNodoRequest(
                poblacion=500, tipo_zona="desconocida", consumo_historico_mensual=2000
            )


class MetricasSinValoresInventadosTest(unittest.TestCase):
    def test_ausencia_o_archivo_invalido_no_impiden_simular_ni_inventan_metricas(self):
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "metricas.json"
            casos = [None, "{json roto", '{"mae": 12}', '{"mae": 12, "rmse": NaN, "r2": 0.9}']
            for contenido in casos:
                with self.subTest(contenido=contenido):
                    if contenido is not None:
                        ruta.write_text(contenido, encoding="utf-8")
                    with patch.object(routes_flujo, "RUTA_METRICAS", str(ruta)), patch.object(routes_modelo, "RUTA_METRICAS", str(ruta)):
                        self.assertIsNone(routes_flujo.cargar_metricas())
                        self.assertIsNone(routes_modelo.obtener_metricas())
                        respuesta = routes_flujo.simular_red(EscenarioRequest())
                        self.assertIsNone(respuesta.metricas_ml)
                        self.assertEqual(len(respuesta.flujos), 16)

    def test_las_dos_rutas_usan_el_archivo_disponible_incluso_con_r2_negativo(self):
        valores = {"mae": 12.5, "rmse": 14.75, "r2": -0.25}
        with tempfile.TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "metricas.json"
            ruta.write_text(json.dumps(valores), encoding="utf-8")
            with patch.object(routes_flujo, "RUTA_METRICAS", str(ruta)), patch.object(routes_modelo, "RUTA_METRICAS", str(ruta)):
                self.assertEqual(routes_flujo.cargar_metricas().model_dump(), valores)
                self.assertEqual(routes_modelo.obtener_metricas(), valores)


class ErrorTopologiaControladoTest(unittest.TestCase):
    def test_simulacion_informa_red_no_disponible_si_no_puede_conectarse(self):
        with patch.object(routes_flujo, "ejecutar_simulacion", side_effect=ValueError("Red desconectada")):
            with self.assertRaises(HTTPException) as error:
                routes_flujo.simular_red(EscenarioRequest())
        self.assertEqual(error.exception.status_code, 503)


if __name__ == "__main__":
    unittest.main()
