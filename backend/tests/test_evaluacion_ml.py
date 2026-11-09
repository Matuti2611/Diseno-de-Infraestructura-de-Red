"""Valores resueltos a mano para las métricas y el reporte de errores existente."""

import unittest
import pandas as pd
from backend.app.ml.evaluar import evaluar_modelo, evaluar_por_subgrupo, obtener_muestra_residuos


class EvaluacionMLTest(unittest.TestCase):
    def test_metricas_coinciden_con_errores_conocidos(self):
        # Errores absolutos 10, 20, 30; SSE=1400, SST=20000 y MAPE=10 %.
        self.assertEqual(evaluar_modelo([100., 200., 300.], [110., 180., 330.]), {
            'mae': 20., 'rmse': 21.6, 'mse': 466.67, 'r2': .93, 'mape': 10.,
        })

    def test_subgrupos_y_residuos_conservan_escala_signo_y_muestras(self):
        datos = pd.DataFrame({
            'nodo_id': ['A', 'B', 'C', 'D'],
            'tipo_zona': ['residencial', 'residencial', 'industrial', 'industrial'],
            'consumo_futuro': [100., 200., 1000., 2000.],
            'prediccion': [110., 180., 900., 2200.],
        })
        antes = datos.copy(deep=True)
        grupos = evaluar_por_subgrupo(datos)
        self.assertEqual(grupos['residencial']['n_muestras'], 2)
        self.assertEqual(grupos['industrial']['n_muestras'], 2)
        self.assertEqual(grupos['residencial']['mae'], 15)
        self.assertEqual(grupos['industrial']['mae'], 150)
        self.assertEqual(grupos['residencial']['mape'], 10)
        self.assertEqual(grupos['industrial']['mape'], 10)
        casos = obtener_muestra_residuos(datos, n=3)
        self.assertEqual([c['nodo_id'] for c in casos], ['A', 'B', 'C'])
        self.assertEqual([c['residuo'] for c in casos], [-10, 20, 100])
        self.assertEqual([c['error_absoluto'] for c in casos], [10, 20, 100])
        self.assertEqual([c['error_porcentual'] for c in casos], [10, 10, 10])
        pd.testing.assert_frame_equal(datos, antes)
