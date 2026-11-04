# Diseño de Infraestructura de Red

```text
diseno-de-infraestructura-de-red/
├── README.md                  
├── .gitignore
├── informe.pdf          
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
* **`informe.pdf`**: Documento final con la memoria, justificaciones y análisis del trabajo realizado.

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
  * **`generar_grafo.py`**: Crea las aristas candidatas entre zonas, asignando costos y capacidades de transmisión.
  * **`cargar.py`**: Funciones utilitarias para leer y cargar los archivos CSV utilizando Pandas.

* **`app/ml/`** (Machine Learning):
  * **`features.py`**: Lógica de preprocesamiento de datos (ej. codificación *one-hot* para tipos de zona).
  * **`entrenar.py`**: Script que divide el dataset, entrena y compara diferentes modelos predictivos, guardando el de mejor rendimiento.
  * **`evaluar.py`**: Calcula métricas de evaluación (MAE, RMSE, R²) y realiza análisis de errores.
  * **`predictor.py`**: Interfaz para cargar el modelo pre-entrenado y realizar inferencias sobre el consumo futuro.

* **`app/grafos/`** (Algoritmos de Redes):
  * **`construir.py`**: Instancia el grafo con NetworkX, integrando nodos (demandas) y aristas (costos/capacidades).
  * **`mst.py`**: Implementación propia del algoritmo de Kruskal o Prim para encontrar el diseño de red más económico.
  * **`union_find.py`**: Estructura de datos de conjuntos disjuntos, esencial si se utiliza el algoritmo de Kruskal.
  * **`flujo.py`**: Implementación del algoritmo de Edmonds-Karp para calcular el flujo máximo en la red.
  * **`diagnostico.py`**: Funciones para analizar qué aristas se encuentran saturadas o cerca de su límite operativo (ej. ≥90% de capacidad).

* **`app/servicios/`**:
  * **`pipeline.py`**: Orquestador principal. Conecta todo el flujo: toma el escenario → realiza la predicción de demanda → calcula el MST → evalúa el flujo de red → retorna el resultado integral.

* **Carpetas de apoyo del Backend**:
  * **`data/raw/`**: Carpeta donde se guardan los CSVs generados inicialmente (`zonas.csv`, `aristas_candidatas.csv`).
  * **`data/processed/`**: Carpeta para los datos limpios y procesados listos para el entrenamiento.
  * **`models/`**: Almacena el modelo de Machine Learning exportado (ej. `.joblib`) y sus métricas en formato `.json`.
  * **`notebooks/exploracion.ipynb`**: Cuaderno de Jupyter utilizado para el Análisis Exploratorio de Datos (EDA) y experimentación de modelos.
  * **`tests/`**: Pruebas unitarias y de integración (`test_mst.py`, `test_flujo.py` con casos de prueba conocidos, `test_pipeline.py`).

### 3. Frontend (React / Vite / TypeScript)
Interfaz de usuario para visualizar los grafos, interactuar con los escenarios de predicción y ver el diagnóstico de la red.

* **Archivos de Configuración**:
  * **`package.json`**: Gestor de dependencias de Node.js y scripts de ejecución.
  * **`tsconfig.json`**: Configuración del compilador de TypeScript.
  * **`vite.config.ts`**: Configuración del empaquetador Vite.

* **`src/`** (Código Fuente):
  * **`main.tsx` & `App.tsx`**: Punto de entrada de la aplicación React y componente raíz que orquesta las vistas.
  * **`api/cliente.ts`**: Lógica de conexión con el backend (funciones `fetch` o Axios para consumir la API de FastAPI).
  * **`types/red.ts`**: Definición de tipos o interfaces de TypeScript (Nodo, Arista, Diagnostico, Escenario) para asegurar el tipado estricto de los datos.

* **`src/components/`** (Componentes Reutilizables):
  * **`MapaRed.tsx`**: Componente visual (basado en SVG o alguna librería de mapas/grafos) que renderiza los nodos y las conexiones.
  * **`SelectorEscenario.tsx`**: Control de UI para cambiar las simulaciones de demanda (+0%, +10%, +30%, etc.).
  * **`PanelDiagnostico.tsx`**: Tarjeta de resumen con KPIs importantes (costo total, flujo actual, cantidad de aristas saturadas).
  * **`TablaAristas.tsx`**: Tabla de datos con el detalle minucioso del flujo y la capacidad por cada tramo de la red.
  * **`Leyenda.tsx`**: Explicación visual de los colores y formas utilizados en el mapa.

* **`src/views/`** (Vistas/Páginas Principales):
  * **`VistaTendidos.tsx`**: Pantalla enfocada en mostrar todas las conexiones candidatas y resaltar la red óptima calculada (MST).
  * **`VistaFlujo.tsx`**: Pantalla enfocada en el análisis operativo, mostrando el flujo por arista y destacando en rojo las líneas saturadas.

* **`src/styles/`**: Carpeta reservada para hojas de estilo (CSS, SCSS o módulos).
