# Diseño de infraestructura de red de agua

Trabajo integrador de Machine Learning, grafos y desarrollo web. Un modelo predice consumo a cinco años; Kruskal conecta planta y barrios al menor costo y Edmonds–Karp comprueba si esa red abastece la demanda. Los datos son sintéticos y sus reglas están declaradas.

La aplicación tiene vistas de tendidos/capacidad, selector de crecimiento y de caso original/progresivo, suministro y déficit por barrio y comparación de escenarios. Los cálculos pertenecen al backend; el navegador valida y presenta resultados.

## Estado de la entrega

Implementación y demo local comprobadas. API existente: [documentación de Render](https://infraestructura-red-api.onrender.com/docs). No se confirmó que su despliegue tenga el último código; no confundir una prueba local con publicación. Frontend preparado para Vercel, publicación sin confirmar.

El código cumple las funcionalidades del TP elegido. El informe, capturas, historial incremental y guías están incluidos. Antes de entregar: revisar que GitHub contenga el código final y preparar la demo/defensa. El enunciado no exige hosting público, importación de CSV desde la web, otro dataset de evaluación ni elección automática entre modelos.

## Requisitos

- Python **3.12.10**, registrado en `.python-version`.
- Node **24.x**, probado con **24.20.0**; versión local en `frontend/.nvmrc`.
- Dependencias Python fijadas en `backend/requirements.txt`; paquetes frontend en `package-lock.json`.
- CSV y modelo ya versionados: no hay que regenerarlos ni reentrenar para iniciar.

## Levantar la demo local

En PowerShell, desde la raíz del repositorio:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Abrir `http://127.0.0.1:8000/docs`. Mantener esa terminal abierta. No hace falta activar la venv ni cambiar la política de scripts.

En otra terminal, desde la raíz:

```powershell
cd frontend
npm.cmd ci
$env:VITE_API_URL='http://127.0.0.1:8000'
npm.cmd run dev
```

Abrir la dirección indicada por Vite, normalmente `http://127.0.0.1:5173`. La variable afecta solo esa terminal. En otros sistemas usar `.venv/bin/python` y `npm`. Las rutas Python actuales requieren iniciar desde la raíz.

## Recorrido de prueba

1. Abrir Capacidad y elegir Progresivo.
2. Base y +10 % cubren la demanda; +30 % tiene suministro 2195 y déficit 47.09 m³/día con el modelo/CSV entregados.
3. Comparar escenarios: tres balances del mismo caso, sin cambiar el escenario principal.
4. Consultar demanda, suministro y déficit de cada barrio; el suministro no es el caudal de su cañería de entrada.
5. Volver a Original: conserva déficit en los tres escenarios. Ante un error se conserva el resultado anterior identificado y se permite reintentar.

Los porcentajes multiplican la tasa anual de crecimiento poblacional, no directamente la demanda. Con costos fijos el MST puede mantenerse. Máximo flujo no garantiza equidad ni una asignación única por barrio.

## Verificaciones

Desde la raíz:

```powershell
.venv\Scripts\python.exe -m unittest discover -s backend/tests -v
```

Dentro de `frontend/`:

```powershell
npm.cmd test
npm.cmd run lint
npm.cmd run typecheck
npm.cmd run build
```

La cobertura y los resultados actuales se detallan en [verificación del proyecto](docs/verificacion-proyecto.md). Las pruebas frontend no sustituyen la comprobación matemática del backend.

## Datos y entrenamiento

Para regenerar intencionalmente los datos originales:

```powershell
python backend/app/data/generar_dataset.py
python backend/app/data/generar_caso_progresivo.py
```

Esos comandos sobrescriben los CSV de salida. Para reentrenar intencionalmente:

```powershell
.venv\Scripts\python.exe -m backend.app.ml.entrenar
```

El entrenamiento compara lineal/árbol con y sin espaciales en CV, y exporta explícitamente la lineal sin espaciales, configuración elegida para este caso. No es una selección automática para cualquier dataset. Sobrescribe modelo/métricas; revisarlos juntos y reiniciar la API, que los carga al arrancar. No se entrena por petición.

## Organización y documentación

- `backend/app/data/`: generación reproducible y carga de CSV.
- `backend/app/ml/`: features, entrenamiento, evaluación, inferencia y lectura validada de métricas.
- `backend/app/grafos/`: Union-Find, Kruskal, Edmonds–Karp y diagnóstico.
- `backend/app/servicios/pipeline.py`: integración de predicciones, red y balances.
- `backend/app/api/`: rutas de simulación e inspección.
- `frontend/src/`: componentes/vistas, cliente HTTP, validación, presentación y pruebas. SVG y CSS propios; efectos React Bits como código local.
- [Informe](Informe.md): problema, dataset, ML, grafos, integración, resultados, IA y límites.
- [Contrato API](docs/contrato-api.md), [casos y barrios](docs/casos-capacidad.md).
- [Guía frontend](frontend/README.md), [instalación](docs/instalacion-reproducible.md), [despliegue](docs/despliegue.md).
- [Cumplimiento de consigna](docs/revision-consigna.md), [verificación](docs/verificacion-proyecto.md), [contexto vivo](docs/context.md), [plan frontend](docs/plan-frontend.md), [efectos](docs/efectos-visuales.md).
- [AGENTS.md](AGENTS.md): reglas de mantenimiento del proyecto.

El análisis reproducible está en los scripts y `backend/models/metricas.json`; el cuaderno reservado de `backend/notebooks/` está vacío y no se presenta como evidencia de análisis.
