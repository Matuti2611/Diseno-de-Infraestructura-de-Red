"""Deriva el caso didáctico sin alterar población, costos, geometría ni el CSV original."""

import argparse
import csv
from pathlib import Path


def generar(entrada: Path, salida: Path) -> None:
    if entrada.resolve() == salida.resolve():
        raise ValueError('El caso original no se debe sobrescribir.')
    with entrada.open(newline='', encoding='utf-8') as archivo:
        lector = csv.DictReader(archivo)
        campos = lector.fieldnames
        filas = list(lector)
    if not filas or not any({f['origen'], f['destino']} == {'PLANTA', 'Z01'} for f in filas):
        raise ValueError('El caso progresivo requiere el enlace PLANTA–Z01.')
    for fila in filas:
        fila['capacidad_m3_dia'] = '2195.0' if {fila['origen'], fila['destino']} == {'PLANTA', 'Z01'} else '2500.0'
    salida.parent.mkdir(parents=True, exist_ok=True)
    with salida.open('w', newline='', encoding='utf-8') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entrada', type=Path, default=Path('backend/data/raw/aristas_candidatas.csv'))
    parser.add_argument('--salida', type=Path, default=Path('backend/data/raw/aristas_progresivas.csv'))
    args = parser.parse_args()
    generar(args.entrada, args.salida)
