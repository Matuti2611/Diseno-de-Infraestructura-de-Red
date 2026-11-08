"""Tests de integración para el pipeline de simulación y la API REST."""

from __future__ import annotations

import unittest
from pydantic import ValidationError
from fastapi import HTTPException
from backend.app.schemas import EscenarioRequest, SimulacionResponse
from backend.app.api.routes_flujo import simular_red
from backend.app.servicios.pipeline import ejecutar_simulacion


class PipelineSimulacionTest(unittest.TestCase):
    def test_pipeline_escenario_base(self) -> None:
        resultado = ejecutar_simulacion(1.0)
        
        # 1. Exactamente 17 nodos (16 barrios + PLANTA)
        self.assertEqual(len(resultado["nodos"]), 17)
        planta = next(n for n in resultado["nodos"] if n["id"] == "PLANTA")
        self.assertEqual(planta["demanda_diaria_proyectada"], 0.0)
        self.assertEqual(planta["tipo_zona"], "PLANTA")
        
        # 2. Exactamente 16 tendidos MST y 16 flujos reportados
        self.assertEqual(len(resultado["mst"].edges()), 16)
        self.assertEqual(len(resultado["flujos"]), 16)
        
        # 3. Exactamente 26 candidatos
        self.assertEqual(len(resultado["candidatos"]), 26)
        
        # 4. Invariante de balance: Demanda total = Abastecido + Déficit
        rc = resultado["resumen_capacidad"]
        demanda = rc["demanda_total_m3_dia"]
        abastecido = rc["caudal_abastecido_m3_dia"]
        deficit = rc["deficit_m3_dia"]
        
        self.assertGreater(demanda, 0.0)
        self.assertGreater(abastecido, 0.0)
        self.assertGreaterEqual(deficit, 0.0)
        self.assertAlmostEqual(demanda, abastecido + deficit, places=2)

    def test_crecimiento_demanda_monotono(self) -> None:
        """Al aumentar el factor de crecimiento poblacional, la demanda debe incrementarse."""
        res_10 = ejecutar_simulacion(1.0)
        res_11 = ejecutar_simulacion(1.1)
        res_13 = ejecutar_simulacion(1.3)
        
        dem_10 = res_10["resumen_capacidad"]["demanda_total_m3_dia"]
        dem_11 = res_11["resumen_capacidad"]["demanda_total_m3_dia"]
        dem_13 = res_13["resumen_capacidad"]["demanda_total_m3_dia"]
        
        self.assertLess(dem_10, dem_11)
        self.assertLess(dem_11, dem_13)


class ApiEndpointTest(unittest.TestCase):
    def test_endpoint_simular_red_valido(self) -> None:
        req = EscenarioRequest(escenario_crecimiento=1.1)
        respuesta = simular_red(req)
        
        self.assertIsInstance(respuesta, SimulacionResponse)
        
        # Verificar que la PLANTA está en nodos con demanda cero
        planta = next(n for n in respuesta.nodos if n.id == "PLANTA")
        self.assertEqual(planta.demanda_diaria_proyectada, 0.0)
        self.assertEqual(planta.tipo_zona, "PLANTA")
        
        # Verificar que tendidos_candidatos contiene 26 aristas
        self.assertIsNotNone(respuesta.tendidos_candidatos)
        self.assertEqual(len(respuesta.tendidos_candidatos), 26)
        
        # Verificar que flujos tiene 16 aristas con magnitudes y booleanos
        self.assertEqual(len(respuesta.flujos), 16)
        for f in respuesta.flujos:
            self.assertGreaterEqual(f.flujo_actual, 0.0)
            self.assertIsInstance(f.saturada, bool)
            
        # Verificar resumen de capacidad
        rc = respuesta.resumen_capacidad
        self.assertIsNotNone(rc)
        self.assertAlmostEqual(
            rc.demanda_total_m3_dia,
            rc.caudal_abastecido_m3_dia + rc.deficit_m3_dia,
            places=1
        )
        
        # Métricas de ML presentes y válidas
        metricas = respuesta.metricas_ml
        self.assertGreater(metricas.mae, 0)
        self.assertGreater(metricas.rmse, 0)
        self.assertGreater(metricas.r2, 0)

    def test_endpoint_rechaza_escenario_invalido(self) -> None:
        # Validación Pydantic (escenario <= 0)
        with self.assertRaises(ValidationError):
            EscenarioRequest(escenario_crecimiento=0.0)
            
        with self.assertRaises(ValidationError):
            EscenarioRequest(escenario_crecimiento=-1.0)


if __name__ == "__main__":
    unittest.main()
