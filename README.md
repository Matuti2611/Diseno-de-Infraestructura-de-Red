# Diseño de Infraestructura de Red

red-agua/
├── README.md                  # instalación y ejecución (entregable)
├── .gitignore
├── docs/
│   ├── informe.md             # borrador del informe, se va completando en paralelo
│   ├── uso_ia.md              # registrar prompts, errores de la IA, reflexiones desde el día 1
│   └── capturas/              # screenshots del frontend
│
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py            # crea la app FastAPI, CORS, registra routers
│   │   ├── config.py          # rutas a datos/modelos, semillas, constantes (horizonte 5 años, etc.)
│   │   ├── schemas.py         # modelos Pydantic de request/response
│   │   │
│   │   ├── api/
│   │   │   ├── routes_red.py        # GET grafo, GET MST
│   │   │   ├── routes_flujo.py      # POST diagnóstico de capacidad por escenario
│   │   │   └── routes_modelo.py     # GET métricas, POST predicción de una zona
│   │   │
│   │   ├── data/
│   │   │   ├── generar_dataset.py   # script generador sintético (reglas declaradas)
│   │   │   ├── generar_grafo.py     # aristas candidatas, costos y capacidades
│   │   │   └── cargar.py            # lectura de CSVs con pandas
│   │   │
│   │   ├── ml/
│   │   │   ├── features.py          # preprocesamiento (one-hot de tipo_zona, etc.)
│   │   │   ├── entrenar.py          # split train/test, entrena y compara modelos, guarda el mejor
│   │   │   ├── evaluar.py           # MAE, RMSE, R², análisis de errores
│   │   │   └── predictor.py         # carga el modelo y predice consumo_futuro
│   │   │
│   │   ├── grafos/
│   │   │   ├── construir.py         # arma el nx.Graph: nodos con demanda, aristas con costo/capacidad
│   │   │   ├── mst.py               # Kruskal o Prim (implementación propia)
│   │   │   ├── union_find.py        # si elegís Kruskal
│   │   │   ├── flujo.py             # Edmonds-Karp (implementación propia)
│   │   │   └── diagnostico.py       # aristas saturadas / cerca del límite (ej. ≥90%)
│   │   │
│   │   └── servicios/
│   │       └── pipeline.py          # une todo: escenario → predicción → demanda → MST → flujo → resultado
│   │
│   ├── data/
│   │   ├── raw/                     # CSV generado (zonas.csv, aristas_candidatas.csv)
│   │   └── processed/
│   ├── models/                      # modelo entrenado (.joblib) y métricas (.json)
│   ├── notebooks/
│   │   └── exploracion.ipynb        # EDA y comparación de modelos
│   └── tests/
│       ├── test_mst.py
│       ├── test_flujo.py            # casos chicos con resultado conocido
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
        │   └── cliente.ts           # funciones fetch al backend
        ├── types/
        │   └── red.ts               # tipos: Nodo, Arista, Diagnostico, Escenario
        ├── components/
        │   ├── MapaRed.tsx          # mapa/SVG con nodos y aristas
        │   ├── SelectorEscenario.tsx   # +0 %, +10 %, +30 %…
        │   ├── PanelDiagnostico.tsx    # resumen: costo total, flujo, nº de saturadas
        │   ├── TablaAristas.tsx        # detalle de flujo/capacidad por arista
        │   └── Leyenda.tsx
        ├── views/
        │   ├── VistaTendidos.tsx    # candidatas + MST resaltado
        │   └── VistaFlujo.tsx       # flujo por arista, saturadas en rojo
        └── styles/