# Instalación reproducible

Objetivo: levantar backend y frontend desde una copia nueva, sin copiar entornos ni depender de archivos externos. CSV, modelo y métricas están versionados. No hace falta entrenar ni generar datos para iniciar.

## Requisitos

Python 3.12.10, Node 24.x (probado con 24.20.0/npm 11.19.0), Git y acceso a los registros de paquetes en la primera instalación. Requirements y lockfile fijan dependencias del entorno probado; scikit-learn 1.9.1 coincide con el modelo guardado.

Los comandos son para PowerShell. En otros sistemas usar .venv/bin/python y npm; esa instalación no se verificó en esta revisión.

## Copia nueva y API

```powershell
git clone https://github.com/Matuti2611/Diseno-de-Infraestructura-de-Red.git
cd Diseno-de-Infraestructura-de-Red
python --version
node --version
npm.cmd --version
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe -m unittest discover -s backend/tests -v
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Antes de clonar para evaluar, verificar que GitHub tenga los cambios finales. No copiar .venv, node_modules, dist ni .env.local de otra máquina. Ejecutar Python desde la raíz por las rutas actuales de datos/modelo.

Abrir `http://127.0.0.1:8000/docs`; ejecutar POST /api/simular-red con `{"caso_red":"progresivo","escenario_crecimiento":1.3}`. Se espera HTTP 200, confirmación del caso y crecimiento, 17 nodos, 16 caudales y resumen/balances por barrio. Mantener la API abierta.

## Página

En otra terminal, desde la raíz:

```powershell
cd frontend
npm.cmd ci
npm.cmd test
npm.cmd run lint
npm.cmd run typecheck
npm.cmd run build
$env:VITE_API_URL='http://127.0.0.1:8000'
npm.cmd run dev
```

Abrir la dirección indicada por Vite, normalmente `http://127.0.0.1:5173`. La variable solo afecta esa terminal; no sobrescribe archivos de entorno. Se puede usar .env.local en una instalación propia, conservándolo ignorado en Git.

Comprobar Original/Progresivo, Base/+10 %/+30 %, vistas Tendidos/Capacidad, suministro/déficit por barrio y comparación. En Progresivo los déficits esperados son 0/0/~47.09 m³/día con los archivos entregados. Detalle de pasos y prueba de error/reintento en [casos-capacidad.md](casos-capacidad.md).

Resultados actuales de la suite: [verificacion-proyecto.md](verificacion-proyecto.md). No declarar aprobada una comprobación que falla; registrar su mensaje real y volver a ejecutarla después de resolverla.

## Qué se verificó y qué no

Se comprobó una instalación limpia en copia separada con venv/node_modules nuevos y versiones fijadas. npm aprovechó la caché disponible. Las ampliaciones posteriores no añadieron dependencias; sus pruebas y build pasaron en el proyecto actual.

No se comprobó una primera descarga en otra computadora ni Linux. Repetir esta guía allí es una verificación recomendable, no un requisito adicional de dataset o proveedor de hosting en el enunciado. Las instrucciones reproducibles sí son un entregable.

Si se usa Render, configurar su URL sin /api al final y reiniciar Vite; la API pública puede tener otra versión y debe verificarse. No reemplazar fallos por datos de ejemplo. Actualizar dependencias junto con modelo/métricas; reentrenar sobrescribe artefactos y exige reiniciar la API.
