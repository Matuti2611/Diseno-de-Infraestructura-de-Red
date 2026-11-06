"""Comprueba que el caso sintético sea reproducible y utilizable como grafo."""

from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.data.generar_dataset import generar


class GeneradorDatosTest(unittest.TestCase):
    def test_datos_reproducibles_y_grafo_conexo(self) -> None:
        with tempfile.TemporaryDirectory() as temporal:
            primera = Path(temporal) / "primera"
            segunda = Path(temporal) / "segunda"
            conteos = generar(primera)
            generar(segunda)

            self.assertEqual(conteos, {"zonas": 16, "historial": 600, "aristas": 26})
            for archivo in primera.iterdir():
                self.assertEqual(archivo.read_bytes(), (segunda / archivo.name).read_bytes())

            def leer(nombre: str) -> list[dict]:
                with (primera / nombre).open(newline="", encoding="utf-8") as archivo:
                    return list(csv.DictReader(archivo))

            zonas = leer("zonas.csv")
            historial = leer("historial_consumo.csv")
            aristas = leer("aristas_candidatas.csv")
            planta = leer("planta.csv")

            self.assertEqual(len(planta), 1)
            self.assertEqual(planta[0]["nodo_id"], "PLANTA")
            self.assertNotIn("consumo_futuro", zonas[0])
            self.assertIn("consumo_futuro", historial[0])

            vecinos: dict[str, set[str]] = defaultdict(set)
            for arista in aristas:
                a, b = arista["origen"], arista["destino"]
                self.assertGreater(float(arista["costo_unidades"]), 0)
                self.assertGreater(float(arista["capacidad_m3_dia"]), 0)
                vecinos[a].add(b)
                vecinos[b].add(a)

            visitados = {"PLANTA"}
            pendientes = ["PLANTA"]
            while pendientes:
                for vecino in vecinos[pendientes.pop()]:
                    if vecino not in visitados:
                        visitados.add(vecino)
                        pendientes.append(vecino)
            self.assertEqual(visitados, {"PLANTA", *(zona["nodo_id"] for zona in zonas)})


if __name__ == "__main__":
    unittest.main()
