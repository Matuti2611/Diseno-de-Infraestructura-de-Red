"""Recorrido ASGI real y resultados conocidos de los casos y consumo por barrio."""

import asyncio
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

from backend.app.main import app
from backend.app.servicios import pipeline
from backend.app.data.generar_caso_progresivo import generar


def solicitar(datos):
    async def ejecutar():
        mensajes = []
        cola = asyncio.Queue()
        await cola.put({'type': 'http.request', 'body': json.dumps(datos).encode(), 'more_body': False})
        async def recibir():
            return await cola.get()
        async def enviar(mensaje):
            mensajes.append(mensaje)
        await app({'type': 'http', 'asgi': {'version': '3.0'}, 'http_version': '1.1',
                   'method': 'POST', 'scheme': 'http', 'path': '/api/simular-red',
                   'raw_path': b'/api/simular-red', 'query_string': b'',
                   'headers': [(b'content-type', b'application/json')],
                   'server': ('test', 80), 'client': ('test', 123)}, recibir, enviar)
        estado = next(m['status'] for m in mensajes if m['type'] == 'http.response.start')
        cuerpo = b''.join(m.get('body', b'') for m in mensajes if m['type'] == 'http.response.body')
        return estado, json.loads(cuerpo)
    return asyncio.run(ejecutar())


class CasosYAbastecimientoTest(unittest.TestCase):
    def test_api_conserva_original_y_progresivo_cruza_el_limite_sin_mezclar_candidatos(self):
        resultados = {}
        for caso in ('original', 'progresivo'):
            for escenario in (1., 1.1, 1.3):
                with self.subTest(caso=caso, escenario=escenario):
                    estado, datos = solicitar({'caso_red': caso, 'escenario_crecimiento': escenario})
                    self.assertEqual(estado, 200)
                    self.assertEqual(datos['caso_red'], caso)
                    self.assertEqual(datos['escenario_crecimiento'], escenario)
                    barrios = [n for n in datos['nodos'] if n['id'] != 'PLANTA']
                    resumen = datos['resumen_capacidad']
                    for n in barrios:
                        self.assertGreaterEqual(n['caudal_abastecido_m3_dia'], 0)
                        self.assertGreaterEqual(n['deficit_m3_dia'], 0)
                        self.assertLessEqual(n['caudal_abastecido_m3_dia'], n['demanda_diaria_proyectada'])
                        self.assertAlmostEqual(n['demanda_diaria_proyectada'], n['caudal_abastecido_m3_dia'] + n['deficit_m3_dia'], places=2)
                    for campo, campo_nodo in (('demanda_total_m3_dia', 'demanda_diaria_proyectada'), ('caudal_abastecido_m3_dia', 'caudal_abastecido_m3_dia'), ('deficit_m3_dia', 'deficit_m3_dia')):
                        self.assertAlmostEqual(resumen[campo], sum(n[campo_nodo] for n in barrios), places=2)
                    candidatos = {frozenset((a['origen'], a['destino'])): a for a in datos['tendidos_candidatos']}
                    for a in datos['tendidos_mst']:
                        candidato = candidatos[frozenset((a['origen'], a['destino']))]
                        self.assertEqual(a['costo'], candidato['costo'])
                        self.assertEqual(a['capacidad_maxima'], candidato['capacidad_maxima'])
                    resultados[caso, escenario] = datos
        self.assertTrue(all(resultados['original', e]['resumen_capacidad']['deficit_m3_dia'] > 700 for e in (1., 1.1, 1.3)))
        self.assertEqual(resultados['progresivo', 1.]['resumen_capacidad']['deficit_m3_dia'], 0)
        self.assertEqual(resultados['progresivo', 1.1]['resumen_capacidad']['deficit_m3_dia'], 0)
        entrada = next(f for f in resultados['progresivo', 1.1]['flujos'] if {f['origen'], f['destino']} == {'PLANTA', 'Z01'})
        self.assertGreater(entrada['flujo_actual'] / entrada['capacidad_maxima'], .99)
        self.assertGreater(resultados['progresivo', 1.3]['resumen_capacidad']['deficit_m3_dia'], 40)
        origen = resultados['original', 1.]['tendidos_mst']
        nuevo = resultados['progresivo', 1.]['tendidos_mst']
        self.assertEqual({(frozenset((a['origen'], a['destino'])), a['costo']) for a in origen}, {(frozenset((a['origen'], a['destino'])), a['costo']) for a in nuevo})

    def test_abastecimiento_no_confunde_transito_con_consumo_y_acepta_deficit(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / 'aristas.csv'
            pd.DataFrame([('PLANTA', 'A', 1, 70), ('A', 'B', 2, 35)], columns=['origen', 'destino', 'costo_unidades', 'capacidad_m3_dia']).to_csv(ruta, index=False)
            zonas = pd.DataFrame([{'nodo_id': n, 'latitud': 0., 'longitud': i, 'tipo_zona': 'residencial'} for i, n in enumerate(('A', 'B'))])
            with patch.object(pipeline, 'RUTA_ARISTAS', str(ruta)), patch.object(pipeline, 'df_zonas_base', zonas), patch.object(pipeline, 'predecir_demanda', side_effect=lambda z, factor: np.array([600., 900.]) * factor):
                for factor, esperado in ((1., {'A': (20., 0.), 'B': (30., 0.)}), (1.3, {'A': (26., 0.), 'B': (35., 4.)})):
                    estado, datos = solicitar({'escenario_crecimiento': factor})
                    self.assertEqual(estado, 200)
                    for nodo in datos['nodos'][1:]:
                        self.assertEqual((nodo['caudal_abastecido_m3_dia'], nodo['deficit_m3_dia']), esperado[nodo['id']])
        self.assertEqual(solicitar({'caso_red': 'otro'})[0], 422)
        self.assertEqual(solicitar({'caso_red': '../../archivo'})[0], 422)

    def test_regla_del_caso_progresivo_reproduce_csv_y_preserva_original(self):
        entrada = Path('backend/data/raw/aristas_candidatas.csv')
        antes = entrada.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            salida = Path(tmp) / 'progresivo.csv'
            generar(entrada, salida)
            with salida.open(newline='', encoding='utf-8') as nuevo, Path('backend/data/raw/aristas_progresivas.csv').open(newline='', encoding='utf-8') as entregado:
                self.assertEqual(list(csv.DictReader(nuevo)), list(csv.DictReader(entregado)))
            with self.assertRaises(ValueError):
                generar(entrada, entrada)
        self.assertEqual(entrada.read_bytes(), antes)
