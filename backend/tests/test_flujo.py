"""Tests unitarios para el cálculo de flujo máximo (Edmonds-Karp manual) y balance de abastecimiento."""

from __future__ import annotations

import unittest
import networkx as nx
from backend.app.config import RUTA_ARISTAS
from backend.app.grafos.flujo import edmonds_karp_manual, evaluar_flujo
from backend.app.grafos.mst import calcular_red_menor_costo
from backend.app.grafos.diagnostico import obtener_estados_flujo


class FlujoEdmondsKarpTest(unittest.TestCase):
    def test_cancela_un_flujo_previo_para_alcanzar_el_maximo(self) -> None:
        # El primer BFS usa S-A-C-T. Para llegar a 2 hay que devolver C-A
        # y usar S-B-C-A-D-T; una implementación sin residuales se queda en 1.
        nodos = ['S', 'A', 'B', 'C', 'D', 'T']
        aristas = [('S', 'A', 1), ('S', 'B', 1), ('A', 'C', 1),
                   ('A', 'D', 1), ('B', 'C', 1), ('C', 'T', 1), ('D', 'T', 1)]
        total, flujo = edmonds_karp_manual(nodos, aristas, 'S', 'T')
        self.assertEqual(total, 2)
        self.assertEqual(flujo['A']['C'], 0)
        self.assertEqual(flujo['A']['D'], 1)
        self.assertEqual(flujo['B']['C'], 1)

    def test_caso_controlado_planta_a_b(self) -> None:
        """
        Caso de prueba exacto especificado en docs/contrato-api.md:
        Red en línea: PLANTA -> A (cap 70), A -> B (cap 35).
        """
        nodos = ["PLANTA", "A", "B", "SUPER_SUMIDERO"]
        
        # 1. Caso Cubierto:
        # Demandas: A=20, B=30 (Total=50)
        aristas_cubierto = [
            ("PLANTA", "A", 70.0),
            ("A", "PLANTA", 70.0),
            ("A", "B", 35.0),
            ("B", "A", 35.0),
            ("A", "SUPER_SUMIDERO", 20.0),
            ("B", "SUPER_SUMIDERO", 30.0),
        ]
        flujo_max, dict_flujos = edmonds_karp_manual(nodos, aristas_cubierto, "PLANTA", "SUPER_SUMIDERO")
        self.assertAlmostEqual(flujo_max, 50.0, places=2)
        # B recibe 30 a través de A
        flujo_ab = dict_flujos["A"]["B"]
        self.assertAlmostEqual(flujo_ab, 30.0, places=2)
        # PLANTA envía 50 hacia A
        flujo_pa = dict_flujos["PLANTA"]["A"]
        self.assertAlmostEqual(flujo_pa, 50.0, places=2)

        # 2. Caso Insuficiente (con Déficit):
        # Demandas: A=26, B=39 (Total=65)
        # Capacidad A-B es 35, por lo que B no puede recibir 39. B recibe 35 (satura A-B).
        # A recibe 26 directamente. Suministro total = 26 + 35 = 61. Déficit = 65 - 61 = 4.
        aristas_deficit = [
            ("PLANTA", "A", 70.0),
            ("A", "PLANTA", 70.0),
            ("A", "B", 35.0),
            ("B", "A", 35.0),
            ("A", "SUPER_SUMIDERO", 26.0),
            ("B", "SUPER_SUMIDERO", 39.0),
        ]
        flujo_max_def, dict_flujos_def = edmonds_karp_manual(nodos, aristas_deficit, "PLANTA", "SUPER_SUMIDERO")
        self.assertAlmostEqual(flujo_max_def, 61.0, places=2)
        self.assertAlmostEqual(dict_flujos_def["A"]["B"], 35.0, places=2)  # Satura el enlace A-B
        self.assertAlmostEqual(dict_flujos_def["PLANTA"]["A"], 61.0, places=2)

    def test_invariantes_flujo_red_completa(self) -> None:
        """Verifica conservación de caudal y respeto de capacidades sobre el MST real."""
        mst, _ = calcular_red_menor_costo(RUTA_ARISTAS)
        
        # Demandas sintéticas de prueba positivas para todos los barrios (excluyendo PLANTA)
        barrios = [n for n in mst.nodes() if n != "PLANTA"]
        demandas_prueba = {b: 100.0 for b in barrios}
        
        abastecido, dict_flujos = evaluar_flujo(mst, demandas_prueba)
        
        # 1. Coincidencia con NetworkX
        nodos_nx = list(mst.nodes()) + ["SUPER_SUMIDERO"]
        G_nx = nx.DiGraph()
        for u, v, d in mst.edges(data=True):
            cap = d["capacidad_m3_dia"]
            G_nx.add_edge(u, v, capacity=cap)
            G_nx.add_edge(v, u, capacity=cap)
        for b, dem in demandas_prueba.items():
            G_nx.add_edge(b, "SUPER_SUMIDERO", capacity=dem)
            
        flujo_nx, _ = nx.maximum_flow(G_nx, "PLANTA", "SUPER_SUMIDERO")
        self.assertAlmostEqual(abastecido, flujo_nx, places=2)
        
        # 2. Respeto de capacidades en todas las aristas
        estados = obtener_estados_flujo(mst, dict_flujos)
        self.assertEqual(len(estados), 16)
        for e in estados:
            self.assertGreaterEqual(e["flujo_actual"], 0.0)
            self.assertLessEqual(e["flujo_actual"], e["capacidad_maxima"] + 1e-4)

        # 3. Conservación de flujo en cada barrio intermedio:
        # Suma de flujos netos que entran al nodo = flujo entregado al SUPER_SUMIDERO
        for b in barrios:
            flujo_recibido_de_vecinos = 0.0
            for u in mst.neighbors(b):
                # Flujo neto que entra a b desde u
                f_ub = dict_flujos.get(u, {}).get(b, 0)
                flujo_recibido_de_vecinos += f_ub
                
            flujo_al_sumidero = dict_flujos.get(b, {}).get("SUPER_SUMIDERO", 0)
            self.assertAlmostEqual(flujo_recibido_de_vecinos, flujo_al_sumidero, places=2)


if __name__ == "__main__":
    unittest.main()

