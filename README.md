# Diseño de Infraestructura de Red

## Contexto y planificación

- [Contexto actualizado del proyecto](docs/context.md): estado real de página, datos, ML, grafos, API y pruebas; debe revisarse y actualizarse ante cambios importantes, commits y push.
- [Plan de arquitectura del frontend](docs/plan-frontend.md): alcance aprobado, flujos, contrato, decisiones y estado de implementación.
- [Guía de la página](frontend/README.md): instalación, ejecución, estructura, pruebas y límites de la API.
- [Efectos visuales](docs/efectos-visuales.md): HoloCard con Pikachu, loader de solicitudes, adaptaciones y procedencia de React Bits.
- [Instalación reproducible](docs/instalacion-reproducible.md): versiones, instalación desde cero y comprobaciones para otra computadora.
- [Revisión de la consigna](docs/revision-consigna.md): requisitos del PDF, evidencia actual y pendientes de frontend, backend e informe.
- [Contrato de capacidad](docs/contrato-api.md): geometría, todos los flujos y balance; implementado por ambos lados y verificado en Render.
- [Casos y abastecimiento por barrio](docs/casos-capacidad.md): ampliación local con caso original/progresivo, regla reproducible, consumo por barrio y comparación de escenarios; pendiente de publicación.
- [Verificación técnica del proyecto](docs/verificacion-proyecto.md): estado, comprobaciones y próximos pasos. Los errores y su resolución se registran en la sección de IA del informe.
- [Guía de despliegue](docs/despliegue.md): Vercel para la página y Render para la API, configuración prevista y pasos pendientes antes de publicar.
- [Instrucciones para agentes de código](AGENTS.md): lectura del contexto, mantenimiento de documentación y criterios de trabajo y pruebas.

API desplegada en Render: [documentación interactiva](https://infraestructura-red-api.onrender.com/docs). Se verificaron 17 nodos, 26 candidatos, 16 flujos y balance completo en tres escenarios. La página muestra esos datos sin tramos Sin dato. Localmente se corrigieron y probaron los casos documentados en «Errores de la IA» del informe: 25 tests backend y 43 frontend aprobados. Esas correcciones siguen pendientes de publicación; faltan despliegue y cierre de entrega.

## Probar la página

Con Node 24.x (probado con 24.20.0, indicado en `frontend/.nvmrc`), desde la raíz:

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev
```

Abrir `http://127.0.0.1:5173`. Usa Render sin tener que ejecutar Python localmente. La primera respuesta puede demorarse después de inactividad. Para verificar: `npm.cmd test`, `npm.cmd run lint` y `npm.cmd run build` (incluye TypeScript). Las 43 pruebas del frontend no sustituyen los tests del backend. El gráfico y el panel muestran caudales y balance reales. La publicación prevista en Vercel sigue pendiente de autorización y verificación.

## Ejecutar el backend localmente

Con Python 3.12.10 (indicado en `.python-version`), desde la raíz del repositorio y en otra terminal:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe -m unittest discover -s backend/tests -v
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Abrir `http://127.0.0.1:8000/docs`. Para conectar la página a este backend, usar `VITE_API_URL=http://127.0.0.1:8000` en `frontend/.env.local` y reiniciar Vite. No hace falta activar el entorno virtual en PowerShell ni cambiar su política de scripts.

CSV y modelo ya están versionados: no hay que generarlos ni entrenar al arrancar. Para reentrenar intencionalmente, ejecutar desde la raíz `.venv\Scripts\python.exe -m backend.app.ml.entrenar`; sobrescribe el modelo y las métricas, por lo que deben revisarse juntos antes de publicar. Las rutas actuales requieren ejecutar el backend desde la raíz.

`backend/requirements.txt` fija dependencias directas y transitivas del entorno comprobado, incluido scikit-learn 1.9.1, compatible con el artefacto. Antes de incorporar los efectos, en una copia separada con `.venv` y `node_modules` nuevos pasaron instalación, `pip check`, 22 pruebas backend, las 33 frontend de esa etapa, lint y build con TypeScript. Los efectos no añaden paquetes y la suite actual tiene 43 pruebas frontend aprobadas. No equivale a probar otra computadora: ese ensayo sigue pendiente y tiene una [guía de comprobación](docs/instalacion-reproducible.md).

## Primer paso: generar los datos del caso sintético

Con Python 3.12, desde la raíz del repositorio:

```powershell
python backend/app/data/generar_dataset.py
```

El comando genera en `backend/data/raw/` cuatro CSV: `planta.csv`, `zonas.csv`, `historial_consumo.csv` y `aristas_candidatas.csv`. Usa una semilla fija (`42`) para que el resultado sea reproducible. Se pueden cambiar la semilla y el tamaño del historial con `--semilla` y `--muestras`. Las reglas y unidades están documentadas en [Informe.md](Informe.md).

Matías incorporó entrenamiento, modelo exportado, Kruskal y Edmonds–Karp manuales y el endpoint `POST /api/simular-red`. NetworkX representa los grafos y sirve de referencia para comprobar totales. La página usa la geometría completa y los 16 flujos de la API actual; conserva compatibilidad explícita con respuestas antiguas. El estado y las limitaciones están en [docs/context.md](docs/context.md).

Para comprobar la reproducibilidad y conectividad del grafo generado:

```powershell
python -m unittest discover -s backend/tests -p test_datos.py -v
```

```text
diseno-de-infraestructura-de-red/
├── README.md                  
├── .gitignore
├── Informe.md
│
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py            
│   │   ├── config.py          
│   │   ├── schemas.py         
│   │   ├── api/
│   │   │   ├── routes_red.py        
│   │   │   ├── routes_flujo.py      
│   │   │   └── routes_modelo.py     
│   │   ├── data/
│   │   │   ├── generar_dataset.py   
│   │   │   ├── generar_grafo.py     
│   │   │   └── cargar.py            
│   │   ├── ml/
│   │   │   ├── features.py          
│   │   │   ├── entrenar.py          
│   │   │   ├── evaluar.py           
│   │   │   └── predictor.py         
│   │   ├── grafos/
│   │   │   ├── construir.py         
│   │   │   ├── mst.py               
│   │   │   ├── union_find.py        
│   │   │   ├── flujo.py             
│   │   │   └── diagnostico.py       
│   │   └── servicios/
│   │       └── pipeline.py          
│   ├── data/
│   │   ├── raw/                     
│   │   └── processed/
│   ├── models/                      
│   ├── notebooks/
│   │   └── exploracion.ipynb        
│   └── tests/
│       ├── test_mst.py
│       ├── test_flujo.py            
│       └── test_pipeline.py
│
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api/
        │   └── cliente.ts           
        ├── types/
        │   └── red.ts               
        ├── components/
        │   ├── MapaRed.tsx          
        │   ├── SelectorEscenario.tsx
        │   ├── PanelDiagnostico.tsx 
        │   ├── TablaAristas.tsx     
        │   └── Leyenda.tsx
        ├── views/
        │   ├── VistaTendidos.tsx    
        │   └── VistaFlujo.tsx       
        └── styles/
```

---

## Detalle por Módulos

### 1. Raíz del Proyecto
Archivos generales de configuración y documentación de todo el repositorio.
* **`README.md`**: Contiene las instrucciones de instalación y ejecución del proyecto. Es el documento entregable principal de cara al usuario o evaluador.
* **`.gitignore`**: Define qué archivos o carpetas (como entornos virtuales o `node_modules`) deben ser ignorados por Git.
* **`Informe.md`**: Informe editable que se completa durante el proyecto con las decisiones, resultados, capturas y limitaciones.

### 2. Backend (Python / FastAPI)
Módulo encargado de la lógica de negocio, algoritmos de grafos, machine learning y provisión de datos mediante una API REST.

* **`requirements.txt`**: Lista de dependencias de Python necesarias para ejecutar el backend.
* **`app/`**: Contiene el código fuente principal de la aplicación.
  * **`main.py`**: Punto de entrada de la aplicación. Crea la instancia de FastAPI, configura los CORS y registra todos los routers (endpoints).
  * **`config.py`**: Archivo de configuraciones centralizadas (rutas a datos/modelos, semillas para aleatoriedad, constantes de negocio como el horizonte de 5 años, etc.).
  * **`schemas.py`**: Define los modelos de datos usando Pydantic para validar las peticiones (requests) y respuestas (responses) de la API.

* **`app/api/`** (Controladores de Rutas):
  * **`routes_red.py`**: Endpoints para obtener el grafo inicial y el Árbol de Expansión Mínima (MST).
  * **`routes_flujo.py`**: Endpoint POST para calcular el diagnóstico de capacidad y flujo de red según un escenario dado.
  * **`routes_modelo.py`**: Endpoints para obtener métricas del modelo de ML y predecir el consumo de una zona específica.

* **`app/data/`** (Manejo de Datos):
  * **`generar_dataset.py`**: Script para generar datos sintéticos basados en reglas de negocio predefinidas.
  * **`generar_grafo.py`**: Crea las aristas candidatas entre zonas, asignando costos y capacidades de transporte de agua.
  * **`cargar.py`**: Funciones utilitarias para leer y cargar los archivos CSV utilizando Pandas.

* **`app/ml/`** (Machine Learning):
  * **`features.py`**: Lógica de preprocesamiento de datos (ej. codificación *one-hot* para tipos de zona).
  * **`entrenar.py`**: Script que divide el dataset, entrena y compara diferentes modelos predictivos, guardando el de mejor rendimiento.
  * **`evaluar.py`**: Calcula métricas de evaluación (MAE, RMSE, R²) y realiza análisis de errores.
  * **`predictor.py`**: Interfaz para cargar el modelo pre-entrenado y realizar inferencias sobre el consumo futuro.

* **`app/grafos/`** (Algoritmos de Redes):
  * **`construir.py`**: Instancia el grafo con NetworkX, integrando nodos (demandas) y aristas (costos/capacidades).
  * **`mst.py`**: Kruskal manual con Union-Find; compara el costo con NetworkX y controla redes vacías, desconectadas o con nodos declarados aislados.
  * **`union_find.py`**: Estructura de datos de conjuntos disjuntos, esencial si se utiliza el algoritmo de Kruskal.
  * **`flujo.py`**: Edmonds–Karp manual con BFS y flujo residual; compara el total con NetworkX.
  * **`diagnostico.py`**: Funciones para analizar qué aristas se encuentran saturadas o cerca de su límite operativo (ej. ≥90% de capacidad).

* **`app/servicios/`**:
  * **`pipeline.py`**: Orquestador principal. Conecta todo el flujo: toma el escenario → realiza la predicción de demanda → calcula el MST → evalúa el flujo de red → retorna el resultado integral.

* **Carpetas de apoyo del Backend**:
  * **`data/raw/`**: Carpeta con los CSV sintéticos generados (`planta.csv`, `zonas.csv`, `historial_consumo.csv`, `aristas_candidatas.csv`).
  * **`data/processed/`**: Carpeta para los datos limpios y procesados listos para el entrenamiento.
  * **`models/`**: Almacena el modelo de Machine Learning exportado (ej. `.joblib`) y sus métricas en formato `.json`.
  * **`notebooks/exploracion.ipynb`**: Cuaderno de Jupyter utilizado para el Análisis Exploratorio de Datos (EDA) y experimentación de modelos.
  * **`tests/`**: 22 pruebas de datos, MST productivo, flujo, pipeline, auxiliares y regresiones de los casos corregidos durante el trabajo asistido por IA.

### 3. Frontend (React / Vite / TypeScript)
Interfaz de usuario para visualizar los grafos, interactuar con los escenarios de predicción y ver el diagnóstico de la red.

* **Archivos de Configuración**:
  * **`package.json`**: Gestor de dependencias de Node.js y scripts de ejecución.
  * **`tsconfig.json`**: Configuración del compilador de TypeScript.
  * **`vite.config.ts`**: Configuración del empaquetador Vite.

* **`src/`** (Código Fuente):
  * **`main.tsx` & `App.tsx`**: Punto de entrada de la aplicación React y componente raíz que orquesta las vistas.
  * **`api/cliente.ts` y `api/validar.ts`**: Conexión mediante `fetch`, cancelación y validación del JSON recibido.
  * **`lib/red.ts` y `data/casoRed.json`**: Adaptación para presentar resultados y geometría del caso CSV; no calculan predicciones, MST ni flujo.
  * **`types/red.ts`**: Definición de tipos o interfaces de TypeScript (Nodo, Arista, Diagnostico, Escenario) para asegurar el tipado estricto de los datos.

* **`src/components/`** (Componentes Reutilizables):
  * **`MapaRed.tsx`**: Gráfico SVG con selección de nodos y conexiones por mouse o teclado.
  * **`SelectorEscenario.tsx`**: Control de UI para cambiar las simulaciones de demanda (+0%, +10%, +30%, etc.).
  * **`PanelDiagnostico.tsx`**: Resumen de demanda proyectada, costo, barrios y tramos críticos informados.
  * **`TablaAristas.tsx`**: Tabla de datos con el detalle minucioso del flujo y la capacidad por cada tramo de la red.
  * **`Leyenda.tsx`**: Explicación visual de los colores y formas utilizados en el mapa.

* **`src/views/`** (Vistas/Páginas Principales):
  * **`VistaTendidos.tsx`**: Pantalla enfocada en mostrar todas las conexiones candidatas y resaltar la red óptima calculada (MST).
  * **`VistaFlujo.tsx`**: Pantalla enfocada en el análisis operativo, mostrando el flujo por arista y destacando en rojo las líneas saturadas.

* **`src/styles/global.css`**: Paleta, estados y diseño adaptable con CSS propio.
* **`src/tests/`**: Pruebas del contrato, cliente y comportamiento de la página. Los fixtures no son un modo demostración de producción.
