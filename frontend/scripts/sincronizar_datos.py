"""Copia la geometría del CSV al frontend; no calcula predicciones ni algoritmos."""

import csv
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DATOS = RAIZ / "backend" / "data" / "raw"


def leer(nombre):
    with (DATOS / nombre).open(encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


def main():
    planta = leer("planta.csv")[0]
    zonas = leer("zonas.csv")
    aristas = leer("aristas_candidatas.csv")
    resultado = {
        "fuente": "backend/data/raw: planta.csv, zonas.csv y aristas_candidatas.csv",
        "planta": {
            "id": planta["nodo_id"],
            "latitud": float(planta["latitud"]),
            "longitud": float(planta["longitud"]),
        },
        "zonas": [
            {
                "id": zona["nodo_id"],
                "latitud": float(zona["latitud"]),
                "longitud": float(zona["longitud"]),
                "poblacion": int(zona["poblacion"]),
                "tipo_zona": zona["tipo_zona"],
            }
            for zona in zonas
        ],
        "aristas": [
            {
                "origen": arista["origen"],
                "destino": arista["destino"],
                "costo": float(arista["costo_unidades"]),
                "capacidad_maxima": float(arista["capacidad_m3_dia"]),
                "distancia_m": float(arista["distancia_m"]),
            }
            for arista in aristas
        ],
    }
    salida = RAIZ / "frontend" / "src" / "data" / "casoRed.json"
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Geometría sincronizada: {len(zonas)} barrios y {len(aristas)} conexiones")


if __name__ == "__main__":
    main()
