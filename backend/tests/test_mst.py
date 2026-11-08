"""Tests unitarios para el algoritmo de árbol generador mínimo (Kruskal manual y Union-Find)."""

from __future__ import annotations

import unittest
import networkx as nx
import pandas as pd
from backend.app.config import RUTA_ARISTAS
from backend.app.grafos.union_find import UnionFind
from backend.app.grafos.mst import calcular_red_menor_costo


class UnionFindTest(unittest.TestCase):
    def test_operaciones_basicas_y_ciclos(self) -> None:
        elementos = ["A", "B", "C", "D"]
        uf = UnionFind(elementos)
        
        # Cada elemento comienza en su propio conjunto
        self.assertNotEqual(uf.find("A"), uf.find("B"))
        
        # Unir A y B
        unio_ab = uf.union("A", "B")
        self.assertTrue(unio_ab)
        self.assertEqual(uf.find("A"), uf.find("B"))
        
        # Unir B y C conecta transitivamente A y C
        unio_bc = uf.union("B", "C")
        self.assertTrue(unio_bc)
        self.assertEqual(uf.find("A"), uf.find("C"))
        
        # Intentar unir A y C debe detectar ciclo y retornar False
        unio_ac_ciclo = uf.union("A", "C")
        self.assertFalse(unio_ac_ciclo)
        
        # D sigue aislado
        self.assertNotEqual(uf.find("D"), uf.find("A"))


class KruskalMSTTest(unittest.TestCase):
    def test_caso_pequeno_controlado(self) -> None:
        """Prueba sobre un grafo de 4 nodos donde se conoce la arista óptima a descartar."""
        # Nodos A, B, C, D con ciclo A-B-C-D-A y diagonal A-C
        # Aristas:
        # A-B (costo 1)
        # B-C (costo 2)
        # C-D (costo 3)
        # D-A (costo 10) -> debe ser descartada por Kruskal
        # A-C (costo 4)  -> debe ser descartada por formar ciclo con A-B y B-C (1+2=3 < 4)
        aristas = [
            ("A", "B", 1.0, 100.0),
            ("B", "C", 2.0, 100.0),
            ("C", "D", 3.0, 100.0),
            ("A", "C", 4.0, 100.0),
            ("D", "A", 10.0, 100.0),
        ]
        nodos = {"A", "B", "C", "D"}
        uf = UnionFind(nodos)
        
        aristas_ordenadas = sorted(aristas, key=lambda x: x[2])
        mst_edges = []
        costo_total = 0.0
        
        for u, v, costo, cap in aristas_ordenadas:
            if uf.union(u, v):
                mst_edges.append((u, v))
                costo_total += costo
                
        # Deben seleccionarse 3 aristas (N - 1)
        self.assertEqual(len(mst_edges), 3)
        # Costo mínimo esperado: 1 + 2 + 3 = 6
        self.assertEqual(costo_total, 6.0)
        self.assertIn(("A", "B"), mst_edges)
        self.assertIn(("B", "C"), mst_edges)
        self.assertIn(("C", "D"), mst_edges)

    def test_kruskal_red_real_coincide_con_networkx(self) -> None:
        """Verifica invariantes del MST en el grafo de la cooperativa."""
        mst_manual, costo_manual = calcular_red_menor_costo(RUTA_ARISTAS)
        
        df_aristas = pd.read_csv(RUTA_ARISTAS)
        G_nx = nx.from_pandas_edgelist(
            df_aristas,
            source="origen",
            target="destino",
            edge_attr=["costo_unidades", "capacidad_m3_dia"]
        )
        mst_nx = nx.minimum_spanning_tree(G_nx, weight="costo_unidades")
        costo_nx = sum(d["costo_unidades"] for _, _, d in mst_nx.edges(data=True))
        
        # 1. El costo manual coincide exactamente con el de NetworkX
        self.assertAlmostEqual(costo_manual, costo_nx, places=2)
        
        # 2. Es conexo y abarca los 17 nodos (16 barrios + PLANTA)
        self.assertTrue(nx.is_connected(mst_manual))
        self.assertEqual(len(mst_manual.nodes()), 17)
        self.assertIn("PLANTA", mst_manual.nodes())
        
        # 3. No tiene ciclos (árbol con V vértices y V - 1 aristas)
        self.assertEqual(len(mst_manual.edges()), 16)
        self.assertTrue(nx.is_tree(mst_manual))
        
        # 4. Todos los costos y capacidades son positivos
        for _, _, datos in mst_manual.edges(data=True):
            self.assertGreater(datos["costo_unidades"], 0)
            self.assertGreater(datos["capacidad_m3_dia"], 0)


if __name__ == "__main__":
    unittest.main()

