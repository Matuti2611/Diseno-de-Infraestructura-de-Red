# Contexto del proyecto para agentes de código

> Documento vivo: leer antes de trabajar y actualizar ante cambios importantes, antes de commits y push. Reglas en `../AGENTS.md`.

## Objetivo y responsabilidades

TP de una cooperativa de agua: dataset sintético, predicción de demanda a cinco años, Kruskal de costo mínimo, Edmonds–Karp de flujo máximo, API FastAPI y página React/TypeScript/Vite. Ciro trabaja en frontend; Matías en backend, ML y grafos. Contratos, integración e informe se coordinan entre ambos.

## Estado y alcance

Se están agrupando cambios autorizados en commits locales. El usuario realiza el push. Hay otros grupos preparados en la copia de trabajo: entorno reproducible, efectos frontend y documentación de cierre. Las correcciones backend y el entorno ya están registrados. Este grupo agrega los efectos frontend y sus pruebas. La revisión integral de documentación e informe queda para el último grupo.

No hacer push, publicar servicios ni ampliar el diseño sin la autorización correspondiente. La documentación no lleva fechas exactas ni hashes. Los errores y sus soluciones se documentan en la sección de IA del informe, sin atribución personal.

## Página

React/Vite con paleta elegida, Tendidos/Capacidad, escenarios, tabla, selección por teclado y validación de la API. Render ya entrega planta, candidatos, todos los caudales y balance. El navegador no calcula predicciones, MST ni flujo. El cliente admite métricas null; los efectos seleccionados por Ciro se registran en un grupo posterior.

## Datos

Generador reproducible, semilla 42: una planta, 16 zonas, 600 muestras y 26 candidatos. Datos sintéticos, consumo mensual y capacidad diaria. Modelo y CSV sin cambios; no se regeneran al iniciar la API.

## Machine learning

Se corrigió la inferencia categórica para que una zona tenga la misma predicción individualmente o dentro de un lote. El endpoint individual limita los tipos admitidos. La lectura de métricas es compartida y validada: archivo ausente o inválido devuelve null, sin constantes de respaldo. No se reentrenó el modelo.

Pendiente con Matías: separar selección y evaluación final, justificar features espaciales y analizar errores contra una referencia simple.

## Grafos

Kruskal y Edmonds–Karp manuales; NetworkX representa grafos y sirve de referencia de totales. Kruskal incorpora los nodos declarados y rechaza redes vacías o desconectadas. La prueba de costo conocido 6 llama a la función productiva en lugar de duplicar el algoritmo. El flujo máximo prioriza suministro total, sin garantizar reparto equitativo.

## API

API en `https://infraestructura-red-api.onrender.com`; el contrato completo se comprobó previamente. Las correcciones de este grupo están probadas localmente y todavía no se publicaron. Simulación y consulta MST devuelven 503 ante topología desconectada; tipo de zona no admitido produce 422; métricas pueden ser null.

El escenario multiplica la tasa anual de crecimiento poblacional; no incrementa directamente el consumo en ese porcentaje. El backend debe iniciarse desde la raíz por sus rutas relativas.

## Pruebas

22 pruebas backend aprobadas: inferencia estable por categorías, métricas inválidas/ausentes, error controlado de topología, MST de costo conocido e invariantes de flujo/pipeline. También se verificó HTTP local con métricas ausentes, 16 caudales y balance, predicción individual y rechazo de categoría inválida. No atribuir esos cambios locales a Render hasta publicarlos.

## Efectos frontend y verificación

Ciro eligió React Bits como fuente externa. HoloCard tiene una pestaña propia, carta Pikachu local, reflejos, inclinación y pausa. La vista se carga al abrirla. LatticeLoader aparece solo durante solicitudes reales, reinicia contador por escenario/intento y desaparece en éxito/error. No muestra progreso del algoritmo ni una conexión permanente.

Versiones TypeScript/CSS adaptadas como código local, sin Tailwind ni dependencias nuevas. TechText quedó sin aplicar porque transforma letras, no grafos. Otras mejoras visuales requieren consulta al usuario. Licencia en `../frontend/THIRD_PARTY_NOTICES.md`; decisiones y archivos en `efectos-visuales.md`.

37 pruebas frontend, lint, TypeScript y build aprobados. Las cuatro pruebas nuevas cubren contador, limpieza, retiro ante error/éxito, imagen sin WebGL y navegación sin nuevas simulaciones. Edge verificó reflejos, pausa, movimiento reducido, móvil de 390 px sin desbordamiento y regreso a Capacidad con 17 nodos/16 caudales de Render. Backend/modelo/datos no cambian por estos efectos.

## Entorno y despliegue

`.python-version` fija Python 3.12.10 y `backend/requirements.txt` fija dependencias directas/transitivas compatibles con scikit-learn 1.9.1, versión del modelo. En Render conservar raíz del repositorio, build `pip install -r backend/requirements.txt` y arranque `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`. Si existe PYTHON_VERSION, debe coincidir.

Frontend: engines Node 24.x, `.nvmrc` con 24.20.0 y lockfile sin actualización de paquetes. `frontend/vercel.json` configura Vite, instalación `npm ci`, build `npm run build` y salida dist. Importar con raíz frontend y `VITE_API_URL=https://infraestructura-red-api.onrender.com`. No se publicó el frontend.

Una copia separada con entornos nuevos pasó instalación, pip check, 22 tests backend, las 33 pruebas frontend anteriores a los efectos, lint y build con TypeScript. npm usó caché local. Falta probar otra computadora. No equivale a verificación en Linux.

## Próximo paso

Registrar el cierre documental ya autorizado: informe, contrato, revisión de consigna, guías, capturas y contexto completo. Después el usuario hará push. Repetir instalación en otra computadora, revisar Render y publicar frontend en Vercel cuando corresponda. La arquitectura elegida sigue siendo Vercel + Render.
