# Instalación reproducible y prueba desde otra computadora

## Qué se busca comprobar

Que otra persona pueda instalar el código, levantar la API y usar la página siguiendo instrucciones, sin copiar entornos ni depender de archivos externos al repositorio. No requiere reentrenar ni regenerar datos: los CSV, el modelo y las métricas están versionados.

## Versiones y archivos

- Python **3.12.10**, registrado en `../.python-version`. `backend/requirements.txt` fija dependencias directas y transitivas del entorno probado; scikit-learn **1.9.1** coincide con el modelo guardado.
- Node **24.x**, probado con **24.20.0** y npm **11.19.0**. `frontend/.nvmrc` registra la versión local; `frontend/package.json` fija la versión mayor. `package-lock.json` fija las dependencias que instala `npm ci`.
- Git y acceso a los registros de paquetes para la primera instalación.

Los comandos siguientes son para PowerShell. En otros sistemas usar `.venv/bin/python` y `npm` en lugar de los ejecutables de Windows. La instalación en Linux no se comprobó en esta revisión.

## Preparar una copia nueva

Una vez que los cambios estén en GitHub, clonar el repositorio en una carpeta nueva y entrar a su raíz:

```powershell
git clone https://github.com/Matuti2611/Diseno-de-Infraestructura-de-Red.git
cd Diseno-de-Infraestructura-de-Red
python --version
node --version
npm.cmd --version
```

Comprobar las versiones antes de instalar. No copiar `.venv`, `node_modules`, `dist` ni archivos `.env.local` de otra instalación.

## API local

Desde la raíz del repositorio:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe -m unittest discover -s backend/tests -v
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Se esperan 22 pruebas aprobadas y ninguna incompatibilidad en `pip check`. Abrir `http://127.0.0.1:8000/docs`, buscar `POST /api/simular-red`, pulsar **Try it out**, enviar `{"escenario_crecimiento": 1.0}` y comprobar HTTP 200, 17 nodos, 16 caudales y resumen de capacidad. Mantener la terminal abierta. Las rutas actuales requieren iniciar Python desde la raíz.

## Página conectada a esa API

En otra terminal, desde la raíz:

```powershell
cd frontend
npm.cmd ci
Copy-Item .env.example .env.local
```

En esa copia nueva, editar `.env.local` para que tenga:

```dotenv
VITE_API_URL=http://127.0.0.1:8000
```

Luego ejecutar:

```powershell
npm.cmd test
npm.cmd run lint
npm.cmd run typecheck
npm.cmd run build
npm.cmd run dev
```

Se esperan 37 pruebas aprobadas y verificaciones sin errores. Abrir `http://127.0.0.1:5173` o la dirección que indique Vite. Comprobar:

- Tendidos muestra planta y barrios; se pueden seleccionar nodos y conexiones.
- Capacidad muestra caudales, demanda, suministro y déficit. Un caudal cero es un resultado válido.
- Base, +10 % y +30 % cambian demanda y balance; los porcentajes modifican la tasa anual poblacional. El MST puede conservarse por tener costos fijos.
- La tabla permite buscar y el gráfico se puede recorrer desde una pantalla estrecha.
- Si se detiene la API, una nueva solicitud muestra un error y permite reintentar; no aparecen resultados inventados.

Para usar Render en lugar de la API local, cambiar la variable a `https://infraestructura-red-api.onrender.com` y reiniciar Vite. El ensayo local comprueba el backend de esa copia; Render puede tener una versión distinta hasta publicar las correcciones.

## Estado y aceptación

Antes de incorporar los efectos visuales se creó una copia separada sin entornos instalados. Allí se instalaron requirements en una `.venv` nueva y el lockfile en `node_modules` nuevo. Pasaron `pip check`, las 22 pruebas backend, las 33 frontend de esa etapa, lint y build con TypeScript. Los efectos posteriores no agregaron paquetes y la suite actual tiene 37 pruebas aprobadas, más lint y build con TypeScript. El frontend se instaló con la caché local de npm; no se comprobó la primera descarga en otra computadora.

**Pendiente:** repetir la guía en la computadora de Matías u otra distinta, incluido el recorrido de navegador. Registrar en `context.md` sistema, versiones, comprobaciones y cualquier bloqueo, sin fechas exactas ni hashes. Si falla, registrar el mensaje real y la solución; no declarar la instalación completa hasta repetir lo que falló.

Al actualizar dependencias, revisar modelo y métricas junto con las versiones; no reemplazar requirements por paquetes de un Python global ajeno al proyecto. Para publicar después, seguir [despliegue.md](despliegue.md).
