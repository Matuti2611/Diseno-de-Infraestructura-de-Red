"""Genera un caso de estudio reproducible para el trabajo de red de agua."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from random import Random

if __package__:
    from .generar_grafo import generar_aristas
else:
    from generar_grafo import generar_aristas


TIPOS_ZONA = ("residencial", "comercial", "industrial")
FACTOR_TIPO = {"residencial": 1.0, "comercial": 1.45, "industrial": 2.1}
ANIOS_PROYECCION = 5
CONSUMO_BASE_M3_PERSONA_DIA = 0.15
DIAS_POR_MES = 30
PLANTA = {"nodo_id": "PLANTA", "latitud": -32.9500, "longitud": -60.6500}
CAMPOS_ZONA = (
    "nodo_id",
    "latitud",
    "longitud",
    "fila",
    "columna",
    "poblacion",
    "tipo_zona",
    "consumo_historico_mensual",
    "crecimiento_poblacional_estimado",
)
CAMPOS_HISTORIAL = CAMPOS_ZONA + ("consumo_futuro",)
CAMPOS_ARISTA = ("origen", "destino", "distancia_m", "costo_unidades", "capacidad_m3_dia")
CAMPOS_PLANTA = ("nodo_id", "latitud", "longitud")


def crear_observacion(rng: Random, nodo_id: str, fila: int, columna: int) -> dict:
    poblacion = rng.randint(200, 1200)
    tipo = rng.choices(TIPOS_ZONA, weights=(0.65, 0.25, 0.10), k=1)[0]
    crecimiento = round(rng.uniform(0.005, 0.04), 4)
    consumo_base = poblacion * CONSUMO_BASE_M3_PERSONA_DIA * DIAS_POR_MES * FACTOR_TIPO[tipo]
    consumo_actual = max(1.0, consumo_base * rng.uniform(0.88, 1.12))
    return {
        "nodo_id": nodo_id,
        "latitud": round(PLANTA["latitud"] - 0.004 * (fila + 1), 6),
        "longitud": round(PLANTA["longitud"] + 0.005 * columna, 6),
        "fila": fila,
        "columna": columna,
        "poblacion": poblacion,
        "tipo_zona": tipo,
        "consumo_historico_mensual": round(consumo_actual, 2),
        "crecimiento_poblacional_estimado": crecimiento,
    }


def consumo_futuro(observacion: dict, rng: Random) -> float:
    """Etiqueta sintética: crecimiento compuesto a cinco años más ruido de medición."""
    actual = float(observacion["consumo_historico_mensual"])
    crecimiento = float(observacion["crecimiento_poblacional_estimado"])
    factor_ruido = rng.uniform(0.95, 1.05)
    return round(actual * (1 + crecimiento) ** ANIOS_PROYECCION * factor_ruido, 2)


def escribir_csv(ruta: Path, campos: tuple[str, ...], filas: list[dict]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)


def generar(salida: Path, semilla: int = 42, muestras: int = 600) -> dict[str, int]:
    if muestras < 100:
        raise ValueError("Se necesitan al menos 100 observaciones para evaluar el modelo")

    rng = Random(semilla)
    zonas = [
        crear_observacion(rng, f"Z{indice + 1:02d}", indice // 4, indice % 4)
        for indice in range(16)
    ]
    historial = []
    for indice in range(muestras):
        fila, columna = divmod(indice % 16, 4)
        observacion = crear_observacion(rng, f"H{indice + 1:04d}", fila, columna)
        historial.append({**observacion, "consumo_futuro": consumo_futuro(observacion, rng)})

    aristas = generar_aristas(zonas, PLANTA, rng)
    escribir_csv(salida / "planta.csv", CAMPOS_PLANTA, [PLANTA])
    escribir_csv(salida / "zonas.csv", CAMPOS_ZONA, zonas)
    escribir_csv(salida / "historial_consumo.csv", CAMPOS_HISTORIAL, historial)
    escribir_csv(salida / "aristas_candidatas.csv", CAMPOS_ARISTA, aristas)
    return {"zonas": len(zonas), "historial": len(historial), "aristas": len(aristas)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--semilla", type=int, default=42)
    parser.add_argument("--muestras", type=int, default=600)
    parser.add_argument(
        "--salida", type=Path, default=Path(__file__).resolve().parents[2] / "data" / "raw"
    )
    args = parser.parse_args()
    conteos = generar(args.salida, args.semilla, args.muestras)
    print(f"Datos generados en {args.salida.resolve()}: {conteos}")


if __name__ == "__main__":
    main()
